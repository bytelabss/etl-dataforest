import os
import rasterio
import numpy as np
import json
from psycopg2.extras import execute_batch
from .verify_point_locale import is_point_in_polygon
from concurrent.futures import ThreadPoolExecutor


def read_raster_in_blocks(file_path):
    """
    Lê um arquivo raster em blocos.

    :param file_path: Caminho do arquivo raster.
    :return: Um gerador que produz blocos de dados do raster.
    """

    # Verifica se o arquivo existe
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    # Abre o arquivo raster e lê os dados em blocos
    with rasterio.open(file_path) as src:
        transform = src.transform
        for window in src.block_windows(1):
            window_data = src.read(1, window=window[1])
            yield window_data, transform, window[1]

def process_chunk(
        cursor,
        conn,
        table_name,
        values, 
        transform,
        window, 
        name, 
        scale,
        measure,
        execution_date,
        shp_table,
        sampling_stride = 10,
        batch_size=1000,
        srid=4326
):
    """
    Processa um bloco de dados raster e insere no banco de dados.

    :param cursor: Cursor do banco de dados.
    :param conn: Conexão com o banco de dados.
    :param table_name: Nome da tabela onde os dados serão inseridos.
    :param values: Dados do bloco raster.
    :param transform: Transformação do raster.
    :param window: Janela do raster.
    :param name: Nome do dado a ser inserido.
    :param scale: Fator de escala para o valor.
    :param measure: Unidade de medida do dado.
    :param execution_date: Data de execução para o registro.
    :param shp_table: Nome da tabela de polígonos para verificação espacial.
    :param sampling_stride: Passo de amostragem para os dados.
    :param batch_size: Tamanho do lote para inserção no banco de dados.
    :param srid: SRID do sistema de referência espacial (default é 4326).
    """

    # Inicializa variáveis
    rows, cols = values.shape
    inserts = []

    for i in range(0, rows, sampling_stride):
        for j in range(0, cols, sampling_stride):
            x, y = transform * (j + window.col_off, i + window.row_off)
            value = values[i, j]

            if np.isnan(value) or value == -9999:
                continue

            if not is_point_in_polygon(cursor, x, y, shp_table):
                continue

            value = value * scale
            doc_id = f"{x},{y}"
            new_data = {
                execution_date: {
                    name: {
                        "valor": float(value),
                        "medida": measure
                    }
                }
            }

            inserts.append((doc_id, f"SRID=4326;POINT({x} {y})", json.dumps(new_data)))

            if len(inserts) >= batch_size:
                try:
                    execute_batch(cursor, f"""
                        INSERT INTO {table_name} (id, geom, raster)
                        VALUES (%s, ST_GeomFromText(%s, {srid}), %s)
                        ON CONFLICT (id) DO UPDATE SET
                        raster = jsonb_strip_nulls(
                            jsonb_deep_merge({table_name}.raster, EXCLUDED.raster)
                        );
                    """, inserts)
                    conn.commit()
                    inserts.clear()
                except Exception as e:
                    print(f"Erro ao inserir no PostGIS: {e}")
                    conn.rollback()

    if inserts:
        try:
            execute_batch(cursor, f"""
                INSERT INTO {table_name} (id, geom, raster)
                VALUES (%s, ST_GeomFromText(%s, {srid}), %s)
                ON CONFLICT (id) DO UPDATE SET
                raster = jsonb_strip_nulls(
                    jsonb_deep_merge({table_name}.raster, EXCLUDED.raster)
                );
            """, inserts)
            conn.commit()
        except Exception as e:
            print(f"Erro ao inserir final no PostGIS: {e}")
            conn.rollback()

def process_raster_in_chunks(
        name,
        raster_path,
        scale,
        measure,
        table_name,
        shp_table,
        execution_date,
        conn,
        cursor,
        sampling_stride=10,
        batch_size=1000,
        srid=4326
    ):
    """
    Processa um arquivo raster em blocos e insere os dados no banco de dados.

    :param name: Nome do dado a ser inserido.
    :param raster_path: Caminho do arquivo raster.
    :param scale: Fator de escala para o valor.
    :param measure: Unidade de medida do dado.
    :param table_name: Nome da tabela onde os dados serão inseridos.
    :param shp_table: Nome da tabela de polígonos para verificação espacial.
    :param execution_date: Data de execução para o registro.
    :param conn: Conexão com o banco de dados.
    :param cursor: Cursor do banco de dados.
    :param sampling_stride: Passo de amostragem para os dados.
    :param batch_size: Tamanho do lote para inserção no banco de dados.
    :param srid: SRID do sistema de referência espacial (default é 4326).
    """

    print(f"Iniciando processamento de {name}...")



    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        for values, transform, window in read_raster_in_blocks(raster_path):
            future = executor.submit(
                process_chunk,
                cursor,
                conn,
                table_name,
                values,
                transform,
                window,
                name,
                scale,
                measure,
                execution_date,
                shp_table,
                sampling_stride,
                batch_size,
                srid
            )
            futures.append(future)

        for future in futures:
            future.result()

    print(f"Finalizado processamento de {name}.")
