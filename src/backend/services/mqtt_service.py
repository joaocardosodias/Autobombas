import json
import threading
import time
from datetime import datetime
import paho.mqtt.client as mqtt

from backend.config import settings

_client = None
_lock = threading.Lock()

# === Heartbeat state ===
# Chave: "<tipo>/<id>" (ex: "motor/1", "sensor/1", "balsa/1")
# Valor: timestamp do último PING recebido
_heartbeat_state: dict[str, datetime] = {}
_heartbeat_lock = threading.Lock()

# Módulos conhecidos que devem receber PONG periódico do backend
_MODULOS_CONHECIDOS = [
    ("motor",    1),
    ("corrente", 1),   # módulo1-B (sensor de corrente)
    ("sensor",   1),   # módulo2-C (sensores de distância)
    ("balsa",    1),
]

HEARTBEAT_TIMEOUT_S = 2.5  # segundos sem PING = considerado offline


def _get_client():
    global _client
    with _lock:
        if _client is None or not _client.is_connected():
            try:
                _client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
                _client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
                _client.loop_start()
            except Exception as e:
                print(f"[MQTT] Broker indisponivel: {e}")
                _client = None
    return _client


def publicar(topico: str, payload: dict) -> bool:
    client = _get_client()
    if client is None:
        print(f"[MQTT] Falha ao publicar em {topico} (broker offline)")
        return False
    client.publish(topico, json.dumps(payload))
    return True


def publicar_raw(topico: str, payload: str) -> bool:
    """Publica um payload string puro (sem serialização JSON), ex: 'EMERGENCIA'."""
    client = _get_client()
    if client is None:
        print(f"[MQTT] Falha ao publicar raw em {topico} (broker offline)")
        return False
    client.publish(topico, payload)
    return True


def registrar_heartbeat(tipo: str, modulo_id: int):
    """Registra o recebimento de um PING de um ESP e publica PONG de volta."""
    chave = f"{tipo}/{modulo_id}"
    with _heartbeat_lock:
        _heartbeat_state[chave] = datetime.now()

    topico_ack = f"{tipo}/{modulo_id}/heartbeat/ack"
    client = _get_client()
    if client:
        client.publish(topico_ack, "PONG")

    print(f"[HB] PING recebido de {chave} -> PONG enviado")


def get_heartbeat_status() -> list[dict]:
    """Retorna o estado de heartbeat de todos os módulos conhecidos."""
    agora = datetime.now()
    resultado = []

    with _heartbeat_lock:
        for tipo, modulo_id in _MODULOS_CONHECIDOS:
            chave = f"{tipo}/{modulo_id}"
            ultimo_ping = _heartbeat_state.get(chave)
            if ultimo_ping:
                delta = (agora - ultimo_ping).total_seconds()
                online = delta <= HEARTBEAT_TIMEOUT_S
            else:
                ultimo_ping = None
                online = False

            resultado.append({
                "modulo": chave,
                "tipo": tipo,
                "modulo_id": modulo_id,
                "online": online,
                "ultimo_ping": ultimo_ping,
            })

    return resultado


def _thread_pong_periodico():
    """Thread que envia PONG periódico do backend para cada ESP conhecido."""
    while True:
        client = _get_client()
        if client:
            for tipo, modulo_id in _MODULOS_CONHECIDOS:
                topico_ack = f"{tipo}/{modulo_id}/heartbeat/ack"
                client.publish(topico_ack, "PONG")
        time.sleep(1)


def iniciar_listener(on_message_callback):
    """Inicia subscriber MQTT em thread separada. Reconecta automaticamente."""

    def _loop():
        while True:
            try:
                sub_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

                def on_connect(client, userdata, flags, rc, properties):
                    client.subscribe("motor/+/status")
                    client.subscribe("balsa/+/status")
                    client.subscribe("sensor/+/status")
                    client.subscribe("sensor/+/distancias")
                    client.subscribe("corrente/+/status")
                    client.subscribe("+/+/heartbeat")
                    print("[MQTT] Listener inscrito em motor/+, balsa/+, sensor/+, corrente/+, +/+/heartbeat")

                sub_client.on_connect = on_connect
                sub_client.on_message = on_message_callback
                sub_client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
                sub_client.loop_forever()
            except Exception as e:
                print(f"[MQTT] Listener desconectado ({e}). Reconectando em 5s...")
                time.sleep(5)

    thread_listener = threading.Thread(target=_loop, daemon=True)
    thread_listener.start()

    thread_pong = threading.Thread(target=_thread_pong_periodico, daemon=True)
    thread_pong.start()

    return thread_listener
