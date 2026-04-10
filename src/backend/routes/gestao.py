from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from backend.repositories import gestao_repo

bp = Blueprint("gestao", __name__, url_prefix="/gestao")

@bp.route("/atividades", methods=["GET"])
@jwt_required()
def listar_atividades():
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)
    bomba_id = request.args.get("bomba_id", type=int)
    status = request.args.get("status", type=str)

    itens, total = gestao_repo.listar_atividades_consolidadas(
        page=page, 
        page_size=page_size, 
        bomba_id=bomba_id,
        status=status
    )
    
    total_pages = 1 if total == 0 else ((total + page_size - 1) // page_size)

    return jsonify({
        "items": itens,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    })

@bp.route("/atividades/<atividade_id>", methods=["GET"])
@jwt_required()
def buscar_atividade(atividade_id):
    atividade = gestao_repo.buscar_atividade_por_id(atividade_id)
    if not atividade:
        return jsonify({"detail": "Atividade nao encontrada"}), 404
        
    return jsonify(atividade)