import requests
import math
import time
import re
import argparse
import getpass

API_URL = "http://localhost:5000"

posicao_atual_cm = 0.0
motor_ocupado = False

TOKEN    = None
USUARIO_ID = None
USUARIO_NOME = None
BOMBA_ID = None

DIAMETRO_CARRETEL_CM = None
COMPRIMENTO_CORDA_CM = None


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
    resp = requests.patch(f"{API_URL}/movimentacao-z/fechar-orfaos/{BOMBA_ID}", headers=api_headers())
    if resp.status_code == 200:
        return resp.json()
    return {"fechados": [], "total": 0}


def api_recuperar_posicao():
    resp = requests.get(f"{API_URL}/movimentacao-z/posicao/{BOMBA_ID}", headers=api_headers())
    if resp.status_code == 200:
        return resp.json()
    return None


def api_criar_registro(comando_bruto, posicao_inicial, deslocamento, voltas):
    """POST cria registro no DB E publica MQTT via backend."""
    resp = requests.post(f"{API_URL}/movimentacao-z/", headers=api_headers(), json={
        "bomba_id": BOMBA_ID,
        "operador_id": USUARIO_ID,
        "comando_bruto": comando_bruto,
        "posicao_inicial_cm": posicao_inicial,
        "deslocamento_solicitado_cm": deslocamento,
        "voltas_mqtt": voltas,
    })
    if resp.status_code == 201:
        r = resp.json()
        print(f"[API] Registro #{r['id']} criado + comando MQTT enviado")
        return r["id"]
    else:
        print(f"[API ERRO] {resp.text}")
        return None


def api_atualizar_registro(registro_id, status, desl_real=None, pos_final=None):
    if registro_id is None:
        return
    body = {"status": status}
    if desl_real is not None:
        body["deslocamento_real_cm"] = desl_real
    if pos_final is not None:
        body["posicao_final_cm"] = pos_final
    requests.patch(f"{API_URL}/movimentacao-z/{registro_id}", headers=api_headers(), json=body)


def api_consultar_status(registro_id):
    """Consulta status de um registro (para saber quando motor terminou)."""
    resp = requests.get(f"{API_URL}/movimentacao-z/bomba/{BOMBA_ID}?limite=1", headers=api_headers())
    if resp.status_code == 200:
        regs = resp.json()
        for r in regs:
            if r["id"] == registro_id:
                return r
    return None


def api_historico(limite=10):
    resp = requests.get(f"{API_URL}/movimentacao-z/bomba/{BOMBA_ID}?limite={limite}", headers=api_headers())
    if resp.status_code == 200:
        return resp.json()
    return []


# === CALCULOS ===

def calcular_voltas(distancia_cm):
    return distancia_cm / (DIAMETRO_CARRETEL_CM * math.pi)

def calcular_cm(voltas):
    return voltas * (DIAMETRO_CARRETEL_CM * math.pi)


# === COMANDOS ===

def cmd_historico(args):
    limite = int(args[0]) if args and args[0].isdigit() else 10
    rows = api_historico(limite)
    if not rows:
        print("[API] Nenhum registro encontrado.")
        return
    print(f"\n{'ID':<5} {'Comando':<22} {'Ini':>6} {'Sol':>7} {'Real':>7} {'Status':<14} {'Operador'}")
    print("-" * 78)
    for r in rows:
        d_real = f"{float(r['deslocamento_real_cm']):.2f}" if r.get("deslocamento_real_cm") else "---"
        ts = str(r.get("timestamp_inicio", ""))[:16].replace("T", " ")
        print(f"{r['id']:<5} {r['comando_bruto']:<22} {float(r['posicao_inicial_cm']):>6.2f} {float(r['deslocamento_solicitado_cm']):>7.2f} {d_real:>7} {r['status']:<14} {r.get('operador_nome', '?')} ({ts})")
    print()


def cmd_info():
    bomba = api_carregar_bomba(BOMBA_ID)
    if not bomba:
        print(f"[API] Bomba #{BOMBA_ID} nao encontrada.")
        return
    print(f"\nBomba #{BOMBA_ID}: {bomba['nome']}")
    print(f"  Localizacao:       {bomba.get('localizacao') or 'N/A'}")
    print(f"  Diametro carretel: {bomba['diametro_carretel_cm']} cm")
    print(f"  Comprimento corda: {bomba['comprimento_corda_cm']} cm")
    print(f"  Operacoes Z:       {bomba.get('total_operacoes_z', 0)}")
    print(f"  Operacoes XY:      {bomba.get('total_operacoes_xy', 0)}\n")


# === AGUARDAR MOTOR ===

def aguardar_motor(registro_id):
    """Faz polling no backend para saber quando o motor terminou."""
    print("[INFO] Aguardando motor... (Ctrl+C para EMERGENCIA)")
    while True:
        try:
            time.sleep(1)
            reg = api_consultar_status(registro_id)
            if reg and reg["status"] != "EM_ANDAMENTO":
                return reg
        except KeyboardInterrupt:
            print("\n[!!!] Motor ainda em andamento. Use movZ reset se necessario.")
            return None


# === MAIN ===

def main():
    global posicao_atual_cm, motor_ocupado
    global TOKEN, USUARIO_ID, USUARIO_NOME
    global BOMBA_ID
    global DIAMETRO_CARRETEL_CM, COMPRIMENTO_CORDA_CM

    parser = argparse.ArgumentParser(description="CLI Motor - Modulo 1-A")
    parser.add_argument("--bomba", type=int, help="ID da bomba")
    args = parser.parse_args()
    BOMBA_ID = args.bomba

    if BOMBA_ID is None:
        try:
            BOMBA_ID = int(input("ID da bomba: ").strip())
        except (ValueError, KeyboardInterrupt):
            print("[ERRO] ID invalido.")
            return

    # --- Login via API ---
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

    DIAMETRO_CARRETEL_CM = float(bomba["diametro_carretel_cm"])
    COMPRIMENTO_CORDA_CM = float(bomba["comprimento_corda_cm"])

    # --- Fechar orfaos e recuperar posicao ---
    orfaos = api_fechar_orfaos()
    if orfaos["total"] > 0:
        print(f"[API] {orfaos['total']} operacao(oes) interrompida(s): {orfaos['fechados']}")

    estado = api_recuperar_posicao()
    if estado and estado.get("posicao_cm") is not None and estado.get("status") is not None:
        posicao_atual_cm = estado["posicao_cm"]
        print(f"[API] Posicao recuperada: {posicao_atual_cm:.2f} cm (ultima: {estado['status']})")
    else:
        posicao_atual_cm = 0.0
        print("[API] Primeira sessao. Posicao: 0.00 cm")

    print(f"\n=== CLI Motor | Bomba #{BOMBA_ID}: {bomba['nome']} ({bomba.get('localizacao', 'N/A')}) ===")
    print("Comandos de movimento:")
    print("  movZ descer(20)    -> Solta 20cm de corda")
    print("  movZ subir(15.5)   -> Puxa 15.5cm de corda")
    print("  movZ status        -> Posicao atual da corda")
    print("  movZ reset         -> Recolhe toda a corda")
    print("Consultas:")
    print("  db historico [N]   -> Ultimos N registros (padrao 10)")
    print("  db info            -> Info da bomba")
    print("  sair               -> Encerrar\n")

    while True:
        try:
            comando = input(">> ").strip()
        except KeyboardInterrupt:
            print("\nEncerrado.")
            break

        if not comando:
            continue

        cmd_lower = comando.lower()

        if cmd_lower == "sair":
            break

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

        match = re.match(r'^movz\s+([a-z]+)(?:\(([-\d.]+)\))?$', cmd_lower)
        if not match:
            print("[ERRO] Sintaxe invalida! Ex: 'movZ descer(10)', 'db historico'")
            continue

        acao = match.group(1)
        valor_str = match.group(2)

        if acao == "status":
            print(f"[STATUS] Posicao atual: {posicao_atual_cm:.2f} cm")
            continue

        if acao == "reset":
            if posicao_atual_cm == 0.0:
                print("[INFO] Corda ja totalmente recolhida.")
                continue
            movimento_cm = -posicao_atual_cm

        elif acao in ["subir", "descer"]:
            if not valor_str:
                print(f"[ERRO] Informe o valor. Ex: movZ {acao}(15)")
                continue
            try:
                movimento_cm = float(valor_str)
                if movimento_cm < 0:
                    movimento_cm = abs(movimento_cm)
                if acao == "subir":
                    movimento_cm = -movimento_cm
            except ValueError:
                print("[ERRO] Valor invalido.")
                continue
        else:
            print(f"[ERRO] Acao desconhecida: '{acao}'")
            continue

        nova_posicao = posicao_atual_cm + movimento_cm

        if nova_posicao < 0.0:
            print(f"[ERRO] Limite inferior! Maximo a recolher: {posicao_atual_cm:.2f} cm")
            continue
        if nova_posicao > COMPRIMENTO_CORDA_CM:
            print(f"[ERRO] Limite maximo! Maximo a soltar: {COMPRIMENTO_CORDA_CM - posicao_atual_cm:.2f} cm")
            continue

        voltas = calcular_voltas(movimento_cm)

        # Envia para o backend (que salva no DB + publica MQTT)
        reg_id = api_criar_registro(comando, posicao_atual_cm, movimento_cm, round(voltas, 4))

        if reg_id:
            posicao_atual_cm = nova_posicao
            print(f"[OK] {acao} | {voltas:+.4f} voltas | Posicao esperada: {posicao_atual_cm:.2f} cm")

            # Polling para aguardar resposta do motor (via backend)
            result = aguardar_motor(reg_id)
            if result:
                status = result["status"]
                if status == "CONCLUIDO":
                    posicao_atual_cm = float(result.get("posicao_final_cm", posicao_atual_cm))
                    print(f"[INFO] Motor CONCLUIDO! Posicao: {posicao_atual_cm:.2f} cm")
                elif status == "ABORTADO":
                    posicao_atual_cm = float(result.get("posicao_final_cm", posicao_atual_cm))
                    desl = result.get("deslocamento_real_cm")
                    print(f"[AVISO] Motor ABORTADO! Real: {desl} cm | Posicao: {posicao_atual_cm:.2f} cm")

    print("Encerrado.")


if __name__ == "__main__":
    main()
