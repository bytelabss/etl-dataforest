import os
from .asc_functions import process_raster_in_chunks
from .shp_functions import process_shapefile

def verify_file_type(
        key, 
        value, 
        conn, 
        cursor, 
        execution_date, 
        table_name,
        shp_table,
        sampling_stride=10,
        batch_size=1000,
        srid=4326
    ):
    """
    Verifica o tipo de arquivo e processa conforme necessário.
    
    :param key: Nome do atributo.
    :param value: Dicionário com informações do arquivo.
    :param conn: Conexão com o banco de dados.
    :param cursor: Cursor do banco de dados.
    :param execution_date: Data de execução para o registro.
    :param table_name: Nome da tabela onde os dados serão inseridos.
    :param shp_table: Nome da tabela de polígonos para verificação espacial.
    :param sampling_stride: Passo de amostragem para os dados.
    :param batch_size: Tamanho do lote para inserção no banco de dados.
    :param srid: SRID do sistema de referência espacial (default é 4326).
    """

    ext = os.path.splitext(value['path'])[1].lower()

    if ext == '.asc':
        # Processa arquivo ASC
        process_raster_in_chunks(
            name=key,
            raster_path=value['path'],
            scale=value['escala'],
            measure=value['medida'],
            table_name=table_name,
            shp_table=shp_table,
            execution_date=execution_date,
            conn=conn,
            cursor=cursor,
        )

    elif ext == '.shp':
        # Processa arquivo SHP
        process_shapefile(
            conn=conn,
            cursor=cursor,
            table_name=shp_table,
            name=key,
            shp_path=value['path'],
            value=value['atributo'],
            refer_shapefile_table=shp_table,
            execution_date=execution_date,
            escala=value['escala'],
            medida=value['medida'],
            spacing_km=sampling_stride,
            srid=srid
        )
    else:
        raise ValueError(f"Tipo de arquivo não suportado: {ext}")
