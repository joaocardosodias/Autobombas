from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from backend.models.leitura_distancia import LeituraDistanciaCreate
from backend.repositories import leitura_distancia_repo
from backend.services import mqtt_service
from backend.services.validador_sensores import obter_status_sensores, get_limiares, set_limiares

bp = Blueprint("leituras_distancia", __name__, url_prefix="/leituras-distancia")


@bp.route("/", methods=["POST"])
@jwt_required()
def criar_leitura():
    """
    Criar Leitura de Distância Manual
    ---
    tags:
      - Leituras Distância
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - bomba_id
              - operador_id
              - distancia_frente_m
              - distancia_tras_m
              - distancia_esq_m
              - distancia_dir_m
            properties:
              bomba_id:
                type: integer
              operador_id:
                type: integer
              distancia_frente_m:
                type: number
              distancia_tras_m:
                type: number
              distancia_esq_m:
                type: number
              distancia_dir_m:
                type: number
    responses:
      201:
        description: Leitura criada
      400:
        description: Dados inválidos
      401:
        description: Não autorizado
    """
    body = request.get_json()
    dados = LeituraDistanciaCreate(**body)
    registro = leitura_distancia_repo.criar(dados)
    return jsonify(registro), 201


@bp.route("/bomba/<int:bomba_id>", methods=["GET"])
@jwt_required()
def listar_por_bomba(bomba_id):
    """
    Listar Leituras de Distância por Bomba
    ---
    tags:
      - Leituras Distância
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
    registros = leitura_distancia_repo.listar_por_bomba(bomba_id, limite)
    return jsonify(registros)


@bp.route("/bomba/<int:bomba_id>/ultima", methods=["GET"])
@jwt_required()
def ultima_leitura(bomba_id):
    """
    Obter Última Leitura de Distância
    ---
    tags:
      - Leituras Distância
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
    leitura = leitura_distancia_repo.ultima_leitura(bomba_id)
    if not leitura:
        return jsonify({"detail": "Nenhuma leitura encontrada"}), 404
    return jsonify(leitura)


@bp.route("/solicitar/<int:bomba_id>", methods=["POST"])
@jwt_required()
def solicitar_leitura(bomba_id):
    """
    Solicitar Leitura de Distância (MQTT)
    ---
    tags:
      - Leituras Distância
    parameters:
      - name: bomba_id
        in: path
        type: integer
        required: true
    requestBody:
      required: false
      content:
        application/json:
          schema:
            type: object
            properties:
              operador_id:
                type: integer
    responses:
      200:
        description: Comando de leitura de distância enviado
      401:
        description: Não autorizado
    """
    body = request.get_json() or {}
    operador_id = body.get("operador_id")
    topico = f"sensor/{bomba_id}/comando"
    mqtt_service.publicar(topico, {"acao": "ler_distancia", "operador_id": operador_id})
    return jsonify({"ok": True, "acao": "ler_distancia"})


@bp.route("/bomba/<int:bomba_id>/status-proximidade", methods=["GET"])
@jwt_required()
def status_proximidade(bomba_id):
    """
    Status de Proximidade e Intertravamento dos Sensores (Módulo 2-C)
    ---
    tags:
      - Leituras Distância
    parameters:
      - name: bomba_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: >
          Retorna classificação de risco por direção (SEGURO, INFORMATIVO,
          ALERTA, CRITICO), direções bloqueadas e em alerta, e os limiares
          configurados.
      401:
        description: Não autorizado
    """
    status = obter_status_sensores(bomba_id)
    return jsonify(status)


@bp.route("/limiares", methods=["GET"])
@jwt_required()
def consultar_limiares():
    """
    Consultar Limiares de Risco dos Sensores
    ---
    tags:
      - Leituras Distância
    responses:
      200:
        description: Limiares atuais (dist_info_m, dist_alerta_m, dist_critico_m)
      401:
        description: Não autorizado
    """
    return jsonify(get_limiares())


@bp.route("/limiares", methods=["PUT"])
@jwt_required()
def atualizar_limiares():
    """
    Atualizar Limiares de Risco dos Sensores
    ---
    tags:
      - Leituras Distância
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - dist_info_m
              - dist_alerta_m
              - dist_critico_m
            properties:
              dist_info_m:
                type: number
                description: Limite superior da zona informativa (metros)
              dist_alerta_m:
                type: number
                description: Limite da zona de alerta (metros)
              dist_critico_m:
                type: number
                description: Limite da zona crítica (metros)
    responses:
      200:
        description: Limiares atualizados
      400:
        description: Valores inválidos (exigido 0 < critico < alerta < info)
      401:
        description: Não autorizado
    """
    body = request.get_json()
    dist_info = body.get("dist_info_m")
    dist_alerta = body.get("dist_alerta_m")
    dist_critico = body.get("dist_critico_m")

    if dist_info is None or dist_alerta is None or dist_critico is None:
        return jsonify({"detail": "Campos obrigatorios: dist_info_m, dist_alerta_m, dist_critico_m"}), 400

    try:
        dist_info = float(dist_info)
        dist_alerta = float(dist_alerta)
        dist_critico = float(dist_critico)
    except (TypeError, ValueError):
        return jsonify({"detail": "Todos os valores devem ser numericos"}), 400

    ok, msg = set_limiares(dist_info, dist_alerta, dist_critico)
    if not ok:
        return jsonify({"detail": msg}), 400

    return jsonify(get_limiares())
