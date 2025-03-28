from flask import Blueprint, request, jsonify
from .services import AscService
from .exceptions import ASCNotFoundError, ASCAlreadyExistsError, ASCProcessingError
from ..database import Session
import uuid

bp = Blueprint("asc", __name__, url_prefix="/asc")


def get_service(table_name: str):
    """Cria uma instância do serviço ASC para a tabela informada."""
    session = Session()
    return AscService(session, table_name)


@bp.route("/upload", methods=["POST"])
def upload_asc():
    """Recebe um arquivo ASC e processa os dados."""
    try:
        user_id = request.form.get("user_id")
        print("user_id", user_id)
        filename = request.form.get("filename")
        print("filename", filename)
        table_name = request.form.get("table_name")
        print("table_name", table_name)
        asc_file = request.files.get("asc_file")

        if not all([user_id, filename, table_name, asc_file]):
            return jsonify({"error": "user_id, filename, table_name e asc_file são obrigatórios."}), 400

        service = get_service(table_name)
        result = service.process_asc_file(user_id, filename, asc_file)

        return jsonify(result), 201

    except ASCProcessingError as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<string:table_name>/<string:asc_id>/", methods=["GET"])
def get_asc(table_name, asc_id):
    """Obtém um arquivo ASC pelo ID."""
    try:
        asc_uuid = uuid.UUID(asc_id)
        service = get_service(table_name)
        asc_entry = service.get_asc(asc_uuid)
        return jsonify(asc_entry), 200
    except ValueError:
        return jsonify({"error": "ID inválido"}), 400
    except ASCNotFoundError as e:
        return jsonify({"error": str(e)}), 404


@bp.route("/<string:table_name>/", methods=["GET"])
def list_asc(table_name):
    """Lista todos os arquivos ASC."""
    service = get_service(table_name)
    asc_entries = service.list_asc()
    return jsonify(asc_entries), 200


@bp.route("/<string:table_name>/<string:asc_id>/", methods=["DELETE"])
def delete_asc(table_name, asc_id):
    """Remove um arquivo ASC pelo ID."""
    try:
        asc_uuid = uuid.UUID(asc_id)
        service = get_service(table_name)
        service.delete_asc(asc_uuid)
        return jsonify({"message": "Arquivo ASC removido com sucesso."}), 200
    except ValueError:
        return jsonify({"error": "ID inválido"}), 400
    except ASCNotFoundError as e:
        return jsonify({"error": str(e)}), 404
