import requests
import time
import argparse
import getpass

API_URL = "http://localhost:5000"

motor_status = "PARADO"
sistema_ligado = False
registro_ativo_id = None
ts_movimento_inicio = None

TOKEN    = None
USUARIO_ID = None
USUARIO_NOME = None
BOMBA_ID = None


# === API ===

def api_headers():
    return {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def api_login():
    print("\n=== Login ===")
    email = input("Email: ").strip()
    senha = getpass.getpass("Senha: ")
    try:
        resp = requests.post(f"{API_URL}/auth/login", json={"email": email, "senha": senha})
    except requests.ConnectionError:
        print("[ERRO] Backend indisponivel. Rode: python3 backend/main.py")
        return None
    if resp.status_code != 200:
        print(f"[ERRO] {resp.json().get('detail', 'Falha no login')}")
        return None
    return resp.json()


def api_carregar_bomba(bomba_id):
    resp = requests.get(f"{API_URL}/bombas/{bomba_id}", headers=api_headers())
    if resp.status_code != 200:
        return None
    return resp.json()


def api_fechar_orfaos():
    resp = requests.patch(f"{API_URL}/movimentacao-xy/fechar-orfaos/{BOMBA_ID}", headers=api_headers())
    if resp.status_code == 200:
        return resp.json()
    return {"fechados": [], "total": 0}


def api_criar_movimento(direcao):
    """POST cria registro no DB E publica MQTT via backend."""
    global registro_ativo_id, ts_movimento_inicio
    resp = requests.post(f"{API_URL}/movimentacao-xy/", headers=api_headers(), json={
        "bomba_id": BOMBA_ID,
        "operador_id": USUARIO_ID,
        "direcao": direcao,
    })
    if resp.status_code == 201:
        r = resp.json()
        registro_ativo_id = r["id"]
        ts_movimento_inicio = time.time()
        print(f"[API] Registro #{registro_ativo_id} criado + comando MQTT enviado")
    else:
        print(f"[API ERRO] {resp.text}")


def api_finalizar_movimento(status="CONCLUIDO"):
    global registro_ativo_id, ts_movimento_inicio
    if registro_ativo_id is None:
        return
    duracao_ms = None
    if ts_movimento_inicio:
        duracao_ms = int((time.time() - ts_movimento_inicio) * 1000)
    requests.patch(f"{API_URL}/movimentacao-xy/{registro_ativo_id}", headers=api_headers(), json={
        "status": status,
        "duracao_ms": duracao_ms,
    })
    print(f"[API] Registro #{registro_ativo_id} -> {status} ({duracao_ms}ms)")
    registro_ativo_id = None
    ts_movimento_inicio = None


def api_enviar_comando(acao):
    """Envia comando genérico (ligar/desligar/parar) via backend → MQTT."""
    requests.post(f"{API_URL}/movimentacao-xy/comando/{BOMBA_ID}", headers=api_headers(), json={
        "acao": acao,
        "operador_id": USUARIO_ID,
    })


def api_historico(limite=10):
    resp = requests.get(f"{API_URL}/movimentacao-xy/bomba/{BOMBA_ID}?limite={limite}", headers=api_headers())
    if resp.status_code == 200:
        return resp.json()
    return []


def api_get_limiares():
    resp = requests.get(f"{API_URL}/leituras-distancia/limiares", headers=api_headers())
    if resp.status_code == 200:
        return resp.json()
    return None


def api_set_limiares(dist_info, dist_alerta, dist_critico):
    return requests.put(f"{API_URL}/leituras-distancia/limiares", headers=api_headers(), json={
        "dist_info_m": dist_info,
        "dist_alerta_m": dist_alerta,
        "dist_critico_m": dist_critico,
    })


def api_status_proximidade():
    resp = requests.get(
        f"{API_URL}/leituras-distancia/bomba/{BOMBA_ID}/status-proximidade",
        headers=api_headers(),
    )
    if resp.status_code == 200:
        return resp.json()
    return None


# === COMANDOS ===

def cmd_historico(args):
    limite = int(args[0]) if args and args[0].isdigit() else 10
    rows = api_historico(limite)
    if not rows:
        print("[API] Nenhum registro encontrado.")
        return
    print(f"\n{'ID':<5} {'Direcao':<12} {'Duracao':>9} {'Status':<14} {'Operador':<16} {'Inicio'}")
    print("-" * 75)
    for r in rows:
        dur = f"{r['duracao_ms']}ms" if r.get("duracao_ms") else "---"
        ts = str(r.get("timestamp_inicio", ""))[:16].replace("T", " ")
        print(f"{r['id']:<5} {r['direcao']:<12} {dur:>9} {r['status']:<14} {r.get('operador_nome', '?'):<16} {ts}")
    print()


def cmd_info():
    bomba = api_carregar_bomba(BOMBA_ID)
    if not bomba:
        print(f"[API] Bomba #{BOMBA_ID} nao encontrada.")
        return
    print(f"\nBomba #{BOMBA_ID}: {bomba['nome']}")
    print(f"  Localizacao:     {bomba.get('localizacao') or 'N/A'}")
    print(f"  Operacoes XY:    {bomba.get('total_operacoes_xy', 0)}\n")


def cmd_sensores():
    status = api_status_proximidade()
    if not status:
        print("[ERRO] Nao foi possivel obter o status dos sensores.")
        return
    if not status.get("disponivel"):
        print(f"  {status.get('mensagem', 'Sem dados')}")
        return

    ts = str(status.get("timestamp_leitura", ""))[:19].replace("T", " ")
    print(f"\n[Sensores de proximidade | {ts}]")

    cores = {"SEGURO": "\033[92m", "INFORMATIVO": "\033[94m", "ALERTA": "\033[93m", "CRITICO": "\033[91m"}
    reset = "\033[0m"

    for direcao, info in status["direcoes"].items():
        cor = cores.get(info["nivel"], "")
        print(f"  {direcao:<10}  {info['distancia_m']:>5.2f} m  {cor}{info['nivel']}{reset}")

    bloq = status.get("direcoes_bloqueadas", [])
    alerta = status.get("direcoes_alerta", [])
    if bloq:
        print(f"\n  \033[91mDirecoes BLOQUEADAS: {', '.join(bloq)}\033[0m")
    if alerta:
        print(f"  \033[93mDirecoes em ALERTA:  {', '.join(alerta)}\033[0m")
    print()


def cmd_limiares(args):
    if not args:
        lim = api_get_limiares()
        if not lim:
            print("[ERRO] Nao foi possivel obter os limiares.")
            return
        print(f"\nLimiares de risco atuais:")
        print(f"  INFORMATIVO:  d <= {lim['dist_info_m']} m")
        print(f"  ALERTA:       d <= {lim['dist_alerta_m']} m   (velocidade reduzida)")
        print(f"  CRITICO:      d <= {lim['dist_critico_m']} m   (movimento bloqueado)")
        print(f"\n  Para alterar: sensor limiares <info> <alerta> <critico>")
        print(f"  Exemplo:      sensor limiares 2.0 1.0 0.5\n")
        return

    if len(args) != 3:
        print("[ERRO] Uso: sensor limiares <dist_info> <dist_alerta> <dist_critico>")
        return

    try:
        dist_info = float(args[0])
        dist_alerta = float(args[1])
        dist_critico = float(args[2])
    except ValueError:
        print("[ERRO] Todos os valores devem ser numericos.")
        return

    resp = api_set_limiares(dist_info, dist_alerta, dist_critico)
    if resp.status_code == 200:
        novo = resp.json()
        print(f"[OK] Limiares atualizados: info={novo['dist_info_m']}  "
              f"alerta={novo['dist_alerta_m']}  critico={novo['dist_critico_m']}")
    else:
        detail = resp.json().get("detail", "Erro desconhecido")
        print(f"[ERRO] {detail}")


# === MAIN ===

def main():
    global motor_status, sistema_ligado, registro_ativo_id
    global TOKEN, USUARIO_ID, USUARIO_NOME, BOMBA_ID

    parser = argparse.ArgumentParser(description="CLI Balsa - Modulo 2-A")
    parser.add_argument("--bomba", type=int, help="ID da bomba")
    args = parser.parse_args()
    BOMBA_ID = args.bomba

    if BOMBA_ID is None:
        try:
            BOMBA_ID = int(input("ID da bomba: ").strip())
        except (ValueError, KeyboardInterrupt):
            print("[ERRO] ID invalido.")
            return

    # --- Login ---
    tentativas = 3
    login_data = None
    while tentativas > 0:
        login_data = api_login()
        if login_data:
            break
        tentativas -= 1
        if tentativas > 0:
            print(f"[AVISO] {tentativas} tentativa(s) restante(s).\n")

    if login_data is None:
        print("[ERRO] Acesso negado.")
        return

    TOKEN        = login_data["token"]
    USUARIO_ID   = login_data["usuario_id"]
    USUARIO_NOME = login_data["nome"]
    print(f"\nBem-vindo, {USUARIO_NOME} ({login_data['role']})!")

    # --- Carregar bomba ---
    bomba = api_carregar_bomba(BOMBA_ID)
    if not bomba:
        print(f"[ERRO] Bomba #{BOMBA_ID} nao encontrada.")
        return

    # --- Fechar orfaos ---
    orfaos = api_fechar_orfaos()
    if orfaos["total"] > 0:
        print(f"[API] {orfaos['total']} operacao(oes) interrompida(s): {orfaos['fechados']}")

    print(f"\n=== CLI Balsa (Modulo 2-A) | Bomba #{BOMBA_ID}: {bomba['nome']} ({bomba.get('localizacao', 'N/A')}) ===")
    print("Comandos de movimento (apenas com sistema ligado):")
    print("  movXY ligar           -> Liga o sistema")
    print("  movXY desligar        -> Desliga o sistema")
    print("  movXY esquerda        -> Move para esquerda")
    print("  movXY direita         -> Move para direita")
    print("  movXY parar           -> Para o motor")
    print("  movXY status          -> Status atual")
    print("Sensores (intertravamento 2-C):")
    print("  sensor status         -> Proximidade por direcao + bloqueios")
    print("  sensor limiares       -> Ver limiares de risco atuais")
    print("  sensor limiares I A C -> Alterar limiares (info alerta critico)")
    print("Consultas:")
    print("  db historico [N]      -> Ultimos N registros (padrao 10)")
    print("  db info               -> Info da bomba")
    print("  sair                  -> Encerrar\n")

    while True:
        try:
            comando = input(">> ").strip()
        except KeyboardInterrupt:
            if sistema_ligado and registro_ativo_id:
                api_enviar_comando("parar")
                api_finalizar_movimento("INTERROMPIDO")
            print("\nEncerrado.")
            break

        if not comando:
            continue

        cmd_lower = comando.lower()

        if cmd_lower == "sair":
            if sistema_ligado and registro_ativo_id:
                api_enviar_comando("parar")
                api_finalizar_movimento("INTERROMPIDO")
            break

        # Comandos sensor (intertravamento 2-C)
        if cmd_lower.startswith("sensor "):
            partes = cmd_lower.split()
            sub = partes[1] if len(partes) > 1 else ""
            sub_args = partes[2:] if len(partes) > 2 else []
            if sub == "status":
                cmd_sensores()
            elif sub == "limiares":
                cmd_limiares(sub_args)
            else:
                print(f"[ERRO] Subcomando desconhecido: '{sub}'. Use: sensor status | sensor limiares")
            continue

        # Comandos DB
        if cmd_lower.startswith("db "):
            partes = cmd_lower.split()
            sub = partes[1] if len(partes) > 1 else ""
            sub_args = partes[2:] if len(partes) > 2 else []
            if sub == "historico":
                cmd_historico(sub_args)
            elif sub == "info":
                cmd_info()
            else:
                print(f"[ERRO] Subcomando desconhecido: '{sub}'")
            continue

        # Comandos movXY
        if not cmd_lower.startswith("movxy "):
            print("[ERRO] Sintaxe invalida! Ex: 'movXY esquerda', 'db historico'")
            continue

        acao = cmd_lower.replace("movxy ", "").strip()

        if acao == "ligar":
            if sistema_ligado:
                print("[AVISO] Sistema ja ligado.")
            else:
                api_enviar_comando("ligar")
                sistema_ligado = True
                print("[OK] Sistema ligado.")

        elif acao == "desligar":
            if not sistema_ligado:
                print("[AVISO] Sistema ja desligado.")
            else:
                if registro_ativo_id:
                    api_enviar_comando("parar")
                    api_finalizar_movimento("CONCLUIDO")
                api_enviar_comando("desligar")
                sistema_ligado = False
                print("[OK] Sistema desligado.")

        elif acao == "status":
            estado = "LIGADO" if sistema_ligado else "DESLIGADO"
            print(f"[STATUS] Sistema: {estado} | Motor: {motor_status}")

        elif acao in ["esquerda", "direita"]:
            if not sistema_ligado:
                print("[ERRO] Ligue o sistema primeiro: movXY ligar")
                continue
            if registro_ativo_id:
                api_finalizar_movimento("CONCLUIDO")
            api_criar_movimento(acao)
            motor_status = "<< ESQUERDA" if acao == "esquerda" else "DIREITA >>"
            print(f"[OK] Motor movendo para {acao.upper()}")

        elif acao == "parar":
            if not sistema_ligado:
                print("[AVISO] Sistema desligado.")
                continue
            api_enviar_comando("parar")
            if registro_ativo_id:
                api_finalizar_movimento("CONCLUIDO")
            motor_status = "PARADO"
            print("[OK] Motor parado.")

        else:
            print(f"[ERRO] Acao desconhecida: '{acao}'. Tente: ligar, desligar, esquerda, direita, parar, status")

    print("Encerrado.")


if __name__ == "__main__":
    main()