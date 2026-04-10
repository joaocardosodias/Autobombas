from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from backend.repositories import logging_repo

bp = Blueprint("logging", __name__, url_prefix="/logs")

@bp.route("", methods=["GET"])
def get_all_logs():
    """
    Retorna todas as informações de todas as tabelas do banco de dados.
    ---
    responses:
      200:
        description: Retorna um objeto JSON contendo todas as tabelas.
    """
    dados = logging_repo.buscar_todos_os_dados()
    return jsonify(dados), 200
