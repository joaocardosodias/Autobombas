"""
Validador de Proximidade por Sensores (Módulo 2-C → Módulo 2-A).

Implementa o intertravamento entre os sensores de fallback (HC-SR04) e
a movimentação XY da balsa, conforme documentação §3.3.2.2 e §3.3.2.4.

Zonas de risco (limiares em metros):
  d > dist_info                 → SEGURO
  dist_alerta < d ≤ dist_info   → INFORMATIVO
  dist_critico < d ≤ dist_alerta → ALERTA
  d ≤ dist_critico               → CRITICO
"""

import threading
from backend.repositories import leitura_distancia_repo

_lock = threading.Lock()

_limiares = {
    "dist_info_m": 2.0,
    "dist_alerta_m": 1.0,
    "dist_critico_m": 0.5,
}

NIVEL_SEGURO = "SEGURO"
NIVEL_INFORMATIVO = "INFORMATIVO"
NIVEL_ALERTA = "ALERTA"
NIVEL_CRITICO = "CRITICO"

DIRECAO_PARA_CAMPO = {
    "frente": "distancia_frente_m",
    "tras":   "distancia_tras_m",
    "esquerda": "distancia_esq_m",
    "direita":  "distancia_dir_m",
}

DIRECOES_MOVIMENTO = {"esquerda", "direita", "frente", "tras"}


def get_limiares() -> dict:
    """Retorna cópia dos limiares atuais."""
    with _lock:
        return dict(_limiares)


def set_limiares(dist_info_m: float, dist_alerta_m: float, dist_critico_m: float) -> tuple[bool, str]:
    """
    Atualiza os limiares de risco.
    Exige: 0 < dist_critico < dist_alerta < dist_info (conforme §3.3.2.3).

    Returns:
        (sucesso, mensagem)
    """
    if not (0 < dist_critico_m < dist_alerta_m < dist_info_m):
        return False, (
            f"Limiares invalidos. Exigido: 0 < dist_critico ({dist_critico_m}) "
            f"< dist_alerta ({dist_alerta_m}) < dist_info ({dist_info_m})."
        )

    with _lock:
        _limiares["dist_info_m"] = dist_info_m
        _limiares["dist_alerta_m"] = dist_alerta_m
        _limiares["dist_critico_m"] = dist_critico_m

    return True, "ok"


def classificar_distancia(distancia_m: float) -> str:
    """Classifica uma distância em nível de risco."""
    lim = get_limiares()
    if distancia_m <= lim["dist_critico_m"]:
        return NIVEL_CRITICO
    if distancia_m <= lim["dist_alerta_m"]:
        return NIVEL_ALERTA
    if distancia_m <= lim["dist_info_m"]:
        return NIVEL_INFORMATIVO
    return NIVEL_SEGURO


def avaliar_todas_direcoes(leitura: dict) -> dict:
    """
    Avalia os 4 sensores e retorna um dicionário com nível de risco
    e distância por direção.

    Returns:
        {
          "frente":   {"distancia_m": 1.23, "nivel": "ALERTA"},
          "tras":     {"distancia_m": 2.40, "nivel": "SEGURO"},
          "esquerda": {"distancia_m": 0.30, "nivel": "CRITICO"},
          "direita":  {"distancia_m": 1.80, "nivel": "INFORMATIVO"},
        }
    """
    resultado = {}
    for direcao, campo in DIRECAO_PARA_CAMPO.items():
        d = float(leitura.get(campo, 999))
        resultado[direcao] = {
            "distancia_m": d,
            "nivel": classificar_distancia(d),
        }
    return resultado


def verificar_movimento_permitido(bomba_id: int, direcao: str) -> tuple[bool, str, dict]:
    """
    Verifica se o movimento em determinada direção é permitido com base
    na última leitura dos sensores de proximidade.

    Returns:
        (permitido, mensagem, detalhes)
        - permitido: True se pode mover, False se bloqueado (CRITICO)
        - mensagem: descrição legível do estado
        - detalhes: dict com info do sensor relevante e de todas as direções
    """
    direcao_lower = direcao.lower().strip()

    if direcao_lower not in DIRECOES_MOVIMENTO:
        return True, "ok", {}

    leitura = leitura_distancia_repo.ultima_leitura(bomba_id)
    if not leitura:
        return True, "ok (sem leitura de sensores disponivel)", {}

    status_direcoes = avaliar_todas_direcoes(leitura)
    sensor = status_direcoes.get(direcao_lower, {})
    nivel = sensor.get("nivel", NIVEL_SEGURO)
    distancia = sensor.get("distancia_m", 999)

    detalhes = {
        "direcao_solicitada": direcao_lower,
        "sensor": sensor,
        "todas_direcoes": status_direcoes,
        "timestamp_leitura": leitura.get("timestamp_leitura"),
    }

    if nivel == NIVEL_CRITICO:
        lim = get_limiares()
        return (
            False,
            f"BLOQUEADO: Proximidade critica na direcao '{direcao_lower}' "
            f"(distancia: {distancia:.2f} m, limite critico: {lim['dist_critico_m']} m). "
            f"Movimentacao bloqueada por seguranca.",
            detalhes,
        )

    if nivel == NIVEL_ALERTA:
        detalhes["velocidade_reduzida"] = True
        return (
            True,
            f"ALERTA: Proximidade elevada na direcao '{direcao_lower}' "
            f"(distancia: {distancia:.2f} m). Velocidade reduzida.",
            detalhes,
        )

    return True, "ok", detalhes


def verificar_proximidade_critica(leitura: dict) -> list[dict]:
    """
    Verifica se algum sensor está em nível CRITICO.
    Usado pelo listener MQTT para disparo automático de parada.

    Returns:
        Lista de dicts com as direções em estado crítico.
        Lista vazia se nenhuma direção estiver em estado crítico.
    """
    criticos = []
    status = avaliar_todas_direcoes(leitura)
    for direcao, info in status.items():
        if info["nivel"] == NIVEL_CRITICO:
            criticos.append({
                "direcao": direcao,
                "distancia_m": info["distancia_m"],
            })
    return criticos


def obter_status_sensores(bomba_id: int) -> dict:
    """
    Retorna o status completo dos sensores para uma bomba,
    incluindo classificação de risco por direção e se há bloqueios ativos.
    """
    leitura = leitura_distancia_repo.ultima_leitura(bomba_id)
    if not leitura:
        return {
            "disponivel": False,
            "mensagem": "Nenhuma leitura de sensores disponivel para esta bomba.",
        }

    status_direcoes = avaliar_todas_direcoes(leitura)

    bloqueios = []
    alertas = []
    for direcao, info in status_direcoes.items():
        if info["nivel"] == NIVEL_CRITICO:
            bloqueios.append(direcao)
        elif info["nivel"] == NIVEL_ALERTA:
            alertas.append(direcao)

    return {
        "disponivel": True,
        "bomba_id": bomba_id,
        "timestamp_leitura": leitura.get("timestamp_leitura"),
        "direcoes": status_direcoes,
        "direcoes_bloqueadas": bloqueios,
        "direcoes_alerta": alertas,
        "limiares": get_limiares(),
    }
