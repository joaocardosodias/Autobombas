import requests
import time
import argparse
import getpass

API_URL = "http://localhost:5000"

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


def api_solicitar_leitura():
    """Pede ao backend que envie comando de leitura via MQTT pro ESP."""
    resp = requests.post(
        f"{API_URL}/leituras-corrente/solicitar/{BOMBA_ID}",
        headers=api_headers(),
        json={"operador_id": USUARIO_ID},
    )
    if resp.status_code == 200:
        print("[API] Comando de leitura enviado ao ESP via MQTT")
        return True
    print(f"[API ERRO] {resp.text}")
    return False


def api_ultima_leitura():
    resp = requests.get(f"{API_URL}/leituras-corrente/bomba/{BOMBA_ID}/ultima", headers=api_headers())
    if resp.status_code == 200:
        return resp.json()
    return None


def api_historico(limite=10):
    resp = requests.get(f"{API_URL}/leituras-corrente/bomba/{BOMBA_ID}?limite={limite}", headers=api_headers())
    if resp.status_code == 200:
        return resp.json()
    return []


def api_info_bomba():
    return api_carregar_bomba(BOMBA_ID)


# === CLASSIFICACAO ===

def classificar(percentual):
    if percentual < 70:
        return "BAIXA", "Predominancia de succao de liquido. Sugestao: descer a motobomba."
    elif percentual < 85:
        return "NORMAL", "Operacao estavel. Manter posicao atual."
    else:
        return "ELEVADA", "Alta concentracao de solidos. Manter posicao."


# === COMANDOS ===

def cmd_ler():
    """Apenas pega a ultima leitura do banco de dados, pois o ESP envia continuamente."""
    leitura = api_ultima_leitura()
    if not leitura:
        print("[API] Nenhuma leitura encontrada.")
        return

    ts = str(leitura.get("timestamp_leitura", ""))[:19].replace("T", " ")
    corrente = float(leitura["corrente_a"])
    percentual = float(leitura["percentual"])
    classif = leitura["classificacao"].upper()
    sugestao = leitura.get("sugestao", "")

    print(f"\n=== Leitura (#{leitura['id']}) ===")
    print(f"  Corrente:       {corrente:.6f} A")
    print(f"  Percentual:     {percentual:.2f}%")
    print(f"  Classificacao:  {classif}")
    print(f"  Sugestao:       {sugestao}")
    print(f"  Timestamp:      {ts}\n")


def cmd_historico(args):
    limite = int(args[0]) if args and args[0].isdigit() else 10
    rows = api_historico(limite)
    if not rows:
        print("[API] Nenhum registro encontrado.")
        return
    print(f"\n{'ID':<5} {'Corrente':>10} {'%':>7} {'Classif':<10} {'Operador':<16} {'Timestamp'}")
    print("-" * 70)
    for r in rows:
        ts = str(r.get("timestamp_leitura", ""))[:16].replace("T", " ")
        print(f"{r['id']:<5} {float(r['corrente_a']):>10.6f} {float(r['percentual']):>7.2f} {r['classificacao']:<10} {r.get('operador_nome', '?'):<16} {ts}")
    print()


def cmd_info():
    bomba = api_info_bomba()
    if not bomba:
        print(f"[API] Bomba #{BOMBA_ID} nao encontrada.")
        return
    print(f"\nBomba #{BOMBA_ID}: {bomba['nome']}")
    print(f"  Localizacao: {bomba.get('localizacao') or 'N/A'}\n")


# === MAIN ===

def main():
    global TOKEN, USUARIO_ID, USUARIO_NOME, BOMBA_ID

    parser = argparse.ArgumentParser(description="CLI Sensor de Corrente - Modulo 1-B")
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

    print(f"\n=== CLI Sensor de Corrente (Modulo 1-B) | Bomba #{BOMBA_ID}: {bomba['nome']} ===")
    print("Comandos:")
    print("  sensor ler            -> Solicita leitura ao ESP")
    print("  sensor ultima         -> Ultima leitura salva")
    print("  db historico [N]      -> Ultimos N registros (padrao 10)")
    print("  db info               -> Info da bomba")
    print("  sair                  -> Encerrar\n")

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

        # Comandos sensor
        if cmd_lower.startswith("sensor "):
            acao = cmd_lower.replace("sensor ", "").strip()

            if acao == "ler":
                cmd_ler()
            elif acao == "ultima":
                leitura = api_ultima_leitura()
                if not leitura:
                    print("[API] Nenhuma leitura encontrada.")
                else:
                    ts = str(leitura.get("timestamp_leitura", ""))[:19].replace("T", " ")
                    print(f"\n=== Ultima Leitura (#{leitura['id']}) ===")
                    print(f"  Corrente:       {float(leitura['corrente_a']):.6f} A")
                    print(f"  Percentual:     {float(leitura['percentual']):.2f}%")
                    print(f"  Classificacao:  {leitura['classificacao'].upper()}")
                    print(f"  Sugestao:       {leitura.get('sugestao', '')}")
                    print(f"  Timestamp:      {ts}\n")
            else:
                print(f"[ERRO] Acao desconhecida: '{acao}'. Tente: ler, ultima")
            continue

        print("[ERRO] Comando invalido! Ex: 'sensor ler', 'db historico'")

    print("Encerrado.")


if __name__ == "__main__":
    main()