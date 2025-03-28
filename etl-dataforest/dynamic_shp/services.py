import os
os.environ["SHAPE_RESTORE_SHX"] = "YES"

import geopandas as gpd
from sqlalchemy.orm import Session
from shapely.geometry import mapping
import tempfile
import json
from .models import create_shp_table_class
from .repositories import ShpFileRepository

class ShpService:
    """Serviço para gerenciar arquivos SHP no banco de dados."""

    def __init__(self, session: Session, table_name: str):
        """Inicializa o serviço com uma sessão do banco e cria a tabela dinamicamente."""
        self.session = session
        self.table_name = table_name
        self.shp_model = create_shp_table_class(table_name)
        self.repository = ShpFileRepository(session, self.shp_model)

    def process_shp_file(self, user_id, filename, shp_file, batch_size=100):
        """Lê um arquivo SHP e armazena no banco PostGIS."""
        try:
            # Debugging file path
            print(f"Processing SHP file.")

            # Using a temporary file to handle the SHP file
            with tempfile.NamedTemporaryFile(suffix=".shp") as temp_file:
                temp_file.write(shp_file.read())
                temp_file.flush()
                gdf = gpd.read_file(temp_file.name)

            print(f"Read {gdf.shape[0]} rows from SHP file.")
            # Garantindo que tem CRS definido e transformando para WGS84
            if gdf.crs is None:
                gdf.set_crs(epsg=4326, inplace=True)
            else:
                gdf.to_crs(epsg=4326, inplace=True)

            print(type(user_id))

            batch = []
            for _, row in gdf.iterrows():
                batch.append({
                    "user_id": int(user_id),
                    "filename": filename,
                    "geometry": row["geometry"],
                    "properties": json.dumps(row.drop("geometry").to_dict()),  # Atributos extras
                })

                if len(batch) >= batch_size:
                    gdf = gpd.GeoDataFrame(batch, geometry="geometry", crs="EPSG:4326")
                    self.repository.insert(gdf)
                    batch.clear()

            if batch:    
                gdf = gpd.GeoDataFrame(batch, geometry="geometry", crs="EPSG:4326")
                self.repository.insert(gdf)

            return {"message": "Arquivo SHP armazenado com sucesso!", "table": self.table_name}
        except Exception as e:
            return {"error on service": str(e)}
