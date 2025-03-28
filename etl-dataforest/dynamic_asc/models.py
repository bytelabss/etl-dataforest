from sqlalchemy import Column, Integer, String
from geoalchemy2.types import Geometry
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def create_asc_table_class(table_name):
    """Cria uma classe de modelo dinâmica para o arquivo ASC."""
    class DynamicAscTable(Base):
        __tablename__ = table_name

        id = Column(Integer, primary_key=True, autoincrement=True)
        user_id = Column(Integer)
        filename = Column(String)
        geometry = Column(Geometry("POINT", srid=4326))
        srid = Column(Integer, nullable=True)
        rows = Column(Integer, nullable=True)
        cols = Column(Integer, nullable=True)
        xllcorner = Column(Integer, nullable=True)
        yllcorner = Column(Integer, nullable=True)
        cellsize = Column(Integer, nullable=True)
        nodata_value = Column(Integer, nullable=True)

        def __init__(self, user_id, filename, geometry, srid=None, rows=None, cols=None,
                     xllcorner=None, yllcorner=None, cellsize=None, nodata_value=None):
            self.user_id = user_id
            self.filename = filename
            self.geometry = geometry
            self.srid = srid
            self.rows = rows
            self.cols = cols
            self.xllcorner = xllcorner
            self.yllcorner = yllcorner
            self.cellsize = cellsize
            self.nodata_value = nodata_value

    return DynamicAscTable
