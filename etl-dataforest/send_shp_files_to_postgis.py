import subprocess

def send_shp_files_to_postgis(path, table_name, db_host, db_name, db_port, db_user, db_password, srid=4326):
    """
    Envia arquivos shapefile para o banco de dados PostGIS.
    
    :param path: Caminho do arquivo shapefile.
    :param table_name: Nome da tabela onde os dados serão inseridos.
    :param db_host: Host do banco de dados.
    :param db_name: Nome do banco de dados.
    :param db_port: Porta do banco de dados.
    :param db_user: Usuário do banco de dados.
    :param db_password: Senha do banco de dados.
    :param srid: SRID do sistema de referência espacial (default é 4326).
    """
    # Comando para carregar o shapefile no banco de dados
    sh_command = (
        f"PGPASSWORD={db_password} "
        f"shp2pgsql -s {srid} -I {path} {db_name} > {table_name}.sql && "
        f"PGPASSWORD={db_password} "
        f"psql -U {db_user} -d {db_name} -h {db_host} -p {db_port} < {table_name}.sql && "
        f"PGPASSWORD={db_password} "
        f"psql -U {db_user} -d {db_name} -h {db_host} -p {db_port} -c \"CREATE INDEX IF NOT EXISTS idx_{db_name}_geom ON {db_name} USING GIST (geom);\""
        f" && "
        f"rm {table_name}.sql"
    )

    result = subprocess.run(sh_command, shell=True)
    if result.returncode != 0:
        print("❌ Erro ao carregar shapefile para o banco!")
    else:
        print("✅ Shapefile carregado com sucesso.")
