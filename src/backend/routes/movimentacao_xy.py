from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from backend.models.movimentacao_xy import MovimentacaoXYCreate, MovimentacaoXYUpdate
from backend.repositories import movimentacao_xy_repo, movimentacao_z_repo, leitura_distancia_repo, bomba_repo
from backend.repositories import sistema_repo
from backend.services import mqtt_service
from backend.services.validador_balsa import motobomba_esta_na_origem, acao_exige_validacao
from backend.services.validador_sensores import verificar_movimento_permitido, obter_status_sensores

ACOES_VALIDAS = {"ligar", "desligar", "parar", "esquerda", "direita", "frente", "tras"}


# Mapeamento: ação da balsa → campo do sensor 2-C e chave de limite no DB
ACAO_PARA_SENSOR = {
    "frente":   ("distancia_frente_m", "frente"),
    "tras":     ("distancia_tras_m",   "tras"),
    "esquerda": ("distancia_esq_m",    "esq"),
    "direita":  ("distancia_dir_m",    "dir"),
}

bp = Blueprint("movimentacao_xy", __name__, url_prefix="/movimentacao-xy")
BLOQUEAR_NOVAS_OPERACOES = True


# ── Helpers de intertravamento ──────────────────────────────────────

def acao_exige_validacao(acao: str) -> bool:
    """Retorna True se a ação é um movimento direcional que precisa de validação."""
    return acao in ("esquerda", "direita", "frente", "tras")


def motobomba_esta_na_origem(bomba_id: int) -> tuple[bool, str]:
    """
    Verifica se a motobomba Z está na posição zero (corda totalmente recolhida).
    A balsa só pode se movimentar com a bomba na origem.
    """
    reg = movimentacao_z_repo.recuperar_posicao(bomba_id)
    if reg is None:
        return True, ""  # sem registros = posição 0 (nunca moveu)

    posicao = float(reg.get("posicao_final_cm") or 0)
    if posicao > 0.5:  # tolerância de 0.5cm
        return False, (
            f"Motobomba Z está em {posicao:.2f} cm. "
            f"Recolha a corda para a origem (/z reset) antes de movimentar a balsa."
        )
    return True, ""


def verificar_movimento_permitido(bomba_id: int, acao: str) -> tuple[bool, str, dict]:
    """
    Verifica os sensores de distância do módulo 2-C.
    Limites de bloqueio por direção são lidos do banco de dados.

    Retorna: (permitido, mensagem, detalhes)
    """
    mapeamento = ACAO_PARA_SENSOR.get(acao)
    if not mapeamento:
        return True, "", {}  # ação sem sensor associado (ligar, desligar, parar)

    campo_sensor, chave_limite = mapeamento

    # Lê o limite configurado no banco (com fallback para 0.30m)
    limites = bomba_repo.get_limite_proximidade(bomba_id)
    dist_minima = limites[chave_limite]

    leitura = leitura_distancia_repo.ultima_leitura(bomba_id)
    if not leitura:
        return True, "", {"radar_disponivel": False}

    distancia = float(leitura.get(campo_sensor, 999))
    detalhes = {
        "radar_disponivel": True,
        "direcao": acao,
        "campo_sensor": campo_sensor,
        "distancia_m": distancia,
        "limite_bloqueio_m": dist_minima,
    }

    if distancia < dist_minima:
        detalhes["bloqueado"] = True
        return (
            False,
            f"Movimento para '{acao}' BLOQUEADO: obstáculo a {distancia:.2f}m "
            f"(mínimo configurado: {dist_minima}m).",
            detalhes,
        )

    return True, "", detalhes


# ── Rotas ───────────────────────────────────────────────────────────

@bp.route("/", methods=["POST"])
@jwt_required()
def criar_registro():
    """
    Criar Registro de Movimentação XY
    ---
    tags:
      - Movimentação XY
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - bomba_id
              - operador_id
              - direcao
            properties:
              bomba_id:
                type: integer
              operador_id:
                type: integer
              direcao:
                type: string
    responses:
      201:
        description: Registro criado e comando publicado
      400:
        description: Dados inválidos
      401:
        description: Não autorizado
      403:
        description: Bloqueado por intertravamento
      503:
        description: ESP offline
    """
    if BLOQUEAR_NOVAS_OPERACOES:
        return jsonify({"detail": "Criacao de operacoes desativada"}), 403

    body = request.get_json()
    dados = MovimentacaoXYCreate(**body)

    # ESP online?
    hb = sistema_repo.get_heartbeat_modulo("balsa", dados.bomba_id)
    if not hb or not hb["online"]:
        return jsonify({
            "detail": f"ESP balsa/{dados.bomba_id} está offline. Comando não enviado."
        }), 503

    # Intertravamento 1: motobomba na origem
    permitido, msg = motobomba_esta_na_origem(dados.bomba_id)
    if not permitido:
        return jsonify({"detail": msg}), 403

    # Intertravamento 2: proximidade (módulo 2-C)
    sensor_ok, sensor_msg, sensor_detalhes = verificar_movimento_permitido(
        dados.bomba_id, dados.direcao
    )
    if not sensor_ok:
        return jsonify({"detail": sensor_msg, "sensores": sensor_detalhes}), 403

    registro = movimentacao_xy_repo.criar(dados)

    # Publica comando no MQTT para o ESP
    payload_mqtt = {
        "acao": dados.direcao,
        "operador_id": dados.operador_id,
    }

    topico = f"balsa/{dados.bomba_id}/comando"
    mqtt_service.publicar(topico, payload_mqtt)

    resposta = dict(registro)
    if sensor_detalhes.get("velocidade_reduzida"):
        resposta["alerta_proximidade"] = sensor_msg
        resposta["velocidade_reduzida"] = True

    return jsonify(resposta), 201


@bp.route("/<int:registro_id>", methods=["PATCH"])
@jwt_required()
def atualizar_registro(registro_id):
    """
    Atualizar Registro de Movimentação XY
    ---
    tags:
      - Movimentação XY
    parameters:
      - name: registro_id
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
              status:
                type: string
              concluido_em:
                type: string
                format: date-time
    responses:
      200:
        description: Registro atualizado
      401:
        description: Não autorizado
      404:
        description: Registro não encontrado
    """
    body = request.get_json()
    dados = MovimentacaoXYUpdate(**body)
    registro = movimentacao_xy_repo.atualizar(registro_id, dados)

    if not registro:
        return jsonify({"detail": "Registro nao encontrado"}), 404
    return jsonify(registro)


@bp.route("/bomba/<int:bomba_id>", methods=["GET"])
@jwt_required()
def listar_por_bomba(bomba_id):
    """
    Listar Movimentações XY por Bomba
    ---
    tags:
      - Movimentação XY
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
        description: Lista de movimentações
      401:
        description: Não autorizado
    """
    limite = request.args.get("limite", 10, type=int)
    registros = movimentacao_xy_repo.listar_por_bomba(bomba_id, limite)
    return jsonify(registros)


@bp.route("/pode-mover/<int:bomba_id>", methods=["GET"])
@jwt_required()
def pode_mover(bomba_id):
    """
    Verificar se a balsa pode ser movimentada (motobomba na origem + sensores)
    ---
    tags:
      - Movimentação XY
    parameters:
      - name: bomba_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Status de permissão incluindo intertravamento de sensores
      401:
        description: Não autorizado
    """
    permitido, msg = motobomba_esta_na_origem(bomba_id)
    sensores = obter_status_sensores(bomba_id)
    return jsonify({
        "pode_mover": permitido,
        "mensagem": msg,
        "sensores": sensores,
    })


@bp.route("/fechar-orfaos/<int:bomba_id>", methods=["PATCH"])
@jwt_required()
def fechar_orfaos(bomba_id):
    """
    Fechar Registros Órfãos (Em Andamento)
    ---
    tags:
      - Movimentação XY
    parameters:
      - name: bomba_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Retorna os IDs fechados e o total
      401:
        description: Não autorizado
    """
    ids = movimentacao_xy_repo.fechar_orfaos(bomba_id)
    return jsonify({"fechados": ids, "total": len(ids)})


@bp.route("/comando/<int:bomba_id>", methods=["POST"])
@jwt_required()
def enviar_comando(bomba_id):
    """
    Enviar Comando MQTT (Ações Genéricas)
    ---
    tags:
      - Movimentação XY
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
            required:
              - acao
              - operador_id
            properties:
              acao:
                type: string
                description: ligar, desligar, parar, esquerda, direita, frente, tras
              operador_id:
                type: integer
    responses:
      200:
        description: Comando enviado
      400:
        description: Ação inválida
      401:
        description: Não autorizado
      403:
        description: Bloqueado por intertravamento
      503:
        description: ESP offline
    """
    body = request.get_json()
    acao = body.get("acao")
    operador_id = body.get("operador_id")

    if acao not in ACOES_VALIDAS:
        return jsonify({"detail": f"Acao invalida: '{acao}'. Validas: {sorted(ACOES_VALIDAS)}"}), 400

    # ESP online?
    hb = sistema_repo.get_heartbeat_modulo("balsa", bomba_id)
    if not hb or not hb["online"]:
        return jsonify({
            "detail": f"ESP balsa/{bomba_id} está offline. Comando não enviado."
        }), 503

    # Valida interlocks apenas para movimentos direcionais
    if acao_exige_validacao(acao):
        # Intertravamento 1: motobomba na origem
        permitido, msg = motobomba_esta_na_origem(bomba_id)
        if not permitido:
            return jsonify({"detail": msg}), 403

        # Intertravamento 2: proximidade (módulo 2-C)
        sensor_ok, sensor_msg, sensor_detalhes = verificar_movimento_permitido(bomba_id, acao)
        if not sensor_ok:
            return jsonify({"detail": sensor_msg, "sensores": sensor_detalhes}), 403
        
    if acao in ["parar", "desligar"]:
        movimentacao_xy_repo.fechar_orfaos(bomba_id)

    payload_mqtt = {"acao": acao, "operador_id": operador_id}

    topico = f"balsa/{bomba_id}/comando"
    mqtt_service.publicar(topico, payload_mqtt)

    resp = {"ok": True, "acao": acao}
    return jsonify(resp), 200
