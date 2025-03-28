import uuid
import geopandas as gpd
from shapely.geometry import mapping
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Type, Optional

class AscFileRepository:
    """Repositório para manipular tabelas ASC dinâmicas."""

    def __init__(self, session: Session, asc_class: Type):
        """
        Inicializa o repositório.

        :param session: Sessão do SQLAlchemy.
        :param asc_class: Classe do modelo ASC dinâmico.
        """
        self.session = session
        self.asc_class = asc_class

    def create_table(self):
        """Cria a tabela no banco de dados."""
        try:
            self.asc_class.__table__.create(bind=self.session.bind)
        except SQLAlchemyError as e:
            print(f"Erro ao criar tabela: {e}")

    def insert(self, gdf: gpd.GeoDataFrame) -> Optional[Type]:
        """
        Insere um novo arquivo ASC no banco como geometria.

        :param gdf: GeoDataFrame contendo os dados a serem inseridos.
        :return: Objeto criado ou None se falhar.
        """
        try:

            if self.get_line() is None:
                self.create_table()
            for _, row in gdf.iterrows():
                # Converte a geometria para WKT
                geometry_wkt = row["geometry"].wkt
                srid = 4326  # Substitua pelo SRID correto, se necessário

                asc_entry = self.asc_class(
                    user_id=row["user_id"],
                    filename=row["filename"],
                    geometry=f"SRID={srid};{geometry_wkt}",  # EWKT format
                    rows=row["rows"],
                    cols=row["cols"],
                    xllcorner=row["xllcorner"],
                    yllcorner=row["yllcorner"],
                    cellsize=row["cellsize"],
                    nodata_value=row["nodata_value"],
                )
                self.session.add(asc_entry)
            self.session.commit()
            print(f"ASC inserido com sucesso: {gdf.shape[0]} registros.")
        except Exception as e:
            self.session.rollback()
            print(f"Erro ao inserir ASC: {e}")

    def get_by_id(self, asc_id: uuid.UUID) -> Optional[Type]:
        """Recupera um ASC pelo ID."""
        return self.session.query(self.asc_class).filter_by(id=asc_id).first()

    def get_by_filename(self, filename: str) -> Optional[Type]:
        """Recupera um ASC pelo nome do arquivo."""
        return self.session.query(self.asc_class).filter_by(filename=filename).first()

    def list_all(self, limit: int = 100):
        """Retorna todos os registros da tabela ASC com limite."""
        return self.session.query(self.asc_class).limit(limit).all()

    def update(self, asc_id: uuid.UUID, **kwargs) -> Optional[Type]:
        """
        Atualiza um ASC pelo ID.

        :return: Objeto atualizado ou None se falhar.
        """
        try:
            asc_entry = self.session.query(self.asc_class).filter_by(id=asc_id).first()
            if not asc_entry:
                return None
            for key, value in kwargs.items():
                if hasattr(asc_entry, key):
                    setattr(asc_entry, key, value)
            self.session.commit()
            return asc_entry
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Erro ao atualizar ASC: {e}")
            return None

    def delete(self, asc_id: uuid.UUID) -> bool:
        """Remove um ASC pelo ID."""
        try:
            asc_entry = self.session.query(self.asc_class).filter_by(id=asc_id).first()
            if not asc_entry:
                return False
            self.session.delete(asc_entry)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Erro ao deletar ASC: {e}")
            return False
        
    def get_line(self):
        """Retorna uma linha da tabela ASC."""
        try:
            data = self.session.query(self.asc_class).first()
            if not data:
                return []
        except SQLAlchemyError as e:
            print(f"Erro ao buscar linha: {e}")
            return None
