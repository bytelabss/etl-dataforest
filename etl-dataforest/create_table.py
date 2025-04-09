

def create_table(conn, cursor, table_name, schema='public', srid=4326):
    """
    Cria uma tabela no banco de dados com o nome e esquema especificados.

    :param conn: Conexão com o banco de dados.
    :param cursor: Cursor do banco de dados.
    :param table_name: Nome da tabela a ser criada.
    :param schema: Esquema da tabela a ser criada.
    """

    creation_query = f"""
        CREATE SCHEMA IF NOT EXISTS {schema};
    
        CREATE EXTENSION IF NOT EXISTS postgis;

        CREATE TABLE IF NOT EXISTS {schema}.{table_name} (
            id TEXT PRIMARY KEY,
            geom GEOMETRY(Point, {srid}),
            raster JSONB
        );
    """

    try:
        cursor.execute(creation_query)
        conn.commit()
    except Exception as e:
        print(f"Erro ao criar tabela: {e}")
        conn.rollback()
        exit(1)

def create_index(conn, cursor, table_name, schema='public'):
    """
    Cria um índice na tabela especificada.

    :param conn: Conexão com o banco de dados.
    :param cursor: Cursor do banco de dados.
    :param table_name: Nome da tabela onde o índice será criado.
    :param schema: Esquema da tabela onde o índice será criado.
    """

    creation_query = f"""
        CREATE INDEX IF NOT EXISTS idx_geom ON {schema}.{table_name} USING GIST (geom);
    """

    try:
        cursor.execute(creation_query)
        conn.commit()
    except Exception as e:
        print(f"Erro ao criar índice: {e}")
        conn.rollback()
        exit(1)

def create_jsonb_merge_function(conn, cursor):
    """
    Cria uma função para mesclar dois objetos JSONB.

    :param conn: Conexão com o banco de dados.
    :param cursor: Cursor do banco de dados.
    """

    creation_query = """

        CREATE OR REPLACE FUNCTION jsonb_deep_merge(jsonb, jsonb)
        RETURNS jsonb LANGUAGE sql IMMUTABLE AS $$
        SELECT jsonb_object_agg(
            COALESCE(key1, key2),
            CASE
                WHEN value1 ISNULL THEN value2
                WHEN value2 ISNULL THEN value1
                WHEN jsonb_typeof(value1) = 'object' AND jsonb_typeof(value2) = 'object'
                    THEN jsonb_deep_merge(value1, value2)
                ELSE value2
            END
        )
        FROM
            jsonb_each($1) AS t1(key1, value1)
        FULL OUTER JOIN
            jsonb_each($2) AS t2(key2, value2)
            ON key1 = key2;
        $$;

    """
    try:
        cursor.execute(creation_query)
        conn.commit()
    except Exception as e:
        print(f"Erro ao criar tabela ou índice: {e}")
        conn.rollback()
        exit(1)
