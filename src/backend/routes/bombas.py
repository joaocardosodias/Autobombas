from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from backend.repositories import bomba_repo
from backend.models.bomba import BombaConfigUpdate

bp = Blueprint("bombas", __name__, url_prefix="/bombas")


@bp.route("", methods=["GET"])
@jwt_required()
def listar_bombas():
    """
    Listar todas as Motobombas
    ---
    tags:
      - Bombas
    responses:
      200:
        description: Lista de motobombas
    """
    return jsonify(bomba_repo.listar_todas())


@bp.route("/<int:bomba_id>", methods=["GET"])
@jwt_required()
def obter_bomba(bomba_id):
    """
    Obter Detalhes da Motobomba
    ---
    tags:
      - Bombas
    parameters:
      - name: bomba_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Detalhes da motobomba
      401:
        description: Não autorizado
      404:
        description: Bomba não encontrada
    """
    bomba = bomba_repo.buscar_por_id(bomba_id)
    if not bomba:
        return jsonify({"detail": "Bomba nao encontrada"}), 404
    return jsonify(bomba)


@bp.route("/<int:bomba_id>/config", methods=["PATCH"])
@jwt_required()
def atualizar_config(bomba_id):
    """
    Atualizar Configurações da Motobomba
    ---
    tags:
      - Bombas
    parameters:
      - name: bomba_id
        in: path
        type: integer
        required: true
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              diametro_carretel_cm:
                type: number
                description: Diâmetro do carretel em centímetros
              comprimento_corda_cm:
                type: number
                description: Comprimento máximo da corda em centímetros
              limite_inferior:
                type: number
                description: Corrente mínima de dragagem (abaixo disso = descer)
              limite_superior:
                type: number
                description: Corrente máxima de proteção (acima disso = subir)
              passo_auto_cm:
                type: number
                description: Passo de descida/subida no modo automático (cm)
    responses:
      200:
        description: Bomba atualizada com os novos valores
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                nome:
                  type: string
                diametro_carretel_cm:
                  type: number
                comprimento_corda_cm:
                  type: number
                limite_inferior:
                  type: number
                  nullable: true
                limite_superior:
                  type: number
                  nullable: true
                passo_auto_cm:
                  type: number
      400:
        description: Nenhum campo válido enviado
      401:
        description: Não autorizado
      404:
        description: Bomba não encontrada
    """
    bomba = bomba_repo.buscar_por_id(bomba_id)
    if not bomba:
        return jsonify({"detail": "Bomba não encontrada"}), 404

    body = request.get_json() or {}
    dados = BombaConfigUpdate(**body)

    # Valida banda: superior deve ser maior que inferior
    # Usa o valor do banco como fallback quando só um dos campos é enviado
    inf_novo = float(dados.limite_inferior) if dados.limite_inferior is not None else None
    sup_novo = float(dados.limite_superior) if dados.limite_superior is not None else None

    inf_final = inf_novo if inf_novo is not None else (float(bomba["limite_inferior"]) if bomba.get("limite_inferior") else None)
    sup_final = sup_novo if sup_novo is not None else (float(bomba["limite_superior"]) if bomba.get("limite_superior") else None)

    if inf_final is not None and sup_final is not None:
        if sup_final <= inf_final:
            return jsonify({
                "detail": f"limite_superior ({sup_final}) deve ser maior que limite_inferior ({inf_final})."
            }), 400

    resultado = bomba_repo.atualizar_config(bomba_id, dados)

    if resultado is None:
        return jsonify({"detail": "Nenhum campo válido enviado para atualização."}), 400

    return jsonify(resultado), 200
