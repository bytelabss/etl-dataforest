def is_point_in_polygon(cursor, x, y, table_name ,srid=4326):
    """
    Verifica se as coordenadas (x, y) estão dentro dos limites de outro polígono

    :param cursor: Cursor do banco de dados.
    :param x: Coordenada x (longitude).
    :param y: Coordenada y (latitude).
    :param table_name: Nome da tabela que contém o polígono.
    :param srid: SRID do sistema de referência espacial (default é 4326).
    """

    try:
        cursor.execute(f"""
            SELECT EXISTS (
                SELECT 1 FROM {table_name}
                WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint(%s, %s), %s))
            )
        """, (x, y, srid))
        result = cursor.fetchone()
        return result and result[0]
    except Exception as e:
        return False
