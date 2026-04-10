from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.services import auto_mode_service

bp = Blueprint("auto_mode", __name__, url_prefix="/auto")


@bp.route("/<int:bomba_id>/ligar", methods=["POST"])
@jwt_required()
def ligar(bomba_id):
    """
    Ligar Modo Automático de Descida
    ---
    tags:
      - Modo Automático
    summary: Ativa o modo automático de descida/subida da bomba baseado na corrente
    parameters:
      - name: bomba_id
        in: path
        type: integer
        required: true
        description: ID da motobomba
    responses:
      200:
        description: Resultado da tentativa de ativação
        content:
          application/json:
            schema:
              type: object
              properties:
                ok:
                  type: boolean
                  description: true se ativado, false se bloqueado
                detail:
                  type: string
                  description: Motivo do bloqueio (quando ok=false)
                bloqueios:
                  type: array
                  items:
                    type: string
                  description: Lista de módulos offline (quando há bloqueio)
                posicao_inicial_cm:
                  type: number
                  description: Posição inicial recuperada do banco (quando ok=true)
                limite_corrente:
                  type: number
                  description: Limite de corrente configurado para a bomba (A)
                passo_cm:
                  type: number
                  description: Incremento de descida/subida por ciclo (cm)
      401:
        description: Não autorizado — token ausente ou expirado
    """
    operador_id = get_jwt_identity()
    resultado = auto_mode_service.ligar(bomba_id, operador_id)
    return jsonify(resultado), 200


@bp.route("/<int:bomba_id>/desligar", methods=["POST"])
@jwt_required()
def desligar(bomba_id):
    """
    Desligar Modo Automático
    ---
    tags:
      - Modo Automático
    summary: Desativa o modo automático (motor conclui o passo atual antes de parar)
    parameters:
      - name: bomba_id
        in: path
        type: integer
        required: true
        description: ID da motobomba
    responses:
      200:
        description: Resultado da tentativa de desativação
        content:
          application/json:
            schema:
              type: object
              properties:
                ok:
                  type: boolean
                detail:
                  type: string
      401:
        description: Não autorizado
    """
    resultado = auto_mode_service.desligar(bomba_id)
    if not resultado["ok"]:
        return jsonify(resultado), 400
    return jsonify(resultado), 200


@bp.route("/<int:bomba_id>/status", methods=["GET"])
@jwt_required()
def status(bomba_id):
    """
    Status do Modo Automático
    ---
    tags:
      - Modo Automático
    summary: Retorna o estado atual do loop de controle automático
    parameters:
      - name: bomba_id
        in: path
        type: integer
        required: true
        description: ID da motobomba
    responses:
      200:
        description: Estado atual do modo automático
        content:
          application/json:
            schema:
              type: object
              properties:
                ativo:
                  type: boolean
                bomba_id:
                  type: integer
                fase:
                  type: string
                  description: >
                    INICIANDO | DESCENDO | SUBINDO | ESTAVEL |
                    MOTOR_OFFLINE | SENSOR_OFFLINE | LIMITE_MINIMO |
                    SEM_LEITURA | ERRO | PARADO
                posicao_cm:
                  type: number
                limite_corrente:
                  type: number
                passo_cm:
                  type: number
                ciclos:
                  type: integer
                ultimo_erro:
                  type: string
                  nullable: true
      401:
        description: Não autorizado
    """
    return jsonify(auto_mode_service.get_status(bomba_id)), 200
