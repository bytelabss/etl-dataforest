import os
from flask import Blueprint, request, jsonify
from .services import ShpService
from ..database import Session

bp = Blueprint("shp", __name__, url_prefix="/shp")

def get_service(table_name: str):
    """Cria uma instância do serviço SHP para a tabela informada."""
    session = Session()
    return ShpService(session, table_name)

@bp.route("/upload", methods=["POST"])
def upload_shp():
    """Recebe um arquivo SHP e processa os dados."""
    try:
        user_id = request.form.get("user_id")
        filename = request.form.get("filename")
        table_name = request.form.get("table_name")
        shp_file = request.files.get("shp_file")

        if not all([user_id, filename, table_name, shp_file]):
            return jsonify({"error": "user_id, filename, table_name e shp_file são obrigatórios."}), 400

        service = get_service(table_name)

        result = service.process_shp_file(user_id, filename, shp_file)

        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error on route": str(e)}), 500
