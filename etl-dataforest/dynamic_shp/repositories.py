from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import json
import geopandas as gpd

class ShpFileRepository:
    """Repositório para manipular tabelas SHP dinâmicas."""

    def __init__(self, session: Session, shp_class):
        self.session = session
        self.shp_class = shp_class

    def create_table(self):
        """Cria a tabela no banco de dados."""
        try:
            self.shp_class.__table__.create(bind=self.session.bind)
        except SQLAlchemyError as e:
            print(f"Erro ao criar tabela: {e}")

    def insert(self, gdf: gpd.GeoDataFrame):
        """Insere um arquivo SHP no banco como geometria."""
        try:
            if self.get_line() is None:
                self.create_table()
            for _, row in gdf.iterrows():
                geometry_wkt = row["geometry"].wkt
                shp_entry = self.shp_class(
                    user_id=row["user_id"],
                    filename=row["filename"],
                    geometry=f"SRID=4326;{geometry_wkt}",
                    properties=json.dumps(row.drop("geometry").to_dict()),
                )
                self.session.add(shp_entry)
            self.session.commit()
            print(f"SHP inserido com sucesso: {gdf.shape[0]} registros.")
        except Exception as e:
            self.session.rollback()
            print(f"Erro ao inserir SHP: {e}: {row.to_dict()}")

    def get_by_id(self, shp_id):
        """Recupera um SHP pelo ID."""
        return self.session.query(self.shp_class).filter_by(id=shp_id).first()
    
    def get_line(self):
        """Recupera uma linha da tabela SHP."""
        try:
            data = self.session.query(self.shp_class).first()
            if not data:
                return []
            return data
        except SQLAlchemyError as e:
            print(f"Erro ao buscar linha: {e}")
            return None
