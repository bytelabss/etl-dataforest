import uuid
import rasterio
import geopandas as gpd
from sqlalchemy.orm import Session
from .models import create_asc_table_class
from .schemas import AscFileSchema
from .repositories import AscFileRepository
from shapely.geometry import Point


class AscService:
    """Serviço para gerenciar arquivos ASC no banco de dados."""

    def __init__(self, session: Session, table_name: str):
        """Inicializa o serviço com uma sessão do banco e cria a tabela dinamicamente."""
        self.session = session
        self.table_name = table_name
        self.asc_model = create_asc_table_class(table_name)  # Mantém dinamicidade
        self.repository = AscFileRepository(session, self.asc_model)

    def process_asc_file(self, user_id, filename, asc_file, batch_size=100):
        """Lê um arquivo ASC, converte para um GeoDataFrame e armazena no banco PostGIS em batches."""
        with rasterio.open(asc_file) as src:
            raster_data = src.read(1)  # Lê a primeira banda
            transform = src.transform
            crs = src.crs.to_epsg() if src.crs else 4326  # Define SRID (WGS84 por padrão)

            rows, cols = raster_data.shape
            nodata_value = src.nodata
            xllcorner, yllcorner = transform * (0, rows)  # Canto inferior esquerdo
            cellsize = transform.a  # Tamanho do pixel

            batch = []  
            for row in range(rows):
                for col in range(cols):
                    value = raster_data[row, col]
                    if value == nodata_value:
                        continue  
                    
                    x, y = transform * (col, row)
                    batch.append({
                        "user_id": user_id,
                        "filename": filename,
                        "rows": row,  # 🔹 Ajustado para "rows"
                        "cols": col,  # 🔹 Ajustado para "cols"
                        "xllcorner": xllcorner,  # 🔹 Adicionado
                        "yllcorner": yllcorner,  # 🔹 Adicionado
                        "cellsize": cellsize,  # 🔹 Adicionado
                        "nodata_value": nodata_value,  # 🔹 Adicionado
                        "value": value,
                        "geometry": Point(x, y),
                    })

                    if len(batch) >= batch_size:
                        gdf = gpd.GeoDataFrame(batch, geometry="geometry", crs=f"EPSG:{crs}")
                        self.repository.insert(gdf)
                        batch.clear()  

            if batch:
                gdf = gpd.GeoDataFrame(batch, geometry="geometry", crs=f"EPSG:{crs}")
                self.repository.insert(gdf)

        return {"message": "Arquivo ASC armazenado com sucesso!", "table": self.table_name}

    def get_asc(self, asc_id: uuid.UUID):
        """Busca um ASC pelo ID."""
        asc_entry = self.repository.get_by_id(asc_id)
        if not asc_entry:
            raise ValueError(f"Arquivo ASC com ID {asc_id} não encontrado.")
        return AscFileSchema().dump(asc_entry)

    def list_asc(self):
        """Lista todos os arquivos ASC."""
        asc_entries = self.repository.get_all()
        return AscFileSchema(many=True).dump(asc_entries)

    def delete_asc(self, asc_id: uuid.UUID):
        """Remove um ASC pelo ID."""
        return self.repository.delete(asc_id)
