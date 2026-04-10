from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime

from backend.models.movimentacao_z import MovimentacaoZCreate, MovimentacaoZUpdate
from backend.repositories import movimentacao_z_repo, movimentacao_xy_repo
from backend.repositories import sistema_repo, bomba_repo
from backend.services import mqtt_service

bp = Blueprint("movimentacao_z", __name__, url_prefix="/movimentacao-z")
BLOQUEAR_NOVAS_OPERACOES = True


def _status_db_para_ui(status_db: str | None) -> str:
    if status_db == "EM_ANDAMENTO":
        return "Em Andamento"
    if status_db == "CONCLUIDO":
        return "Finalizada"
    return "Alerta"


def _duracao_ui(inicio, fim) -> str:
    if not inicio:
        return "-"
    fim_ref = fim if fim is not None else datetime.now(inicio.tzinfo) if inicio.tzinfo else datetime.utcnow()
    total_segundos = max(0, int((fim_ref - inicio).total_seconds()))
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    if horas > 0:
        return f"{horas}h {minutos}min"
    return f"{minutos}min"


@bp.route("/", methods=["POST"])
@jwt_required()
def criar_registro():
    """
    Criar Registro de Movimentação Z
    ---
    tags:
      - Movimentação Z
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - bomba_id
              - operador_id
              - voltas_mqtt
              - comando_bruto
              - posicao_inicial_cm
              - deslocamento_solicitado_cm
            properties:
              bomba_id:
                type: integer
              operador_id:
                type: integer
              voltas_mqtt:
                type: number
              comando_bruto:
                type: string
              posicao_inicial_cm:
                type: number
              deslocamento_solicitado_cm:
                type: number
    responses:
      201:
        description: Registro criado e comando publicado via MQTT
      400:
        description: Dados inválidos
      401:
        description: Não autorizado
    """
    if BLOQUEAR_NOVAS_OPERACOES:
        return jsonify({"detail": "Criacao de operacoes desativada"}), 403

    body = request.get_json() or {}
    comando_bruto = str(body.get("comando_bruto", "")).strip().lower()

    # Bloqueia criação automática para evitar crescimento contínuo da lista no dashboard.
    comandos_bloqueados = {"snapshot", "auto:snapshot", "/z reset", "z reset", "reset"}
    if (
        comando_bruto.startswith("auto:")
        or comando_bruto in comandos_bloqueados
        or "snapshot" in comando_bruto
    ):
        return jsonify({"detail": "Registro automatico ignorado"}), 202

    dados = MovimentacaoZCreate(**body)

    # Verifica se o ESP está online antes de enviar
    hb = sistema_repo.get_heartbeat_modulo("motor", dados.bomba_id)
    if not hb or not hb["online"]:
        return jsonify({
            "detail": f"ESP motor/{dados.bomba_id} está offline. Comando não enviado."
        }), 503

    # Restrição: descida não pode ultrapassar o comprimento da corda
    if float(dados.deslocamento_solicitado_cm) > 0:
        bomba = bomba_repo.buscar_por_id(dados.bomba_id)
        if bomba and bomba.get("comprimento_corda_cm"):
            corda_cm = float(bomba["comprimento_corda_cm"])
            posicao_projetada = float(dados.posicao_inicial_cm) + float(dados.deslocamento_solicitado_cm)
            if posicao_projetada > corda_cm:
                restante = max(0, corda_cm - float(dados.posicao_inicial_cm))
                return jsonify({
                    "detail": (
                        f"Descida bloqueada: a posição projetada ({posicao_projetada:.1f} cm) "
                        f"ultrapassa o comprimento da corda ({corda_cm:.1f} cm). "
                        f"Máximo permitido a partir daqui: {restante:.1f} cm."
                    )
                }), 422

        # Intertravamento: bloqueia DESCIDA se a balsa está em movimento
        if movimentacao_xy_repo.tem_em_andamento(dados.bomba_id):
            return jsonify({
                "detail": "Descida bloqueada: a balsa está em movimento. "
                           "Pare a balsa (/balsa stop) antes de descer a motobomba."
            }), 403

    registro = movimentacao_z_repo.criar(dados)

    # Publica comando no MQTT para o ESP
    topico = f"motor/{dados.bomba_id}/comando"
    mqtt_service.publicar(topico, {
        "voltas": float(dados.voltas_mqtt),
        "operador_id": dados.operador_id,
        "comando_bruto": dados.comando_bruto,
        "posicao_inicial_cm": float(dados.posicao_inicial_cm),
        "deslocamento_solicitado_cm": float(dados.deslocamento_solicitado_cm),
    })

    return jsonify(registro), 201


@bp.route("/<int:registro_id>", methods=["PATCH"])
@jwt_required()
def atualizar_registro(registro_id):
    """
    Atualizar Registro de Movimentação Z
    ---
    tags:
      - Movimentação Z
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
              posicao_final_cm:
                type: number
              concluido_em:
                type: string
                format: date-time
    responses:
      200:
        description: Registro atualizado com sucesso
      401:
        description: Não autorizado
      404:
        description: Registro não encontrado
    """
    body = request.get_json()
    dados = MovimentacaoZUpdate(**body)
    registro = movimentacao_z_repo.atualizar(registro_id, dados)

    if not registro:
        return jsonify({"detail": "Registro nao encontrado"}), 404
    return jsonify(registro)


@bp.route("/bomba/<int:bomba_id>", methods=["GET"])
@jwt_required()
def listar_por_bomba(bomba_id):
    """
    Listar Movimentações Z por Bomba
    ---
    tags:
      - Movimentação Z
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
    registros = movimentacao_z_repo.listar_por_bomba(bomba_id, limite)
    return jsonify(registros)


@bp.route("/fechar-orfaos/<int:bomba_id>", methods=["PATCH"])
@jwt_required()
def fechar_orfaos(bomba_id):
    """
    Fechar Registros Órfãos (Em Andamento)
    ---
    tags:
      - Movimentação Z
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
    ids = movimentacao_z_repo.fechar_orfaos(bomba_id)
    return jsonify({"fechados": ids, "total": len(ids)})


@bp.route("/posicao/<int:bomba_id>", methods=["GET"])
@jwt_required()
def recuperar_posicao(bomba_id):
    """
    Recuperar Última Posição Z
    ---
    tags:
      - Movimentação Z
    parameters:
      - name: bomba_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Última posição conhecida
        content:
          application/json:
            schema:
              type: object
              properties:
                posicao_cm:
                  type: number
                status:
                  type: string
                timestamp_fim:
                  type: string
                  format: date-time
      401:
        description: Não autorizado
    """
    posicao = movimentacao_z_repo.recuperar_posicao(bomba_id)
    em_andamento = movimentacao_z_repo.tem_movimento_em_andamento(bomba_id)
    bomba = bomba_repo.buscar_por_id(bomba_id)
    corda_cm = float(bomba["comprimento_corda_cm"]) if bomba and bomba.get("comprimento_corda_cm") else None

    if not posicao:
        return jsonify({
            "posicao_cm": 0.0,
            "status": None,
            "timestamp_fim": None,
            "em_andamento": em_andamento,
            "comprimento_corda_cm": corda_cm,
        })
    return jsonify({
        "posicao_cm": float(posicao["posicao_final_cm"]),
        "status": posicao["status"],
        "timestamp_fim": posicao["timestamp_fim"],
        "em_andamento": em_andamento,
        "comprimento_corda_cm": corda_cm,
    })

