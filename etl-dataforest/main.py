import json
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz
import psycopg2
from .verify_postgres_conection import is_postgis_enabled
from .create_table import create_table, create_index, create_jsonb_merge_function
from .send_shp_files_to_postgis import send_shp_files_to_postgis
from .verify_file_type import verify_file_type


# === Carrega variáveis de ambiente ===
load_dotenv()

EXTERNAL_DB_NAME = os.getenv("EXTERNAL_DB_NAME", "reflorestamento")
EXTERNAL_DB_USER = os.getenv("EXTERNAL_DB_USER", "dataforest")
EXTERNAL_DB_PASSWORD = os.getenv("EXTERNAL_DB_PASSWORD", "dataforest")
EXTERNAL_DB_HOST = os.getenv("EXTERNAL_DB_HOST", "localhost")
EXTERNAL_DB_PORT = os.getenv("EXTERNAL_DB_PORT", "5432")

ASC_TABLE_NAME = os.getenv("ASC_TABLE_NAME", "dados_geoespaciais")
ASC_SCHEMA = os.getenv("ASC_SCHEMA", "public")
SRID = os.getenv("ASC_SRID", 4326)

SHP_TABLE_NAME = os.getenv("SH_TABLE_NAME", "brasil")
SHP_FILE_PATH = os.getenv("SH_FILE", None)

ASC_SAMPLING_STRIDE = int(os.getenv("ASC_SAMPLING_STRIDE", 10))
BATCH_SIZE = int(os.getenv("ASC_BATCH_SIZE", 1000))

# === Conexão com PostGIS ===
CONN = psycopg2.connect(
    dbname= EXTERNAL_DB_NAME,
    user= EXTERNAL_DB_USER,
    password= EXTERNAL_DB_PASSWORD,
    host= EXTERNAL_DB_HOST,
    port= EXTERNAL_DB_PORT
)
CURSOR = CONN.cursor()

with open("etl-dataforest/input_data/asc_files.json", "r") as file:
    ASC_FILES = json.load(file)

def main():
    sao_paulo_tz = pytz.timezone("America/Sao_Paulo")
    execution_date = datetime.now(sao_paulo_tz).strftime("%Y-%m-%d")
    print(execution_date)

    # Verifica a conexão com o banco de dados
    is_postgis_enabled(CURSOR)

    # Cria a tabela para os arquivos ASC
    create_table(CONN, CURSOR, ASC_TABLE_NAME, ASC_SCHEMA, SRID)
    # Cria o índice para os arquivos ASC
    create_index(CONN, CURSOR, ASC_TABLE_NAME, ASC_SCHEMA)
    # Cria a função para mesclar JSONB
    create_jsonb_merge_function(CONN, CURSOR)

    # Cria a tabela para os arquivos SHP

    if SHP_FILE_PATH:
        # Envia o shapefile para o PostGIS
        send_shp_files_to_postgis(
            path=SHP_FILE_PATH,
            table_name=SHP_TABLE_NAME,
            db_host= EXTERNAL_DB_HOST,
            db_name= EXTERNAL_DB_NAME,
            db_port= EXTERNAL_DB_PORT,
            db_user= EXTERNAL_DB_USER,
            db_password= EXTERNAL_DB_PASSWORD,
            srid=SRID
        )
        print(f"Tabela {SHP_TABLE_NAME} para o arquivo shapefile criada com sucesso!")

    # Processa os arquivos ASC
    print("Iniciando processamento concorrente...")

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(
                verify_file_type,
                key,
                value,
                CONN,
                CURSOR,
                execution_date,
                ASC_TABLE_NAME,
                SHP_TABLE_NAME,
                ASC_SAMPLING_STRIDE,
                BATCH_SIZE,
                SRID
            ): key for key, value in ASC_FILES.items()
        }
        for future in futures:
            future.result()

    print("Processamento ASC concluído!")

    # Fecha a conexão com o banco de dados
    CURSOR.close()
    CONN.close()

if __name__ == "__main__":
    main()