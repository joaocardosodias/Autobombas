from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from backend.models.leitura_corrente import LeituraCorrenteCreate
from backend.repositories import leitura_corrente_repo
from backend.repositories import sistema_repo
from backend.services import mqtt_service

bp = Blueprint("leituras_corrente", __name__, url_prefix="/leituras-corrente")


@bp.route("/", methods=["POST"])
@jwt_required()
def criar_leitura():
    """
    Criar Leitura de Corrente Manual
    ---
    tags:
      - Leituras Corrente
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - bomba_id
              - corrente_a
            properties:
              bomba_id:
                type: integer
              operador_id:
                type: integer
              corrente_a:
                type: number
    responses:
      201:
        description: Leitura registrada com sucesso
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                bomba_id:
                  type: integer
                operador_id:
                  type: integer
                  nullable: true
                corrente_a:
                  type: number
                timestamp_leitura:
                  type: string
                  format: date-time
      400:
        description: Dados inválidos
      401:
        description: Não autorizado
    """
    body = request.get_json()
    dados = LeituraCorrenteCreate(**body)
    registro = leitura_corrente_repo.criar(dados)
    return jsonify(registro), 201


@bp.route("/bomba/<int:bomba_id>", methods=["GET"])
@jwt_required()
def listar_por_bomba(bomba_id):
    """
    Listar Leituras de Corrente por Bomba
    ---
    tags:
      - Leituras Corrente
    parameters:
      - name: bomba_id
        in: path
        type: integer
        required: true
      - name: limite
        in: query
        type: integer
        required: false
        default: 10
    responses:
      200:
        description: Lista de leituras
      401:
        description: Não autorizado
    """
    limite = request.args.get("limite", 10, type=int)
    registros = leitura_corrente_repo.listar_por_bomba(bomba_id, limite)
    return jsonify(registros)


@bp.route("/bomba/<int:bomba_id>/ultima", methods=["GET"])
@jwt_required()
def ultima_leitura(bomba_id):
    """
    Obter Última Leitura de Corrente
    ---
    tags:
      - Leituras Corrente
    parameters:
      - name: bomba_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Última leitura
      401:
        description: Não autorizado
      404:
        description: Nenhuma leitura encontrada
    """
    leitura = leitura_corrente_repo.ultima_leitura(bomba_id)
    if not leitura:
        return jsonify({"detail": "Nenhuma leitura encontrada"}), 404
    return jsonify(leitura)


@bp.route("/solicitar/<int:bomba_id>", methods=["POST"])
@jwt_required()
def solicitar_leitura(bomba_id):
    """
    Solicitar Leitura via MQTT
    ---
    tags:
      - Leituras Corrente
    parameters:
      - name: bomba_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Comando de leitura enviado ao ESP
        content:
          application/json:
            schema:
              type: object
              properties:
                ok:
                  type: boolean
                acao:
                  type: string
                  example: ler
      401:
        description: Não autorizado
      503:
        description: ESP corrente offline — comando não enviado
    """
    # Verifica se o ESP de corrente está online
    hb = sistema_repo.get_heartbeat_modulo("corrente", bomba_id)
    if not hb or not hb["online"]:
        return jsonify({
            "detail": f"ESP corrente/{bomba_id} está offline. Comando não enviado."
        }), 503

    body = request.get_json() or {}
    operador_id = body.get("operador_id")
    topico = f"corrente/{bomba_id}/comando"
    mqtt_service.publicar(topico, {"acao": "ler", "operador_id": operador_id})
    return jsonify({"ok": True, "acao": "ler"})
