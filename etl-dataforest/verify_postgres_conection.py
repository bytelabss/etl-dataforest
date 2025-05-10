
def is_postgis_enabled(cursor):
    """
    Verifica se a extensão PostGIS está habilitada no banco de dados.
    """
    print("Testando conexão com PostGIS...")
    try:
        cursor.execute("SELECT PostGIS_Version();")
        version = cursor.fetchone()
        print(f"Conexão bem-sucedida! PostGIS versão: {version[0]}")
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        exit(1)