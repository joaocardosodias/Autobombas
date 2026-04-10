"""
auto_mode_service.py
Serviço de controle automático da bomba no eixo Z.

Lógica:
  - Lê a última leitura de corrente do DB a cada ciclo
  - Se corrente > limite_corrente → sobe PASSO_CM
  - Se corrente < limite_corrente * HISTERESE e há espaço → desce PASSO_CM
  - Aguarda o motor Z concluir antes do próximo passo
  - Para automaticamente se o ESP motor estiver offline (heartbeat)
"""
import math
import threading
import time

from backend.repositories import leitura_corrente_repo, movimentacao_z_repo, bomba_repo
from backend.services import mqtt_service

# ── Configurações ──────────────────────────────────────────────────────────
INTERVALO_S = 2.0         # segundos entre verificações
TIMEOUT_MOTOR_S = 60.0    # tempo máximo aguardando motor concluir

# ── Estado em memória (por bomba) ──────────────────────────────────────────
_estados: dict[int, dict] = {}
_lock = threading.Lock()


# ── API Pública ────────────────────────────────────────────────────────────

def ligar(bomba_id: int, operador_id: int) -> dict:
    """
    Ativa o modo automático para a bomba.
    Retorna erro se já estiver ativo ou se dados da bomba forem inválidos.
    """
    with _lock:
        if _estados.get(bomba_id, {}).get("ativo"):
            return {"ok": False, "detail": "Modo automático já está ativo."}

    bomba = bomba_repo.buscar_por_id(bomba_id)
    if not bomba:
        return {"ok": False, "detail": "Bomba não encontrada."}
    if not bomba.get("limite_superior"):
        return {"ok": False, "detail": "Bomba sem limite_superior configurado. Configure antes de usar o modo auto."}
    if not bomba.get("limite_inferior"):
        return {"ok": False, "detail": "Bomba sem limite_inferior configurado. Configure antes de usar o modo auto."}
    if float(bomba["limite_inferior"]) >= float(bomba["limite_superior"]):
        return {"ok": False, "detail": "limite_inferior deve ser menor que limite_superior."}

    # Verifica todos os ESPs essenciais e coleta os problemas juntos
    hb_lista = mqtt_service.get_heartbeat_status()
    motor_online   = any(m["modulo"] == f"motor/{bomba_id}"    and m["online"] for m in hb_lista)
    sensor_online  = any(m["modulo"] == f"corrente/{bomba_id}" and m["online"] for m in hb_lista)

    bloqueios = []
    if not motor_online:
        bloqueios.append(f"motor/{bomba_id}:offline")
    if not sensor_online:
        bloqueios.append(f"corrente/{bomba_id}:offline")

    if bloqueios:
        return {"ok": False, "detail": "ESPs offline", "bloqueios": bloqueios}

    passo = float(bomba.get("passo_auto_cm") or 2.0)
    limite_inf = float(bomba["limite_inferior"])
    limite_sup = float(bomba["limite_superior"])
    max_cm = float(bomba["comprimento_corda_cm"])

    # Recupera posição atual
    pos_reg = movimentacao_z_repo.recuperar_posicao(bomba_id)
    posicao_cm = float(pos_reg["posicao_final_cm"]) if pos_reg else 0.0

    with _lock:
        _estados[bomba_id] = {
            "ativo": True,
            "posicao_cm": posicao_cm,
            "limite_inf": limite_inf,
            "limite_sup": limite_sup,
            "passo_cm": passo,
            "max_cm": max_cm,
            "operador_id": operador_id,
            "diametro_carretel_cm": float(bomba["diametro_carretel_cm"]),
            "fase": "INICIANDO",
            "ultimo_erro": None,
            "ciclos": 0,
        }

    t = threading.Thread(target=_loop, args=(bomba_id,), daemon=True)
    t.start()
    return {
        "ok": True,
        "posicao_inicial_cm": posicao_cm,
        "limite_inferior": limite_inf,
        "limite_superior": limite_sup,
        "passo_cm": passo,
    }


def desligar(bomba_id: int) -> dict:
    """Desativa o modo automático (o motor termina o passo atual normalmente)."""
    with _lock:
        st = _estados.get(bomba_id)
        if not st or not st["ativo"]:
            return {"ok": False, "detail": "Modo automático não está ativo."}
        st["ativo"] = False
    return {"ok": True}


def get_status(bomba_id: int) -> dict:
    """Retorna o estado atual do modo automático para a bomba."""
    with _lock:
        st = _estados.get(bomba_id)
    if not st:
        return {"ativo": False, "bomba_id": bomba_id}
    return {
        "ativo": st["ativo"],
        "bomba_id": bomba_id,
        "fase": st["fase"],
        "posicao_cm": st["posicao_cm"],
        "limite_inferior": st["limite_inf"],
        "limite_superior": st["limite_sup"],
        "passo_cm": st["passo_cm"],
        "ciclos": st["ciclos"],
        "ultimo_erro": st["ultimo_erro"],
    }


# ── Loop de controle ───────────────────────────────────────────────────────

def _loop(bomba_id: int):
    print(f"[AUTO] Modo automático INICIADO para bomba #{bomba_id}")

    while True:
        time.sleep(INTERVALO_S)

        with _lock:
            st = _estados.get(bomba_id)
            if not st or not st["ativo"]:
                break

        try:
            _ciclo(bomba_id, st)
        except Exception as e:
            with _lock:
                st["ultimo_erro"] = str(e)
                st["fase"] = "ERRO"
            print(f"[AUTO] Erro no ciclo da bomba #{bomba_id}: {e}")

    with _lock:
        if bomba_id in _estados:
            _estados[bomba_id]["fase"] = "PARADO"

    # Salva a posição final no DB para que /z status reflita corretamente
    with _lock:
        st = _estados.get(bomba_id, {})
        posicao_final = st.get("posicao_cm", 0.0)
        operador_id   = st.get("operador_id", 1)
    try:
        movimentacao_z_repo.salvar_posicao_final(bomba_id, posicao_final, operador_id)
        print(f"[AUTO] Posição final gravada: {posicao_final:.2f} cm")
    except Exception as e:
        print(f"[AUTO] Erro ao gravar posição final: {e}")

    print(f"[AUTO] Modo automático ENCERRADO para bomba #{bomba_id}")


def _ciclo(bomba_id: int, st: dict):
    # 1. Verifica heartbeat do motor
    hb_lista = mqtt_service.get_heartbeat_status()
    motor_online = any(
        m["modulo"] == f"motor/{bomba_id}" and m["online"]
        for m in hb_lista
    )
    if not motor_online:
        with _lock:
            st["fase"] = "MOTOR_OFFLINE"
        print(f"[AUTO] motor/{bomba_id} offline — aguardando...")
        return

    # 1b. Verifica heartbeat do sensor de corrente
    sensor_online = any(
        m["modulo"] == f"corrente/{bomba_id}" and m["online"]
        for m in hb_lista
    )
    if not sensor_online:
        with _lock:
            st["fase"] = "SENSOR_OFFLINE"
        print(f"[AUTO] corrente/{bomba_id} offline — aguardando...")
        return

    # 2. Lê corrente mais recente
    leitura = leitura_corrente_repo.ultima_leitura(bomba_id)
    if not leitura:
        with _lock:
            st["fase"] = "SEM_LEITURA"
        return

    corrente = float(leitura["corrente_a"])
    limite_inf = st["limite_inf"]
    limite_sup = st["limite_sup"]
    passo = st["passo_cm"]

    # 3. Decide direção com banda de corrente
    # Convenção: delta_cm positivo = descer (soltar corda = posição aumenta)
    #            delta_cm negativo = subir (recolher corda = posição diminui)
    if corrente > limite_sup:
        # Acima do limite superior → SUBIDA COMPLETA sem passo
        if st["posicao_cm"] <= 0.0:
            with _lock:
                st["fase"] = "LIMITE_MINIMO"
            return
        delta_cm     = -st["posicao_cm"]
        acao         = "auto:subindo"
        nova_posicao = 0.0
        subida_plena = True
        print(f"[AUTO] Corrente {corrente:.4f}A > sup {limite_sup}A — SUBINDO")
    elif corrente < limite_inf and st["posicao_cm"] < st["max_cm"]:
        # Abaixo do limite inferior e tem espaço → descer por passo
        delta_cm     = passo
        acao         = "auto:descendo"
        nova_posicao = min(st["max_cm"], st["posicao_cm"] + passo)
        subida_plena = False
        print(f"[AUTO] Corrente {corrente:.4f}A < inf {limite_inf}A — DESCENDO")
    else:
        with _lock:
            st["fase"] = "ESTAVEL"
        return

    voltas = _cm_para_voltas(delta_cm, st["diametro_carretel_cm"])

    # 4. Publica comando MQTT para o motor Z
    topico = f"motor/{bomba_id}/comando"
    mqtt_service.publicar(topico, {
        "voltas": round(voltas, 4),
        "operador_id": st["operador_id"],
    })

    # Registra no BD
    from backend.models.movimentacao_z import MovimentacaoZCreate
    reg = movimentacao_z_repo.criar(MovimentacaoZCreate(
        bomba_id=bomba_id,
        operador_id=st["operador_id"],
        comando_bruto=acao,
        posicao_inicial_cm=st["posicao_cm"],
        deslocamento_solicitado_cm=delta_cm,
        voltas_mqtt=round(voltas, 4),
    ))

    fase = "DESCENDO" if delta_cm > 0 else "SUBINDO"
    with _lock:
        st["fase"] = fase
        st["ciclos"] += 1

    print(
        f"[AUTO] {'DESCENDO' if not subida_plena else 'SUBINDO'} "
        f"| corrente={corrente:.4f}A banda=[{limite_inf},{limite_sup}]A "
        f"| {st['posicao_cm']:.2f}cm → {nova_posicao:.2f}cm"
    )

    if subida_plena:
        # Subida: monitora corrente e aborta motor quando seguro
        posicao_real = _aguardar_ou_abortar_subida(bomba_id, reg["id"], st)
        with _lock:
            st["posicao_cm"] = posicao_real
    else:
        # Descida: aguarda conclusão normal
        _aguardar_conclusao(bomba_id, reg["id"], st, nova_posicao)
        with _lock:
            st["posicao_cm"] = nova_posicao


def _aguardar_conclusao(bomba_id: int, reg_id: int, st: dict, nova_posicao_cm: float):
    """Bloqueia o ciclo até o registro Z não estar mais EM_ANDAMENTO."""
    inicio = time.time()
    while True:
        time.sleep(1)
        with _lock:
            if not st["ativo"]:
                return
        regs = movimentacao_z_repo.listar_por_bomba(bomba_id, limite=10)
        for r in regs:
            if r["id"] == reg_id and r["status"] != "EM_ANDAMENTO":
                return
        if time.time() - inicio > TIMEOUT_MOTOR_S:
            print(f"[AUTO] Timeout aguardando motor (reg #{reg_id}) — forces posicao={nova_posicao_cm:.2f}cm")
            # Fecha o registro travado e grava snapshot de posição
            with _lock:
                operador_id = st.get("operador_id", 1)
            try:
                movimentacao_z_repo.salvar_posicao_final(bomba_id, nova_posicao_cm, operador_id)
            except Exception as e:
                print(f"[AUTO] Erro ao salvar posição no timeout: {e}")
            return


def _aguardar_ou_abortar_subida(bomba_id: int, reg_id: int, st: dict) -> float:
    """
    Durante a subida (emergencial), monitora a corrente a cada segundo.
    Quando a corrente cair abaixo do limite, envia EMERGENCIA para parar o motor.
    Retorna a posição real estimada após a parada.
    """
    inicio = time.time()
    pos_inicio = st["posicao_cm"]
    limite = st["limite"]
    diametro = st["diametro_carretel_cm"]
    abortado = False

    while True:
        time.sleep(1)
        with _lock:
            if not st["ativo"]:
                break

        # Verifica se motor já terminou naturalmente
        regs = movimentacao_z_repo.listar_por_bomba(bomba_id, limite=5)
        motor_concluido = any(r["id"] == reg_id and r["status"] != "EM_ANDAMENTO" for r in regs)
        if motor_concluido:
            print(f"[AUTO] Subida concluída naturalmente (pos 0).")
            return 0.0

        # Lê corrente atual
        leitura = leitura_corrente_repo.ultima_leitura(bomba_id)
        if leitura:
            corrente_atual = float(leitura["corrente_a"])
            print(f"[AUTO] SUBINDO | corrente={corrente_atual:.6f}A limite={limite}A")

            if corrente_atual <= limite:
                # Corrente segura → abortar motor agora
                mqtt_service.publicar_raw(f"motor/{bomba_id}/comando", "EMERGENCIA")
                abortado = True
                print(f"[AUTO] Corrente segura ({corrente_atual:.6f}A ≤ {limite}A) — EMERGENCIA enviada")
                break

        if time.time() - inicio > TIMEOUT_MOTOR_S:
            print(f"[AUTO] Timeout na subida (reg #{reg_id})")
            mqtt_service.publicar_raw(f"motor/{bomba_id}/comando", "EMERGENCIA")
            abortado = True
            break

    if abortado:
        # Aguarda o motor confirmar o abort e atualizar o DB
        for _ in range(10):
            time.sleep(1)
            regs = movimentacao_z_repo.listar_por_bomba(bomba_id, limite=5)
            for r in regs:
                if r["id"] == reg_id and r["status"] != "EM_ANDAMENTO":
                    posicao_real = r.get("posicao_final_cm")
                    if posicao_real is not None:
                        return float(posicao_real)

    # Fallback: estima pela distância percorrida no tempo
    tempo = time.time() - inicio
    voltas_estimadas = (tempo / 60.0) * 5  # estimativa grosseira
    cm_estimados = voltas_estimadas * diametro * math.pi
    return max(0.0, pos_inicio - cm_estimados)


def _cm_para_voltas(delta_cm: float, diametro_cm: float) -> float:
    """Converte cm de deslocamento em número de voltas do carretel."""
    circunferencia = diametro_cm * math.pi
    return delta_cm / circunferencia
