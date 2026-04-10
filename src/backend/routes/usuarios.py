from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from pydantic import ValidationError

from backend.repositories import usuario_repo
from backend.services import auth_service
from backend.models.usuario import UsuarioCreate

bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

# Função auxiliar para checar se é gestor
def verificar_se_gestor():
    claims = get_jwt()
    if claims.get("role") != "gestor":
        return jsonify({"detail": "Acesso negado. Apenas gestores podem realizar esta ação."}), 403
    return None


@bp.route("", methods=["GET"])
@jwt_required()
def listar():
    # Verifica se quem está pedindo é gestor
    erro_permissao = verificar_se_gestor()
    if erro_permissao: return erro_permissao

    usuarios = usuario_repo.listar_todos()
    return jsonify(usuarios), 200


@bp.route("", methods=["POST"])
@jwt_required()
def criar():
    erro_permissao = verificar_se_gestor()
    if erro_permissao: return erro_permissao

    body = request.get_json()

    # 1. Valida o corpo da requisição com Pydantic
    try:
        dados = UsuarioCreate(**body)
    except ValidationError as e:
        # Se faltar campo ou e-mail for inválido, cai aqui
        return jsonify({"detail": str(e)}), 400

    # 2. Verifica se o e-mail já existe
    usuario_existente = usuario_repo.buscar_por_email(dados.email)
    if usuario_existente:
        return jsonify({"detail": "Já existe um usuário com este e-mail."}), 400

    # 3. Gera o hash da senha e salva no banco
    senha_hash = auth_service.gerar_hash_senha(dados.senha)
    novo_usuario = usuario_repo.criar(dados.nome, dados.email, senha_hash, dados.role)

    return jsonify(novo_usuario), 201


@bp.route("/<int:usuario_id>", methods=["DELETE"])
@jwt_required()
def deletar(usuario_id):
    erro_permissao = verificar_se_gestor()
    if erro_permissao: return erro_permissao

    sucesso = usuario_repo.deletar(usuario_id)
    if not sucesso:
        return jsonify({"detail": "Usuário não encontrado."}), 404

    return jsonify({"detail": "Usuário removido com sucesso."}), 200