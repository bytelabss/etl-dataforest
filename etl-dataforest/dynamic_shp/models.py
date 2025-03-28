from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def create_shp_table_class(table_name):
    """Cria uma classe de modelo dinâmica para arquivos SHP."""
    class DynamicShpTable(Base):
        __tablename__ = table_name

        id = Column(Integer, primary_key=True, autoincrement=True)
        user_id = Column(Integer)
        filename = Column(String)
        geometry = Column(Geometry("GEOMETRY", srid=4326))  # Aceita qualquer tipo geométrico
        properties = Column(String)  # JSON armazenando atributos extras

        def __init__(self, user_id, filename, geometry, properties=None):
            self.user_id = user_id
            self.filename = filename
            self.geometry = geometry
            self.properties = properties

    return DynamicShpTable
