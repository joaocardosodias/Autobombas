from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from backend.repositories import sistema_repo

bp = Blueprint("sistema", __name__, url_prefix="/sistema")


@bp.route("/status/<int:bomba_id>", methods=["GET"])
@jwt_required()
def get_status(bomba_id):
    status = sistema_repo.get_status_sistema(bomba_id)

    if status is None:
        return jsonify({"detail": "Bomba não encontrada"}), 404

    return jsonify(status), 200


@bp.route("/heartbeat", methods=["GET"])
def get_heartbeat_todos():
    """
    Retorna o estado de heartbeat de todos os módulos ESP.
    ---
    tags:
      - Sistema
    responses:
      200:
        description: Lista de módulos com status online/offline
    """
    estado = sistema_repo.get_heartbeat_todos()
    return jsonify(estado), 200


@bp.route("/heartbeat/<string:tipo>/<int:modulo_id>", methods=["GET"])
def get_heartbeat_modulo(tipo, modulo_id):
    """
    Retorna o estado de heartbeat de um módulo ESP específico.
    ---
    tags:
      - Sistema
    parameters:
      - name: tipo
        in: path
        type: string
        required: true
        description: Tipo do módulo (motor, sensor, balsa)
      - name: modulo_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Estado do módulo
      404:
        description: Módulo não encontrado
    """
    estado = sistema_repo.get_heartbeat_modulo(tipo, modulo_id)
    if estado is None:
        return jsonify({"detail": "Módulo não encontrado"}), 404
    return jsonify(estado), 200


@bp.route("/heartbeat/debug", methods=["GET"])
def get_heartbeat_debug():
    """
    Debug: Todos os PINGs já recebidos desde a inicialização
    ---
    tags:
      - Sistema
    summary: >
      Mostra o estado bruto de todos os módulos que já enviaram PING,
      inclusive os que não estão na lista de módulos conhecidos.
      Útil para diagnosticar conflitos de tópico (ex: sensor/1 vs corrente/1).
    responses:
      200:
        description: Estado bruto do heartbeat
    """
    from backend.services.mqtt_service import _heartbeat_state, _heartbeat_lock, _MODULOS_CONHECIDOS
    from datetime import datetime
    agora = datetime.now()
    with _heartbeat_lock:
        raw = {
            chave: {
                "ultimo_ping": ts.isoformat(),
                "segundos_atras": round((agora - ts).total_seconds(), 1),
                "online": (agora - ts).total_seconds() <= 5,
            }
            for chave, ts in _heartbeat_state.items()
        }
    conhecidos = [f"{t}/{i}" for t, i in _MODULOS_CONHECIDOS]
    return jsonify({
        "estado_bruto": raw,
        "modulos_conhecidos": conhecidos,
        "modulos_sem_ping": [m for m in conhecidos if m not in raw],
        "pings_desconhecidos": [k for k in raw if k not in conhecidos],
    }), 200