import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import json
from datetime import datetime, date
from decimal import Decimal

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from flask_cors import CORS

from backend.config import settings
from backend.routes import auth, bombas, movimentacao_z, movimentacao_xy, leituras_corrente, leituras_distancia, logs, sistema, auto_mode, usuarios, gestao
from backend.services import mqtt_service
from backend.repositories import movimentacao_z_repo, leitura_corrente_repo, leitura_distancia_repo


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def criar_app():
    app = Flask(__name__)
    CORS(app)
    app.json_encoder = CustomEncoder
    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    
    # Configuração do Swagger
    app.config["SWAGGER"] = {
        "title": "API G06 - Automação",
        "uiversion": 3,
    }
    Swagger(app)

    JWTManager(app)

    # Registra blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(usuarios.bp)
    app.register_blueprint(bombas.bp)
    app.register_blueprint(movimentacao_z.bp)
    app.register_blueprint(movimentacao_xy.bp)
    app.register_blueprint(leituras_corrente.bp)
    app.register_blueprint(leituras_distancia.bp)
    app.register_blueprint(logs.bp)
    app.register_blueprint(sistema.bp)
    app.register_blueprint(auto_mode.bp)
    app.register_blueprint(gestao.bp)

    # Error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"detail": str(e)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"detail": "Recurso nao encontrado"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"detail": "Erro interno do servidor"}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        print(f"[ERRO] {type(e).__name__}: {e}")
        return jsonify({"detail": "Erro inesperado no servidor"}), 500

    @app.route("/")
    def health():
        return {"status": "ok", "message": "API G06 ativa (Flask)"}

    return app


# === MQTT Listener Callback ===
def on_esp_message(client, userdata, msg):
    """Callback para mensagens dos ESPs: atualiza o DB automaticamente."""
    topic = msg.topic
    payload = msg.payload.decode("utf-8")

    parts = topic.split("/")
    if len(parts) < 3:
        return

    tipo = parts[0]
    bomba_id = parts[1]
    canal = parts[2]

    # Heartbeat: <tipo>/<id>/heartbeat
    if canal == "heartbeat":
        print(f"[HB-RECV] Tópico: {topic} | Payload: {payload.strip()!r}")
        if payload.strip() == "PING":
            mqtt_service.registrar_heartbeat(tipo, int(bomba_id))
        return

    # Agora suportamos 'status' ou 'distancias'
    if canal not in ["status", "distancias"]:
        return

    print(f"[MQTT-IN] {topic}: {payload}")

    if tipo == "motor" and canal == "status":
        tratar_status_motor(int(bomba_id), payload)
    elif tipo in ["sensor", "corrente"] and canal == "status":
        tratar_leitura_sensor(int(bomba_id), payload)
    elif tipo == "sensor" and canal == "distancias":
        tratar_leitura_distancias(int(bomba_id), payload)


def tratar_status_motor(bomba_id, payload):
    """Atualiza movimentacao_z quando o ESP reporta LIVRE ou ABORTADO."""
    if payload == "LIVRE":
        reg = movimentacao_z_repo.concluir_em_andamento(bomba_id)
        if reg:
            print(f"[MQTT-IN] Registro #{reg['id']} -> CONCLUIDO")

    elif payload.startswith("ABORTADO:"):
        try:
            voltas_feitas = float(payload.split(":")[1])
        except (IndexError, ValueError):
            return
        reg = movimentacao_z_repo.abortar_em_andamento(bomba_id, voltas_feitas)
        if reg:
            print(f"[MQTT-IN] Registro #{reg['id']} -> ABORTADO")


def tratar_leitura_sensor(bomba_id, payload):
    """Salva leitura de corrente recebida do ESP no DB."""
    import json
    try:
        dados = json.loads(payload)
    except (json.JSONDecodeError, ValueError):
        return

    corrente = dados.get("corrente_a", 0)
    operador_id = dados.get("operador_id", None)

    from backend.models.leitura_corrente import LeituraCorrenteCreate
    reg = leitura_corrente_repo.criar(LeituraCorrenteCreate(
        bomba_id=bomba_id,
        operador_id=operador_id,
        corrente_a=corrente,
    ))
    print(f"[MQTT-IN] Leitura #{reg['id']} salva: {corrente}A")


def tratar_leitura_distancias(bomba_id, payload):
    """Salva leitura das distancias recebida do ESP (modulo 2-C) no DB.
    Se houver proximidade critica, envia parada automatica para a balsa."""
    import json
    try:
        dados = json.loads(payload)
    except (json.JSONDecodeError, ValueError):
        return

    operador_id = dados.get("operador_id", 1)

    from backend.models.leitura_distancia import LeituraDistanciaCreate
    try:
        reg = leitura_distancia_repo.criar(LeituraDistanciaCreate(
            bomba_id=bomba_id,
            operador_id=operador_id,
            distancia_frente_m=dados.get("frente_m", 0.0),
            distancia_tras_m=dados.get("tras_m", 0.0),
            distancia_esq_m=dados.get("esq_m", 0.0),
            distancia_dir_m=dados.get("dir_m", 0.0)
        ))
        print(f"[MQTT-IN] Leitura Distancia #{reg['id']} salva.")
    except Exception as e:
        print(f"[MQTT-IN] Erro ao salvar leitura de distancia: {e}")
        return

    _verificar_parada_emergencia(bomba_id, reg)


def _verificar_parada_emergencia(bomba_id, leitura):
    """Intertravamento 2C→2A para balsa em movimento: se a balsa estiver se
    movendo em uma direção e atingir o limite configurado no banco para essa
    direção, envia PARAR automaticamente e fecha a movimentação."""
    from backend.repositories import movimentacao_xy_repo, bomba_repo
    from backend.services import mqtt_service

    em_andamento = movimentacao_xy_repo.buscar_em_andamento(bomba_id)
    if not em_andamento:
        return

    ACAO_PARA_SENSOR = {
        "frente":   ("distancia_frente_m", "frente"),
        "tras":     ("distancia_tras_m",   "tras"),
        "esquerda": ("distancia_esq_m",    "esq"),
        "direita":  ("distancia_dir_m",    "dir"),
    }

    limites = bomba_repo.get_limite_proximidade(bomba_id)
    criticos = []

    for mov in em_andamento:
        direcao = mov.get("direcao")
        if direcao not in ACAO_PARA_SENSOR:
            continue
            
        campo_sensor, chave_limite = ACAO_PARA_SENSOR[direcao]
        dist_minima = limites[chave_limite]
        distancia_atual = float(leitura.get(campo_sensor, 999))
        
        if distancia_atual < dist_minima:
            criticos.append({
                "direcao": direcao,
                "distancia_m": distancia_atual,
                "limite_m": dist_minima
            })

    if not criticos:
        return

    direcoes = ", ".join(c["direcao"] for c in criticos)
    distancias = ", ".join(f"{c['direcao']}={c['distancia_m']:.2f}m (limite={c['limite_m']}m)" for c in criticos)
    print(
        f"[INTERLOCK] Proximidade CRITICA detectada na bomba {bomba_id}: "
        f"{distancias}. Enviando parada de emergencia."
    )

    topico = f"balsa/{bomba_id}/comando"
    mqtt_service.publicar(topico, {
        "acao": "parar",
        "motivo": f"parada_emergencia_sensores",
        "direcoes_criticas": direcoes,
    })

    ids_fechados = movimentacao_xy_repo.fechar_orfaos(bomba_id)
    if ids_fechados:
        print(
            f"[INTERLOCK] {len(ids_fechados)} movimentacao(oes) XY "
            f"encerrada(s) automaticamente: {ids_fechados}"
        )


# === Entry Point ===
if __name__ == "__main__":
    app = criar_app()

    mqtt_service.iniciar_listener(on_esp_message)
    print("[MQTT] Listener ativo — aguardando status dos ESPs")

    app.run(host="0.0.0.0", port=5000, debug=False)
