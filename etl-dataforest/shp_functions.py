import geopandas as gpd
import pandas as pd
import numpy as np
import os
import json
import psycopg2
from psycopg2.extras import execute_batch
from shapely.geometry import Point, Polygon, MultiPolygon
from .verify_point_locale import is_point_in_polygon



def process_shapefile(
        conn, 
        cursor,
        table_name,
        name, 
        shp_path, 
        value,
        refer_shapefile_table,
        execution_date,
        escala=1, 
        medida="", 
        spacing_km=10,
        srid=4326,
    ):
    """
    Processa um shapefile e insere os dados no PostGIS.

    :param conn: Conexão com o banco de dados PostGIS.
    :param cursor: Cursor do banco de dados.
    :param table_name: Nome da tabela onde os dados serão inseridos.
    :param name: Nome do shapefile.
    :param shp_path: Caminho para o shapefile.
    :param value: Atributo a ser processado.
    :param refer_shapefile_table: Nome da tabela com o polígono usado como referência.
    :param execution_date: Data de execução para o registro.
    :param escala: Fator de escala para o valor.
    :param medida: Unidade de medida.
    :param spacing_km: Espaçamento em km para amostragem.
    :param srid: SRID do sistema de referência espacial (default é 4326).
    """

    # Verifica se o arquivo existe
    if not os.path.exists(shp_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {shp_path}")
    
    # Verifica se a tabela existe
    cursor.execute(f"""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = '{table_name}'
        );
    """)
    table_exists = cursor.fetchone()[0]
    if not table_exists:
        raise ValueError(f"Tabela {table_name} não existe no banco de dados.")

    print(f"Processando shapefile: {name}")

    # Lè o shapefile
    gdf = gpd.read_file(shp_path)
    # Ajusta o CRS
    gdf = gdf.to_crs(epsg=srid)

    inserts = []

    for idx, row in gdf.iterrows():
        geom = row.geometry

        if geom.geom_type == "Point":
            points = [geom]
        elif isinstance(geom, Polygon):
            points = [coord for coord in geom.exterior.coords]
        elif isinstance(geom, MultiPolygon):
            points = []
            for poly in geom.geoms:
                points.extend(list(poly.exterior.coords))
        else:
            print(f"Geometria não suportada: {geom.geom_type}")
            continue

        for point in points:
            if isinstance(point, tuple):
                x, y = point
            else:
                x, y = point.x, point.y


            if not is_point_in_polygon(cursor, x, y, refer_shapefile_table, srid):
                continue

            valor = row[value]
            if pd.isna(valor):
                continue

            valor = valor * escala if isinstance(valor, (int, float, np.number)) else str(valor)
            doc_id = f"{x},{y}"
            new_data = {
                execution_date: {
                    name: {
                        "valor": valor,
                        "medida": medida
                    }
                }
            }

            inserts.append((doc_id, f"SRID=4326;POINT({x} {y})", json.dumps(new_data)))

    try:
        execute_batch(cursor, f"""
            INSERT INTO {table_name} (id, geom, raster)
            VALUES (%s, ST_GeomFromText(%s, 4326), %s)
            ON CONFLICT (id) DO UPDATE SET
            raster = jsonb_strip_nulls(
                jsonb_deep_merge({table_name}.raster, EXCLUDED.raster)
            );
        """, inserts)
        conn.commit()
        print(f"Finalizado processamento de {name} com múltiplos pontos.")
    except Exception as e:
        print(f"Erro ao inserir shapefile no PostGIS: {e}")
        conn.rollback()
