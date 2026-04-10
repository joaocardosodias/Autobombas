#!/usr/bin/env python3
"""
CLI simples para o módulo 2‑C (fallback dos sensores) consumindo a API Backend.

Objetivo:
  - Fazer login na API do G06.
  - Consultar última leitura registrada dos sensores.
  - Monitorar (polling contínuo das últimas leituras).
  - Mostrar histórico de leituras de distâncias guardado no BD via API.
"""

import argparse
import sys
import time
import getpass
import requests
from typing import Optional

API_URL = "http://localhost:5000"

TOKEN = None
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


def api_ultima_leitura():
    resp = requests.get(f"{API_URL}/leituras-distancia/bomba/{BOMBA_ID}/ultima", headers=api_headers())
    if resp.status_code == 200:
        return resp.json()
    return None


def api_historico(limite=10):
    resp = requests.get(f"{API_URL}/leituras-distancia/bomba/{BOMBA_ID}?limite={limite}", headers=api_headers())
    if resp.status_code == 200:
        return resp.json()
    return []


def api_solicitar_leitura():
    payload = {"operador_id": USUARIO_ID}
    resp = requests.post(f"{API_URL}/leituras-distancia/solicitar/{BOMBA_ID}", headers=api_headers(), json=payload)
    return resp.status_code == 200


def api_get_limiares():
    resp = requests.get(f"{API_URL}/leituras-distancia/limiares", headers=api_headers())
    if resp.status_code == 200:
        return resp.json()
    return None


def api_set_limiares(dist_info, dist_alerta, dist_critico):
    resp = requests.put(f"{API_URL}/leituras-distancia/limiares", headers=api_headers(), json={
        "dist_info_m": dist_info,
        "dist_alerta_m": dist_alerta,
        "dist_critico_m": dist_critico,
    })
    return resp


def api_status_proximidade():
    resp = requests.get(
        f"{API_URL}/leituras-distancia/bomba/{BOMBA_ID}/status-proximidade",
        headers=api_headers(),
    )
    if resp.status_code == 200:
        return resp.json()
    return None


# === FUNÇÕES DA CLI ===

def acao_ver_status():
    print("\n>>> Pedindo status (ultima leitura na API)...")
    leitura = api_ultima_leitura()
    if not leitura:
        print("[ERRO] Nenhuma leitura registrada.")
        return

    ts = str(leitura.get("timestamp_leitura", ""))[:19].replace("T", " ")
    print(f"\n[Última Leitura #{leitura['id']} | {ts} | Operador: {leitura.get('operador_nome', '?')}]")
    print(f"Frente:   {leitura['distancia_frente_m']}m")
    print(f"Tras:     {leitura['distancia_tras_m']}m")
    print(f"Esquerda: {leitura['distancia_esq_m']}m")
    print(f"Direita:  {leitura['distancia_dir_m']}m")


def acao_monitorar():
    print("\n>>> Monitorando status da bomba a cada 3 segundos via API.")
    print("Pressione Ctrl+C para voltar ao menu.\n")
    try:
        ultimo_id = None
        while True:
            leitura = api_ultima_leitura()
            if leitura and leitura["id"] != ultimo_id:
                ultimo_id = leitura["id"]
                ts = str(leitura.get("timestamp_leitura", ""))[:19].replace("T", " ")
                print(f"[{ts}] F={leitura['distancia_frente_m']}m T={leitura['distancia_tras_m']}m "
                      f"E={leitura['distancia_esq_m']}m D={leitura['distancia_dir_m']}m")
            time.sleep(3)
    except KeyboardInterrupt:
        print("\nVoltando ao menu...")


def acao_historico():
    print("\n>>> Histórico de leituras:")
    rows = api_historico(10)
    if not rows:
        print("[API] Nenhum registro encontrado no histórico.")
        return
        
    print(f"\n{'ID':<5} | {'Frente':<10} | {'Trás':<10} | {'Esq.':<10} | {'Dir.':<10} | {'Data'}")
    print("-" * 80)
    for r in rows:
        ts = str(r.get("timestamp_leitura", ""))[:16].replace("T", " ")
        print(f"{r['id']:<5} | {float(r['distancia_frente_m']):>4.2f}m     | "
              f"{float(r['distancia_tras_m']):>4.2f}m     | "
              f"{float(r['distancia_esq_m']):>4.2f}m     | "
              f"{float(r['distancia_dir_m']):>4.2f}m     | {ts}")


def acao_ver_limiares():
    print("\n>>> Limiares de risco atuais:")
    lim = api_get_limiares()
    if not lim:
        print("[ERRO] Nao foi possivel obter os limiares.")
        return
    print(f"  INFORMATIVO:  d <= {lim['dist_info_m']} m")
    print(f"  ALERTA:       d <= {lim['dist_alerta_m']} m   (velocidade reduzida)")
    print(f"  CRITICO:      d <= {lim['dist_critico_m']} m   (movimento bloqueado)")
    print(f"\n  Regra: 0 < critico < alerta < info")


def acao_set_limiares():
    print("\n>>> Configurar limiares de risco (em metros)")
    print("  Regra: 0 < dist_critico < dist_alerta < dist_info\n")

    lim = api_get_limiares()
    if lim:
        print(f"  Valores atuais: info={lim['dist_info_m']}  alerta={lim['dist_alerta_m']}  critico={lim['dist_critico_m']}\n")

    try:
        dist_info = float(input("  dist_info_m (zona informativa): ").strip())
        dist_alerta = float(input("  dist_alerta_m (zona de alerta): ").strip())
        dist_critico = float(input("  dist_critico_m (zona critica): ").strip())
    except (ValueError, KeyboardInterrupt):
        print("\n[CANCELADO] Valores invalidos.")
        return

    resp = api_set_limiares(dist_info, dist_alerta, dist_critico)
    if resp.status_code == 200:
        novo = resp.json()
        print(f"\n[OK] Limiares atualizados: info={novo['dist_info_m']}  "
              f"alerta={novo['dist_alerta_m']}  critico={novo['dist_critico_m']}")
    else:
        detail = resp.json().get("detail", "Erro desconhecido")
        print(f"\n[ERRO] {detail}")


def acao_status_proximidade():
    print("\n>>> Status de proximidade (intertravamento):")
    status = api_status_proximidade()
    if not status:
        print("[ERRO] Nao foi possivel obter o status.")
        return
    if not status.get("disponivel"):
        print(f"  {status.get('mensagem', 'Sem dados')}")
        return

    ts = str(status.get("timestamp_leitura", ""))[:19].replace("T", " ")
    print(f"  Leitura em: {ts}\n")

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


def menu_interativo():
    global TOKEN, USUARIO_ID, USUARIO_NOME

    print("==============================================")
    print(" CLI - Módulo 2-C (Via Backend API)")
    print("==============================================")

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
    print(f"Trabalhando na Bomba #{BOMBA_ID}\n")

    while True:
        print("\nEscolha uma opção:")
        print("  1) Ver última leitura gravada (GET_STATUS)")
        print("  2) Monitorar leituras em tempo real")
        print("  3) Ver histórico de leituras de distância")
        print("  4) Status de proximidade (intertravamento)")
        print("  5) Ver limiares de risco")
        print("  6) Configurar limiares de risco")
        print("  0) Sair")

        escolha = input("Opção: ").strip()

        if escolha == "1":
            acao_ver_status()
        elif escolha == "2":
            acao_monitorar()
        elif escolha == "3":
            acao_historico()
        elif escolha == "4":
            acao_status_proximidade()
        elif escolha == "5":
            acao_ver_limiares()
        elif escolha == "6":
            acao_set_limiares()
        elif escolha == "0":
            print("Saindo da CLI. Até mais!")
            break
        else:
            print("Opção desconhecida. Tente de novo.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CLI para o módulo 2-C (consumo API backend).",
        add_help=True,
    )
    parser.add_argument(
        "--bomba",
        type=int,
        help="ID da bomba",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    global BOMBA_ID
    if argv is None:
        argv = sys.argv[1:]

    args = parse_args(argv)
    BOMBA_ID = args.bomba

    if BOMBA_ID is None:
        try:
            BOMBA_ID = int(input("ID da bomba: ").strip())
        except (ValueError, KeyboardInterrupt):
            print("[ERRO] ID invalido.")
            return 1

    try:
        menu_interativo()
    except KeyboardInterrupt:
        print("\nEncerrando CLI.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
