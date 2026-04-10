from flask import Blueprint, request, jsonify

from backend.repositories import usuario_repo
from backend.services import auth_service

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["POST"])
def login():
    """
    Autenticação de Usuário
    ---
    tags:
      - Auth
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - email
              - senha
            properties:
              email:
                type: string
                description: Email do usuário
              senha:
                type: string
                description: Senha do usuário
    responses:
      200:
        description: Login bem sucedido
        content:
          application/json:
            schema:
              type: object
              properties:
                token:
                  type: string
                usuario_id:
                  type: integer
                nome:
                  type: string
                role:
                  type: string
      400:
        description: Email e senha obrigatórios
      401:
        description: Credenciais inválidas
    """
    body = request.get_json()
    email = body.get("email")
    senha = body.get("senha")

    if not email or not senha:
        return jsonify({"detail": "Email e senha obrigatorios"}), 400

    usuario = usuario_repo.buscar_por_email(email)
    if not usuario:
        return jsonify({"detail": "Email nao encontrado"}), 401

    if not auth_service.verificar_senha(senha, usuario["senha_hash"]):
        return jsonify({"detail": "Senha incorreta"}), 401

    token = auth_service.criar_token(usuario["id"], usuario["role"])
    return jsonify({
        "token": token,
        "usuario_id": usuario["id"],
        "nome": usuario["name"],
        "role": usuario["role"],
    })
