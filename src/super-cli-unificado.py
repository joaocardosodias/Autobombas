#!/usr/bin/env python3
"""
SUPER CLI - G06 (Modernizado)
Centraliza todos os comandos de todos os módulos (1-A, 1-B, 2-A, 2-B, 2-C).
Comunica-se inteiramente via API REST com o Backend.
Utiliza 'rich' para UI moderna e 'prompt_toolkit' para input interativo.
"""

import math
import time
import re
import getpass
import sys
import requests
import argparse

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

# Imports de UI Moderna
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, IntPrompt
from rich.live import Live
from rich.align import Align
from rich.layout import Layout
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

console = Console()

API_URL = "http://localhost:5000"
TOKEN = None
USUARIO_ID = None
USUARIO_NOME = None
BOMBA_ID = None

# GLOBAIS - Modulo 1-A (Z)
posicao_atual_cm = 0.0
DIAMETRO_CARRETEL_CM = 0.0
COMPRIMENTO_CORDA_CM = 0.0

# GLOBAIS - Modulo 2-A (XY)
motor_status_xy = "PARADO"
sistema_ligado_xy = False
registro_ativo_id_xy = None
ts_movimento_inicio_xy = None

# ==========================================
# CORE API
# ==========================================
def api_headers():
    return {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def print_error(msg):
    console.print(f"[bold red]⛔ ERRO:[/bold red] [white]{msg}[/white]")

def print_success(msg):
    console.print(f"[bold dark_green]✔ SUCESSO:[/bold dark_green] [bold white]{msg}[/bold white]")

def print_info(msg):
    console.print(f"[bold yellow]ℹ INFO:[/bold yellow] [white]{msg}[/white]")

def print_warning(msg):
    console.print(f"[bold yellow]⚠ AVISO:[/bold yellow] [white]{msg}[/white]")

def print_esp_offline(modulo: str):
    """Exibe painel visualmente destacado quando o ESP está offline."""
    console.print(Panel(
        f"[bold red]O módulo [white]{modulo}[/white] está OFFLINE.[/bold red]\n"
        f"[yellow]• Verifique se o ESP está energizado e conectado ao Wi-Fi.\n"
        f"• Aguarde até 5 s para o heartbeat se restabelecer.\n"
        f"• Use [bold white]/hb[/bold white] para ver o status de todos os módulos.[/yellow]",
        title="[bold red]📡 ESP DESCONECTADO[/bold red]",
        border_style="red",
    ))


def safe_request(method: str, url: str, *, label: str = "", **kwargs):
    """
    Wrapper seguro para todas as chamadas HTTP da CLI.
    Retorna (response | None, error_message | None).
    Trata: timeout, backend offline, 401, 422, 503 (ESP offline), outros erros.
    """
    try:
        resp = requests.request(method, url, timeout=8, **kwargs)
    except requests.ConnectionError:
        return None, "Backend indisponível. Verifique se o servidor está rodando na porta 5000."
    except requests.Timeout:
        return None, f"Timeout ao conectar ao backend{' (' + label + ')' if label else ''}."
    except requests.RequestException as e:
        return None, f"Erro de rede: {e}"

    if resp.status_code == 401:
        return None, "Sessão expirada ou não autorizada. Faça login novamente."
    if resp.status_code == 422:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        return None, f"Dados inválidos enviados à API: {detail}"
    if resp.status_code == 503:
        try:
            detail = resp.json().get("detail", "ESP offline")
        except Exception:
            detail = "ESP offline"
        return None, f"[ESP_OFFLINE] {detail}"
    if resp.status_code >= 500:
        try:
            detail = resp.json().get("detail", "Erro interno do servidor")
        except Exception:
            detail = "Erro interno do servidor"
        return None, f"Erro no servidor (HTTP {resp.status_code}): {detail}"
    if resp.status_code == 400:
        # Deixa passar para que o caller leia o JSON (ex: {"ok": False, "detail": "..."})
        return resp, None
    if resp.status_code == 404:
        try:
            detail = resp.json().get("detail", "Recurso não encontrado")
        except Exception:
            detail = "Recurso não encontrado"
        return None, f"Não encontrado: {detail}"

    return resp, None


def handle_api_error(error_msg: str, modulo_hint: str = "") -> None:
    """Exibe o erro adequado, com painel especial para ESP offline."""
    if error_msg and error_msg.startswith("[ESP_OFFLINE]"):
        detalhe = error_msg.replace("[ESP_OFFLINE] ", "")
        # Extrai o nome do módulo da mensagem, ou usa o hint
        m = re.search(r'ESP (\S+) está offline', detalhe)
        nome_modulo = m.group(1) if m else (modulo_hint or "desconhecido")
        print_esp_offline(nome_modulo)
    else:
        print_error(error_msg)


def api_login(email=None, senha=None):
    console.clear()
    console.print(Panel.fit("[bold yellow]Autenticação do Sistema G06[/bold yellow]", border_style="dark_green"))
    if not email:
        email = Prompt.ask("[bold white]Email[/bold white]")
    if not senha:
        senha = getpass.getpass("Senha: ")

    resp, err = safe_request("POST", f"{API_URL}/auth/login", json={"email": email, "senha": senha})
    if err:
        print_error(err)
        return None
    if resp.status_code != 200:
        print_error(resp.json().get('detail', 'Falha no login'))
        return None
    return resp.json()

def api_carregar_bomba():
    resp, err = safe_request("GET", f"{API_URL}/bombas/{BOMBA_ID}", headers=api_headers())
    if err or resp is None:
        return None
    return resp.json() if resp.status_code == 200 else None

def api_atualizar_config(payload: dict):
    resp, err = safe_request("PATCH", f"{API_URL}/bombas/{BOMBA_ID}/config", headers=api_headers(), json=payload)
    if err:
        handle_api_error(err)
        return None
    return resp.json() if resp else None

def api_heartbeat_todos():
    resp, err = safe_request("GET", f"{API_URL}/sistema/heartbeat")
    if err or resp is None:
        print_error(err or "Falha ao buscar heartbeat.")
        return []
    return resp.json()

# ==========================================
# API - Z (Modulo 1-A)
# ==========================================
def api_fechar_orfaos_z():
    resp, _ = safe_request("PATCH", f"{API_URL}/movimentacao-z/fechar-orfaos/{BOMBA_ID}", headers=api_headers())
    return resp.json() if resp and resp.status_code == 200 else {"fechados": [], "total": 0}

def api_recuperar_posicao_z():
    resp, _ = safe_request("GET", f"{API_URL}/movimentacao-z/posicao/{BOMBA_ID}", headers=api_headers())
    return resp.json() if resp and resp.status_code == 200 else None

def _exibir_erro_api(resp, prefixo: str = "Erro"):
    """Exibe o motivo de qualquer resposta de erro da API."""
    if resp is None:
        return
    try:
        corpo = resp.json()
        detalhe = corpo.get("detail") or corpo.get("message") or str(corpo)
    except Exception:
        detalhe = f"HTTP {resp.status_code}"
    print_error(f"{prefixo}: {detalhe}")


def api_criar_registro_z(comando_bruto, posicao_inicial, deslocamento, voltas):
    resp, err = safe_request("POST", f"{API_URL}/movimentacao-z/", headers=api_headers(), json={
        "bomba_id": BOMBA_ID, "operador_id": USUARIO_ID,
        "comando_bruto": comando_bruto, "posicao_inicial_cm": posicao_inicial,
        "deslocamento_solicitado_cm": deslocamento, "voltas_mqtt": voltas,
    })
    if err:
        handle_api_error(err, modulo_hint=f"motor/{BOMBA_ID}")
        return None
    if resp and resp.status_code == 201:
        return resp.json()["id"]
    _exibir_erro_api(resp, "Movimentação Z não autorizada")
    return None

def api_consultar_status_z(registro_id):
    resp, _ = safe_request("GET", f"{API_URL}/movimentacao-z/bomba/{BOMBA_ID}?limite=10", headers=api_headers())
    if resp and resp.status_code == 200:
        for r in resp.json():
            if r["id"] == registro_id:
                return r
    return None

def api_historico_z(limite=10):
    resp, err = safe_request("GET", f"{API_URL}/movimentacao-z/bomba/{BOMBA_ID}?limite={limite}", headers=api_headers())
    if err:
        print_error(err)
        return []
    return resp.json() if resp and resp.status_code == 200 else []

# ==========================================
# API - XY (Modulo 2-A)
# ==========================================
def api_fechar_orfaos_xy():
    resp, _ = safe_request("PATCH", f"{API_URL}/movimentacao-xy/fechar-orfaos/{BOMBA_ID}", headers=api_headers())
    return resp.json() if resp and resp.status_code == 200 else {"fechados": [], "total": 0}


def api_criar_movimento_xy(direcao):
    global registro_ativo_id_xy, ts_movimento_inicio_xy
    resp, err = safe_request("POST", f"{API_URL}/movimentacao-xy/", headers=api_headers(), json={
        "bomba_id": BOMBA_ID, "operador_id": USUARIO_ID, "direcao": direcao,
    })
    if err:
        handle_api_error(err, modulo_hint=f"balsa/{BOMBA_ID}")
        return False
    if resp and resp.status_code == 201:
        registro_ativo_id_xy = resp.json()["id"]
        ts_movimento_inicio_xy = time.time()
        print_success(f"Movimentação XY [bold]#{registro_ativo_id_xy}[/bold] criada.")
        return True
    _exibir_erro_api(resp, "Movimentação XY não autorizada")
    return False


def api_finalizar_movimento_xy(status="CONCLUIDO"):
    global registro_ativo_id_xy, ts_movimento_inicio_xy
    if not registro_ativo_id_xy:
        return
    duracao_ms = int((time.time() - ts_movimento_inicio_xy) * 1000) if ts_movimento_inicio_xy else None
    safe_request("PATCH", f"{API_URL}/movimentacao-xy/{registro_ativo_id_xy}", headers=api_headers(), json={
        "status": status, "duracao_ms": duracao_ms,
    })
    print_info(f"Movimentação XY [bold]#{registro_ativo_id_xy}[/bold] finalizada: {status} ({duracao_ms}ms)")
    registro_ativo_id_xy = None
    ts_movimento_inicio_xy = None


def api_enviar_comando_xy(acao):
    resp, err = safe_request("POST", f"{API_URL}/movimentacao-xy/comando/{BOMBA_ID}", headers=api_headers(), json={
        "acao": acao, "operador_id": USUARIO_ID,
    })
    if err:
        handle_api_error(err, modulo_hint=f"balsa/{BOMBA_ID}")
        return False
    if resp and resp.status_code == 200:
        return True
    _exibir_erro_api(resp, f"Comando XY '{acao}' não aceito")
    return False

def api_historico_xy(limite=10):
    resp, err = safe_request("GET", f"{API_URL}/movimentacao-xy/bomba/{BOMBA_ID}?limite={limite}", headers=api_headers())
    if err:
        print_error(err)
        return []
    return resp.json() if resp and resp.status_code == 200 else []

def api_logs():
    resp, err = safe_request("GET", f"{API_URL}/logs", headers=api_headers())
    if err:
        print_error(err)
        return None
    return resp.json() if resp and resp.status_code == 200 else None

# ==========================================
# API - Modo Automático
# ==========================================
def api_auto_ligar():
    resp, err = safe_request("POST", f"{API_URL}/auto/{BOMBA_ID}/ligar", headers=api_headers())
    if err:
        handle_api_error(err)
        return None
    return resp.json() if resp else None

def api_auto_desligar():
    resp, err = safe_request("POST", f"{API_URL}/auto/{BOMBA_ID}/desligar", headers=api_headers())
    if err:
        handle_api_error(err)
        return None
    return resp.json() if resp else None

def api_auto_status():
    resp, err = safe_request("GET", f"{API_URL}/auto/{BOMBA_ID}/status", headers=api_headers())
    if err:
        handle_api_error(err)
        return None
    return resp.json() if resp else None

# ==========================================
# GLOBAIS - CORRENTE (Modulo 1-B) & DIST (Modulo 2-C)
# ==========================================
def api_ultima_leitura(tipo):
    resp, err = safe_request("GET", f"{API_URL}/leituras-{tipo}/bomba/{BOMBA_ID}/ultima", headers=api_headers())
    if err:
        print_error(err)
        return None
    return resp.json() if resp and resp.status_code == 200 else None

def api_historico(tipo, limite=10):
    resp, err = safe_request("GET", f"{API_URL}/leituras-{tipo}/bomba/{BOMBA_ID}?limite={limite}", headers=api_headers())
    if err:
        print_error(err)
        return []
    return resp.json() if resp and resp.status_code == 200 else []

def api_status_proximidade():
    resp = requests.get(f"{API_URL}/leituras-distancia/bomba/{BOMBA_ID}/status-proximidade", headers=api_headers())
    return resp.json() if resp.status_code == 200 else None

def api_get_limiares():
    resp = requests.get(f"{API_URL}/leituras-distancia/limiares", headers=api_headers())
    return resp.json() if resp.status_code == 200 else None

def api_set_limiares(dist_info, dist_alerta, dist_critico):
    return requests.put(f"{API_URL}/leituras-distancia/limiares", headers=api_headers(), json={
        "dist_info_m": dist_info, "dist_alerta_m": dist_alerta, "dist_critico_m": dist_critico,
    })

# ==========================================
# PROCESSAMENTO DE COMANDOS
# ==========================================

# --- Sensores Proximidade (Modulo 2-C → Intertravamento) ---
def processar_cmd_sensor(cmd_lower):
    partes = cmd_lower.split()
    sub = partes[1] if len(partes) > 1 else ""
    args = partes[2:] if len(partes) > 2 else []

    if sub == "status":
        status = api_status_proximidade()
        if not status:
            print_error("Não foi possível obter o status dos sensores.")
            return
        if not status.get("disponivel"):
            print_warning(status.get("mensagem", "Sem dados de sensores disponíveis."))
            return

        ts = str(status.get("timestamp_leitura", ""))[:19].replace("T", " ")
        linhas = f"[dim]{ts}[/dim]\n"

        nivel_cor = {"SEGURO": "green", "INFORMATIVO": "blue", "ALERTA": "yellow", "CRITICO": "bold red"}
        for direcao, info in status["direcoes"].items():
            cor = nivel_cor.get(info["nivel"], "white")
            linhas += f"  {direcao:<10}  {info['distancia_m']:>5.2f} m  [{cor}]{info['nivel']}[/{cor}]\n"

        bloq = status.get("direcoes_bloqueadas", [])
        alerta = status.get("direcoes_alerta", [])
        if bloq:
            linhas += f"\n  [bold red]Direções BLOQUEADAS: {', '.join(bloq)}[/bold red]"
        if alerta:
            linhas += f"\n  [yellow]Direções em ALERTA: {', '.join(alerta)}[/yellow]"

        console.print(Panel(linhas.strip(), title="[yellow]📡 Sensores de Proximidade[/yellow]", border_style="dark_green", padding=(1, 2)))

    elif sub == "limiares":
        if not args:
            lim = api_get_limiares()
            if not lim:
                print_error("Não foi possível obter os limiares.")
                return
            linhas = (
                f"  INFORMATIVO:  d ≤ [white]{lim['dist_info_m']}[/white] m\n"
                f"  ALERTA:       d ≤ [yellow]{lim['dist_alerta_m']}[/yellow] m  (velocidade reduzida)\n"
                f"  CRÍTICO:      d ≤ [bold red]{lim['dist_critico_m']}[/bold red] m  (movimento bloqueado)\n\n"
                f"  [dim]Para alterar: /sensor limiares <info> <alerta> <critico>[/dim]"
            )
            console.print(Panel(linhas, title="[yellow]⚙️ Limiares de Risco[/yellow]", border_style="dark_green", padding=(1, 2)))
        elif len(args) == 3:
            try:
                vals = [float(a) for a in args]
            except ValueError:
                print_error("Valores devem ser numéricos. Ex: /sensor limiares 2.0 1.0 0.5")
                return
            resp = api_set_limiares(*vals)
            if resp.status_code == 200:
                novo = resp.json()
                print_success(f"Limiares atualizados: info={novo['dist_info_m']}  alerta={novo['dist_alerta_m']}  critico={novo['dist_critico_m']}")
            else:
                detail = resp.json().get("detail", "Erro desconhecido")
                print_error(detail)
        else:
            print_error("Uso: /sensor limiares  ou  /sensor limiares <info> <alerta> <critico>")

    else:
        print_error("Subcomando desconhecido. Use: [bold white]/sensor status[/bold white] | [bold white]/sensor limiares[/bold white]")


# --- Z (Modulo 1-A) ---
def _exibir_status_z():
    posicao_backend = api_recuperar_posicao_z()
    em_andamento = posicao_backend.get("em_andamento", False) if posicao_backend else False
    estado_motor = "[bold red]EM MOVIMENTO[/bold red]" if em_andamento else "[bold green]PARADA[/bold green]"
    print_info(
        f"Posição atual do Motor Z: [bold white]{posicao_atual_cm:.2f} cm[/bold white] | "
        f"Motobomba: {estado_motor}"
    )


def processar_cmd_z(cmd_lower, original_cmd):
    global posicao_atual_cm
    
    match = re.match(r'^/z\s+(down|up|descer|subir|status|reset)(?:\s+([-\d.]+))?$', cmd_lower)
    if not match:
        if cmd_lower == "/z status":
            _exibir_status_z()
        else:
            print_error("Sintaxe /z inválida! Ex: '/z down 10', '/z up 15.5', '/z status'")
        return

    acao, valor_str = match.groups()
    movimento_cm = 0.0

    if acao == "reset":
        if posicao_atual_cm == 0.0:
            print_info("Corda já totalmente recolhida.")
            return
        movimento_cm = -posicao_atual_cm
    elif acao in ["subir", "descer", "up", "down"]:
        if not valor_str:
            print_error(f"Informe o valor em cm. Ex: /z {acao} 15")
            return
        try:
            movimento_cm = float(valor_str)
            if movimento_cm < 0: movimento_cm = abs(movimento_cm)
            if acao in ["subir", "up"]: movimento_cm = -movimento_cm
        except ValueError:
            print_error("Valor numérico inválido.")
            return
    elif acao == "status":
        estado_z = api_recuperar_posicao_z()
        if estado_z and estado_z.get("posicao_cm") is not None:
            posicao_atual_cm = estado_z["posicao_cm"]
        return print_info(f"Posição atual do Motor Z: [bold white]{posicao_atual_cm:.2f} cm[/bold white]")
    else:
        print_error(f"Ação /z desconhecida: '{acao}'")
        return

    nova_posicao = posicao_atual_cm + movimento_cm
    if nova_posicao < 0.0:
        print_error(f"Limite mínimo violado. Pode recolher no máximo {posicao_atual_cm:.2f} cm.")
        return
    if nova_posicao > COMPRIMENTO_CORDA_CM:
        print_error(f"Limite máximo violado. Pode soltar no máximo {COMPRIMENTO_CORDA_CM - posicao_atual_cm:.2f} cm.")
        return

    voltas = movimento_cm / (DIAMETRO_CARRETEL_CM * math.pi)
    reg_id = api_criar_registro_z(original_cmd, posicao_atual_cm, movimento_cm, round(voltas, 4))
    
    if reg_id:
        posicao_atual_cm = nova_posicao
        print_info(f"Girando [bold]{voltas:+.4f}[/bold] voltas. Posição projetada: [bold]{posicao_atual_cm:.2f} cm[/bold]")
        
        with console.status("[cyan]Aguardando finalização do Motor Z (Ctrl+C para cancelar espera)..."):
            while True:
                try:
                    time.sleep(1)
                    reg = api_consultar_status_z(reg_id)
                    if reg and reg["status"] != "EM_ANDAMENTO":
                        break
                    if reg is None:
                        print_warning("Perdeu contato com a API durante a espera.")
                        # Mantém posicao_atual_cm = nova_posicao (motor já foi comandado)
                        # Tenta sincronizar do banco uma última vez
                        estado_z = api_recuperar_posicao_z()
                        if estado_z and estado_z.get("posicao_cm") is not None:
                            posicao_atual_cm = estado_z["posicao_cm"]
                            print_info(f"Posição recuperada do banco: [bold white]{posicao_atual_cm:.2f} cm[/bold white]")
                        # nova_posicao já foi atribuída a posicao_atual_cm na linha 375
                        return
                except KeyboardInterrupt:
                    print_warning("\nEspera cancelada. O motor pode ainda estar se movendo.")
                    return
                    
        if reg["status"] == "CONCLUIDO":
            posicao_atual_cm = float(reg.get("posicao_final_cm", posicao_atual_cm))
            print_success(f"Motor Z Concluído! Fixado em {posicao_atual_cm:.2f} cm")
        elif reg["status"] == "ABORTADO":
            posicao_atual_cm = float(reg.get("posicao_final_cm", posicao_atual_cm))
            print_warning(
                f"Operação ABORTADA! "
                f"Deslocamento real: {reg.get('deslocamento_real_cm')}cm. "
                f"Fixado em: {posicao_atual_cm:.2f} cm\n"
                f"[dim]Causa provável: ESP perdeu conexão com o backend (watchdog ativado).[/dim]"
            )


# --- Balsa XY (Modulo 2-A) ---
def processar_cmd_xy(cmd_lower):
    global motor_status_xy, sistema_ligado_xy, registro_ativo_id_xy
    
    acao = cmd_lower.replace("/balsa ", "").strip()

    if acao == "on":
        if sistema_ligado_xy:
            print_warning("Sistema XY já se encontra ligado.")
        else:
            if api_enviar_comando_xy("ligar"):
                sistema_ligado_xy = True
                print_success("Energia da Balsa LIGADA.")
    elif acao == "off":
        if not sistema_ligado_xy:
            print_warning("Sistema XY já se encontra desligado.")
        else:
            if registro_ativo_id_xy:
                api_enviar_comando_xy("parar")
                api_finalizar_movimento_xy("CONCLUIDO")
            if api_enviar_comando_xy("desligar"):
                sistema_ligado_xy = False
                print_success("Energia da Balsa DESLIGADA.")
    elif acao == "/balsa":
        st_sys = "[bold dark_green]LIGADO[/bold dark_green]" if sistema_ligado_xy else "[bold red]DESLIGADO[/bold red]"
        console.print(Panel(f"[yellow]Energia:[/yellow] {st_sys}\n[yellow]Motor Balsa:[/yellow] [bold white]{motor_status_xy}[/bold white]", title="[yellow]Status XY[/yellow]", border_style="dark_green", width=40))
    elif acao in ["esq", "dir", "frente", "tras"]:
        if not sistema_ligado_xy:
            print_error("É necessário ligar a energia primeiro: [bold]/balsa on[/bold]")
            return
        if registro_ativo_id_xy:
            api_finalizar_movimento_xy("CONCLUIDO")
        if acao in ["dir", "frente"]:
            acao_backend = "direita" if acao == "dir" else "frente"
        else:
            acao_backend = "esquerda" if acao == "esq" else "tras"
        if api_criar_movimento_xy(acao_backend):
            labels = {"esq": "<< ESQUERDA", "dir": "DIREITA >>", "frente": "▲ FRENTE", "tras": "▼ TRÁS"}
            motor_status_xy = labels[acao]
            print_success(f"Balsa fluindo para [bold]{acao_backend.upper()}[/bold]")
    elif acao == "stop":
        if not sistema_ligado_xy:
            return print_warning("Sistema já sem energia.")
        if api_enviar_comando_xy("parar"):
            if registro_ativo_id_xy:
                api_finalizar_movimento_xy("CONCLUIDO")
            motor_status_xy = "PARADO"
            print_success("Motores de direção travados (PARADO).")
    else:
        print_error(f"Ação /balsa desconhecida: '{acao}'")


# --- Sensores: Corrente e Radar ---
def processar_cmd_sensores(cmd_lower, prefix, nome):
    acao = cmd_lower.replace(f"{prefix} ", "").strip()
    
    if acao == prefix or acao == "last":
        tipo = "corrente" if prefix == "/corrente" else "distancia"
        leitura = api_ultima_leitura(tipo)
        if not leitura:
            print_warning(f"Nenhuma leitura de {nome} registrada no Banco de Dados.")
            return
            
        ts = str(leitura.get("timestamp_leitura", ""))[:19].replace("T", " ")
        if prefix == "/corrente":
            panel = Panel.fit(
                f"[yellow]Corrente:[/yellow] [bold white]{float(leitura['corrente_a']):.6f} A[/bold white]\n\n"
                f"[dim]Data da coleta: {ts}[/dim]",
                title=f"[yellow]🔍 Leitura de Corrente (ID: {leitura['id']})[/yellow]", border_style="dark_green"
            )
        else:
            panel = Panel.fit(
                f"[yellow]▲ Frente:[/yellow] [white]{leitura['distancia_frente_m']} m[/white]\n"
                f"[yellow]▼ Trás:[/yellow]   [white]{leitura['distancia_tras_m']} m[/white]\n"
                f"[yellow]◄ Esq:[/yellow]    [white]{leitura['distancia_esq_m']} m[/white]\n"
                f"[yellow]► Dir:[/yellow]    [white]{leitura['distancia_dir_m']} m[/white]\n\n"
                f"[dim]Data da varredura: {ts}[/dim]",
                title=f"[yellow]📡 Leitura Espacial (ID: {leitura['id']})[/yellow]", border_style="dark_green"
            )
        console.print(panel)
        
    elif prefix == "/radar" and acao == "/radar":
        print_info("Iniciando varredura em tempo real. Pressione Ctrl+C para sair do painel.")
        try:
            ultimo_id = None
            with Live(console=console, refresh_per_second=2) as live:
                while True:
                    leitura = api_ultima_leitura("distancia")
                    if leitura and leitura["id"] != ultimo_id:
                        ultimo_id = leitura["id"]
                        
                        grid = Table.grid(expand=True)
                        grid.add_column(justify="center") 
                        grid.add_column(justify="center")
                        grid.add_column(justify="center")
                        
                        grid.add_row("", f"[yellow]▲ [white]{leitura['distancia_frente_m']}m[/white][/yellow]", "")
                        grid.add_row(f"[yellow]◄ [white]{leitura['distancia_esq_m']}m[/white][/yellow]", "[dark_green]🚣 BALSA[/dark_green]", f"[yellow]► [white]{leitura['distancia_dir_m']}m[/white][/yellow]")
                        grid.add_row("", f"[yellow]▼ [white]{leitura['distancia_tras_m']}m[/white][/yellow]", "")
                        
                        p = Panel(grid, title="[bold yellow]📡 Radar Dinâmico[/bold yellow]", border_style="dark_green", padding=(1, 2))
                        live.update(p)
                    time.sleep(1)
        except KeyboardInterrupt:
            print_info("\nMonitoramento encerrado.")
    else:
        print_error(f"Comando de {prefix} inválido.")


# --- Câmera (Modulo 2-B) ---
def processar_cmd_cam(cmd_lower):
    acao = cmd_lower.replace("/cam ", "").strip()
    if acao == "status":
        st = "[bold green]SIM[/bold green]" if HAS_CV2 else "[bold red]NÃO[/bold red]"
        console.print(Panel.fit(f"Módulo de Câmera Ativo na CLI.\nBibliotecas Gráficas (OpenCV): {st}", title="🎥 Status Câmara"))
        return

    if acao == "/cam":
        if not HAS_CV2:
            return print_error("OpenCV/Numpy ausentes. O streaming local não poderá ser renderizado. Instale: pip install opencv-python numpy")
            
        url = "http://10.30.244.181/stream"
        print_info(f"Conectando ao streaming em {url}...\n[bold]DICA:[/bold] Pressione a tecla 'q' na janela para fechar o vídeo.")
        
        try:
            res = requests.get(url, stream=True, timeout=5)
            if res.status_code != 200:
                return print_error(f"ESP conectada mas sub-fluxo recusado (HTTP {res.status_code}).")
                
            bytes_data = bytes()
            for chunk in res.iter_content(chunk_size=1024):
                bytes_data += chunk
                a = bytes_data.find(b'\xff\xd8') 
                b = bytes_data.find(b'\xff\xd9') 
                if a != -1 and b != -1:
                    jpg = bytes_data[a:b+2]
                    bytes_data = bytes_data[b+2:]
                    frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    if frame is not None:
                        cv2.imshow('[G06] Câmera Módulo 2-B', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print_info("Transmissão fechada.")
                        break
            cv2.destroyAllWindows()
            
        except requests.exceptions.Timeout:
            print_error("Timeout ao conectar ao ESP32-CAM.")
            print_warning("O ESP32-CAM não respondeu a tempo. Verifique se está ligado e acessível na rede.")
        except requests.exceptions.ConnectionError:
            print_error("Falha de conexão com a Placa da Câmera.")
            print_warning("O ESP32-CAM pode estar offline, com outro IP ou os computadores estão em redes distintas.")
        except requests.exceptions.RequestException as e:
            print_error(f"Erro de rede com câmera: {e}")
    else:
        print_error("Comando de /cam invalido. Utilize '/cam' para abrir ou '/cam status'.")

# --- Modo Automático ---
def processar_cmd_auto(cmd_lower):
    acao = cmd_lower.replace("/auto", "").strip()

    if acao in ["on", "ligar"]:
        resultado = api_auto_ligar()
        if not resultado:
            return

        if not resultado.get("ok"):
            # Nomes amigáveis para os módulos
            NOMES_MODULOS = {
                f"motor/{BOMBA_ID}":    "Módulo 1-A — Motor Z",
                f"corrente/{BOMBA_ID}": "Módulo 1-B — Sensor de Corrente",
                f"sensor/{BOMBA_ID}":   "Módulo 2-C — Radar Ultrassônico",
                f"balsa/{BOMBA_ID}":    "Módulo 2-A — Balsa XY",
            }

            hb = api_heartbeat_todos()
            def hb_status(modulo_key):
                for m in hb:
                    if m["modulo"] == modulo_key:
                        if m["online"]:
                            return "[bold dark_green]✔ ONLINE[/bold dark_green]"
                        else:
                            return "[bold red]✘ OFFLINE[/bold red]"
                return "[dim]? sem sinal[/dim]"

            bomba = api_carregar_bomba()
            inf_val = bomba.get("limite_inferior") if bomba else None
            sup_val = bomba.get("limite_superior") if bomba else None
            banda_existe = bool(inf_val and sup_val)
            banda_valida = banda_existe and float(inf_val) < float(sup_val)
            limite_ok = banda_valida

            if not banda_existe:
                limite_str = "[bold red]✘ não configurado — use /config set inf=X sup=Y[/bold red]"
            elif not banda_valida:
                limite_str = (
                    f"[bold red]✘ INVÁLIDO: inf ({inf_val}) ≥ sup ({sup_val})"
                    f" — use /config set inf=X sup=Y[/bold red]"
                )
            else:
                limite_str = f"[bold dark_green]✔ [{inf_val} A — {sup_val} A][/bold dark_green]"

            # Motivo extra do backend (quando não é problema de ESP)
            motivo = resultado.get("detail", "")
            bloqueios_esp = resultado.get("bloqueios", [])
            motivo_extra = (
                f"\n[yellow]Motivo:[/yellow] {motivo}\n"
                if motivo and not bloqueios_esp else ""
            )

            # Lista linhas dos módulos necessários para o modo auto
            modulos_necessarios = [
                f"motor/{BOMBA_ID}",
                f"corrente/{BOMBA_ID}",
            ]
            linhas_modulos = ""
            for key in modulos_necessarios:
                nome = NOMES_MODULOS.get(key, key)
                linhas_modulos += f"  [yellow]{nome}:[/yellow]  {hb_status(key)}\n"

            console.print(Panel(
                f"[bold red]✘ Modo automático bloqueado[/bold red]{motivo_extra}\n"
                f"[bold white]ESPs necessários:[/bold white]\n"
                f"{linhas_modulos}\n"
                f"[bold white]Banda de corrente:[/bold white]\n"
                f"  {limite_str}\n\n"
                f"[dim]Corrija os itens em vermelho e tente novamente.[/dim]",
                title="[bold red]⚠  Modo Automático — BLOQUEADO[/bold red]",
                border_style="red",
                width=62,
            ))
        else:
            console.print(Panel(
                f"[bold dark_green]✔ Modo automático ATIVADO[/bold dark_green]\n\n"
                f"[yellow]Posição inicial:[/yellow]  {resultado['posicao_inicial_cm']:.2f} cm\n"
                f"[yellow]Banda corrente:[/yellow]   [{resultado['limite_inferior']} A — {resultado['limite_superior']} A]\n"
                f"[yellow]Passo por ciclo:[/yellow]  {resultado['passo_cm']} cm",
                title="[bold dark_green]🤖 Modo Automático[/bold dark_green]",
                border_style="dark_green",
                width=45,
            ))

    elif acao in ["off", "desligar"]:
        resultado = api_auto_desligar()
        if not resultado:
            return
        if not resultado.get("ok"):
            motivo = resultado.get("detail", "Falha desconhecida.")
            console.print(Panel(
                f"[bold red]✘ Não foi possível desativar[/bold red]\n\n"
                f"[yellow]Motivo:[/yellow] {motivo}\n\n"
                f"[dim]O modo automático pode já estar inativo.\n"
                f"Use [bold white]/auto status[/bold white] para verificar.[/dim]",
                title="[bold red]⚠ Modo Automático — Erro ao Desligar[/bold red]",
                border_style="red",
                width=50,
            ))
        else:
            console.print(Panel(
                "[bold yellow]⏹ Modo automático DESATIVADO[/bold yellow]\n\n"
                "[dim]O motor concluirá o passo atual antes de parar.[/dim]",
                title="[bold yellow]🤖 Modo Automático[/bold yellow]",
                border_style="yellow",
                width=50,
            ))
            # Atualiza posicao_atual_cm com a última posição gravada pelo modo auto
            import time as _time; _time.sleep(1.5)
            estado_z = api_recuperar_posicao_z()
            if estado_z and estado_z.get("posicao_cm") is not None:
                posicao_atual_cm = estado_z["posicao_cm"]
                print_info(f"Posição sincronizada: [bold white]{posicao_atual_cm:.2f} cm[/bold white]")

    elif acao in ["", "status"]:
        st = api_auto_status()
        if not st:
            return
        ativo = st.get("ativo", False)
        fase = st.get("fase", "N/A")
        cor_fase = {
            "DESCENDO":       "cyan",
            "SUBINDO":        "yellow",
            "ESTAVEL":        "dark_green",
            "MOTOR_OFFLINE":  "red",
            "SENSOR_OFFLINE": "red",
            "LIMITE_MINIMO":  "yellow",
            "SEM_LEITURA":    "yellow",
            "ERRO":           "bold red",
            "PARADO":         "dim",
            "INICIANDO":      "blue",
        }.get(fase, "white")
        status_str = "[bold dark_green]ATIVO[/bold dark_green]" if ativo else "[bold red]INATIVO[/bold red]"
        ultimo_erro = st.get("ultimo_erro")
        console.print(Panel(
            f"[yellow]Estado:[/yellow]          {status_str}\n"
            f"[yellow]Fase:[/yellow]            [{cor_fase}]{fase}[/{cor_fase}]\n"
            f"[yellow]Posição:[/yellow]         {st.get('posicao_cm', 0):.2f} cm\n"
            f"[yellow]Banda corrente:[/yellow]  [{st.get('limite_inferior', '-')} A — {st.get('limite_superior', '-')} A]\n"
            f"[yellow]Passo:[/yellow]           {st.get('passo_cm', '-')} cm\n"
            f"[yellow]Ciclos:[/yellow]          {st.get('ciclos', 0)}"
            + (f"\n[bold red]Último erro:[/bold red] {ultimo_erro}" if ultimo_erro else ""),
            title="[bold yellow]🤖 Modo Automático[/bold yellow]",
            border_style="dark_green" if ativo else "dim",
            width=55,
        ))
    else:
        console.print(Panel(
            "[white]Comandos disponíveis:[/white]\n\n"
            "  [bold white]/auto on[/bold white]      — Ativa o modo automático\n"
            "  [bold white]/auto off[/bold white]     — Desativa o modo automático\n"
            "  [bold white]/auto status[/bold white]  — Exibe o estado atual",
            title="[bold yellow]⚠ Comando /auto inválido[/bold yellow]",
            border_style="yellow",
            width=50,
        ))


# --- Configurações da Bomba ---
def processar_cmd_config(cmd_lower):
    """Permite visualizar e alterar as configurações de hardware/segurança da bomba."""
    acao = cmd_lower.replace("/config", "").strip()

    # /config sem subcomando ou /config show — exibe configurações atuais
    if acao in ["", "show", "ver"]:
        bomba = api_carregar_bomba()
        if not bomba:
            return
        def fmt_prox(val):
            return f"[white]{float(val):.2f} m[/white]" if val else "[dim]0.30 m (padrão)[/dim]"
        console.print(Panel(
            f"[yellow]Diâmetro do Carretel:[/yellow]  [white]{bomba.get('diametro_carretel_cm', '-')} cm[/white]\n"
            f"[yellow]Comprimento da Corda:[/yellow]  [white]{bomba.get('comprimento_corda_cm', '-')} cm[/white]\n"
            f"[yellow]Limite Inferior (min):[/yellow] [white]{bomba.get('limite_inferior') or '[dim]não definido[/dim]'} A[/white]\n"
            f"[yellow]Limite Superior (max):[/yellow] [white]{bomba.get('limite_superior') or '[dim]não definido[/dim]'} A[/white]\n"
            f"[yellow]Passo Auto (cm):[/yellow]       [white]{bomba.get('passo_auto_cm', 2.0)} cm[/white]\n"
            f"[bold white]── Proximidade (Módulo 2-C) ──[/bold white]\n"
            f"[yellow]Bloqueio Frente:[/yellow]  {fmt_prox(bomba.get('limite_prox_frente_m'))}\n"
            f"[yellow]Bloqueio Trás:[/yellow]    {fmt_prox(bomba.get('limite_prox_tras_m'))}\n"
            f"[yellow]Bloqueio Esq:[/yellow]     {fmt_prox(bomba.get('limite_prox_esq_m'))}\n"
            f"[yellow]Bloqueio Dir:[/yellow]     {fmt_prox(bomba.get('limite_prox_dir_m'))}",
            title=f"[bold yellow]⚙️ Configurações da Bomba #{BOMBA_ID}[/bold yellow]",
            border_style="dark_green",
            width=55,
        ))
        return

    # /config set campo=valor [campo=valor ...]
    if acao.startswith("set "):
        partes = acao[4:].strip().split()
        payload = {}
        campos_validos = {
            "diametro":  "diametro_carretel_cm",
            "corda":     "comprimento_corda_cm",
            "inf":       "limite_inferior",
            "sup":       "limite_superior",
            "passo":     "passo_auto_cm",
            "p_frente":  "limite_prox_frente_m",
            "p_tras":    "limite_prox_tras_m",
            "p_esq":     "limite_prox_esq_m",
            "p_dir":     "limite_prox_dir_m",
        }
        for parte in partes:
            if "=" not in parte:
                print_error(f"Formato inválido: '{parte}'. Use campo=valor.")
                return
            chave, valor = parte.split("=", 1)
            chave = chave.lower()
            if chave not in campos_validos:
                print_error(
                    f"Campo '{chave}' desconhecido. Válidos: "
                    + ", ".join(campos_validos.keys())
                )
                return
            try:
                payload[campos_validos[chave]] = float(valor)
            except ValueError:
                print_error(f"Valor '{valor}' não é numérico.")
                return

        if not payload:
            print_error("Nenhum campo fornecido.")
            return

        # Valida banda na CLI antes de enviar à API
        if "limite_inferior" in payload or "limite_superior" in payload:
            bomba_atual = api_carregar_bomba() or {}
            inf_final = payload.get("limite_inferior",
                        float(bomba_atual["limite_inferior"]) if bomba_atual.get("limite_inferior") else None)
            sup_final = payload.get("limite_superior",
                        float(bomba_atual["limite_superior"]) if bomba_atual.get("limite_superior") else None)
            if inf_final is not None and sup_final is not None:
                if float(sup_final) <= float(inf_final):
                    print_error(
                        f"Banda inválida: limite superior ({sup_final} A) deve ser "
                        f"maior que limite inferior ({inf_final} A).\n"
                        f"  Exemplo: [bold white]/config set inf=50 sup=70[/bold white]"
                    )
                    return

        resultado = api_atualizar_config(payload)
        if resultado:
            print_success("Configurações atualizadas com sucesso!")
            global DIAMETRO_CARRETEL_CM, COMPRIMENTO_CORDA_CM
            if "diametro_carretel_cm" in payload:
                DIAMETRO_CARRETEL_CM = float(payload["diametro_carretel_cm"])
            if "comprimento_corda_cm" in payload:
                COMPRIMENTO_CORDA_CM = float(payload["comprimento_corda_cm"])
        return

    print_error(
        "Sintaxe inválida. Exemplos:\n"
        "  [bold white]/config[/bold white]                                   (ver configurações)\n"
        "  [bold white]/config set inf=50 sup=70[/bold white]                 (banda de dragagem)\n"
        "  [bold white]/config set passo=3 corda=40[/bold white]              (múltiplos)"
    )


# --- Heartbeat / Status dos Módulos ---
def processar_cmd_hb():
    """Exibe o estado de heartbeat de todos os módulos ESP."""
    modulos = api_heartbeat_todos()
    if not modulos:
        print_warning("Não foi possível buscar o status dos módulos.")
        return

    table = Table(
        title="[bold yellow]📡 Status de Conectividade dos Módulos ESP[/bold yellow]",
        border_style="dark_green",
    )
    table.add_column("Módulo", style="yellow")
    table.add_column("Status", justify="center")
    table.add_column("Último PING", style="white")

    for m in modulos:
        if m["online"]:
            status_str = "[bold dark_green]● ONLINE[/bold dark_green]"
        else:
            status_str = "[bold red]○ OFFLINE[/bold red]"
        ultimo = str(m.get("ultimo_ping") or "-")[:19].replace("T", " ")
        table.add_row(m["modulo"], status_str, ultimo)

    console.print(table)

# --- Processar Historicos Gerais ---
def processar_cmd_history(cmd_lower):
    partes = cmd_lower.split()
    if len(partes) < 2:
        return print_error("Faltou o alvo. Ex: /history z, /history balsa, /history radar, /history corrente")
    alvo = partes[1]
    limite = int(partes[2]) if len(partes) > 2 and partes[2].isdigit() else 10
    
    if alvo == "z":
        rows = api_historico_z(limite)
        if not rows: return print_warning("Nenhum registro Z encontrado.")
        table = Table(title=f"[yellow]Histórico Eixo Z (Últimos {limite})[/yellow]", border_style="dark_green")
        table.add_column("ID", justify="center", style="yellow")
        table.add_column("Comando", style="white")
        table.add_column("Inicial", justify="right", style="white")
        table.add_column("Solicitado", justify="right", style="white")
        table.add_column("Real", justify="right", style="white")
        table.add_column("Status", justify="center")
        table.add_column("Timestamp", style="white")
        for r in rows:
            d_real = f"{float(r['deslocamento_real_cm']):.2f}cm" if r.get("deslocamento_real_cm") else "-"
            st_color = "dark_green" if r["status"] == "CONCLUIDO" else ("yellow" if r["status"] == "EM_ANDAMENTO" else "red")
            table.add_row(str(r["id"]), r["comando_bruto"], f"{float(r['posicao_inicial_cm']):.2f}cm", f"{float(r['deslocamento_solicitado_cm']):.2f}cm", d_real, f"[{st_color}]{r['status']}[/{st_color}]", str(r.get("timestamp_inicio", ""))[:19].replace("T", " "))
        console.print(table)
        
    elif alvo == "balsa":
        rows = api_historico_xy(limite)
        if not rows: return print_warning("Nenhum registro Balsa encontrado.")
        table = Table(title=f"[yellow]Histórico Balsa (Últimos {limite})[/yellow]", border_style="dark_green")
        table.add_column("ID", justify="center", style="yellow")
        table.add_column("Direção", style="white")
        table.add_column("Duração", justify="right", style="white")
        table.add_column("Status", justify="center")
        table.add_column("Timestamp", style="white")
        for r in rows:
            dur = f"{r['duracao_ms']}ms" if r.get("duracao_ms") else "-"
            st_color = "dark_green" if r["status"] == "CONCLUIDO" else "yellow"
            table.add_row(str(r["id"]), r["direcao"].upper(), dur, f"[{st_color}]{r['status']}[/{st_color}]", str(r.get("timestamp_inicio", ""))[:19].replace("T", " "))
        console.print(table)
        
    elif alvo == "corrente":
        rows = api_historico("corrente", limite)
        if not rows: return print_warning("Nenhum registro de corrente encontrado.")
        table = Table(title=f"[yellow]Histórico Corrente (Últimos {limite})[/yellow]", border_style="dark_green")
        table.add_column("ID", justify="center", style="yellow")
        table.add_column("Corrente (A)", justify="right", style="white")
        table.add_column("Operador", style="white")
        table.add_column("Data", style="white")
        for r in rows:
            operador = r.get('operador_nome') or (f"ID {r['operador_id']}" if r.get('operador_id') else "-")
            table.add_row(
                str(r["id"]),
                f"{float(r['corrente_a']):.6f} A",
                operador,
                str(r.get("timestamp_leitura", ""))[:19].replace("T", " ")
            )
        console.print(table)
        
    elif alvo == "radar":
        rows = api_historico("distancia", limite)
        if not rows: return print_warning("Nenhum registro de radar encontrado.")
        table = Table(title=f"[yellow]Histórico Radar M2-C (Últimos {limite})[/yellow]", border_style="dark_green")
        table.add_column("ID", justify="center", style="yellow")
        table.add_column("Frente", justify="right", style="white")
        table.add_column("Trás", justify="right", style="white")
        table.add_column("Esquerda", justify="right", style="white")
        table.add_column("Direita", justify="right", style="white")
        table.add_column("Data", style="white")
        for r in rows:
            table.add_row(str(r["id"]), f"{float(r['distancia_frente_m']):.2f}m", f"{float(r['distancia_tras_m']):.2f}m", f"{float(r['distancia_esq_m']):.2f}m", f"{float(r['distancia_dir_m']):.2f}m", str(r.get("timestamp_leitura", ""))[:19].replace("T", " "))
        console.print(table)
    else:
        print_error(f"Alvo '/history {alvo}' não reconhecido.")

def processar_cmd_log(cmd_lower):
    logs = api_logs()
    if not logs:
        return print_error("Não foi possível carregar os logs gerais.")
    
    t_usuarios = len(logs.get("usuarios", []))
    t_bombas = len(logs.get("bombas", []))
    t_z = len(logs.get("movimentacao_z", []))
    t_xy = len(logs.get("movimentacao_xy", []))
    t_corrente = len(logs.get("leituras_corrente", []))
    t_distancia = len(logs.get("leituras_distancia", []))
    
    table = Table(title="[bold yellow]📊 Resumo Geral do Banco de Dados[/bold yellow]", border_style="dark_green", expand=False)
    table.add_column("Tabela", style="white")
    table.add_column("Total de Registros", justify="right", style="yellow")
    
    table.add_row("Usuarios", str(t_usuarios))
    table.add_row("Bombas", str(t_bombas))
    table.add_row("Movimentacao Z", str(t_z))
    table.add_row("Movimentacao XY", str(t_xy))
    table.add_row("Leituras Corrente", str(t_corrente))
    table.add_row("Leituras Distancia", str(t_distancia))
    
    console.print(table)
    print_info("Para ver detalhes, acesse as rotas do backend ou use /history <alvo>.")

from rich.box import ROUNDED

# ==========================================
# MENUS & INTERFACE PRINCIPAL
# ==========================================
def print_header(bomba):
    header_content = (
        f"[bold yellow]G06 Super CLI[/bold yellow] [white]v1.0.0[/white]\n"
        f"Alvo Selecionado: Bomba #{BOMBA_ID} ({bomba['nome']}) - {bomba.get('localizacao', 'N/A')}\n\n"
        f"Tip: Type [bold yellow]/help[/bold yellow] to see available commands."
    )
    
    console.print(Panel(header_content, border_style="dark_green", box=ROUNDED, padding=(1, 2), width=90))
    console.print()
    
    console.print("  [yellow]💡[/yellow] [dim white]System loaded: M1-A, M1-B, M2-A, M2-B, M2-C[/dim white]\n")

def print_help():
    t = Table(title="📘 Lista de Atalhos e Comandos (/)", title_style="bold yellow", border_style="dark_green", expand=True)
    t.add_column("Sistema", style="yellow", justify="right")
    t.add_column("Ações Rápidas", style="white")
    
    t.add_row("Torno Z (Profundidade)", "[white]/z down <cm>[/white] | [white]/z up <cm>[/white] | [white]/z status[/white] | [white]/z reset[/white]")
    t.add_row("Balsa XY (Horizontal)", "[white]/balsa on[/white] | [white]/balsa off[/white] | [white]/balsa esq[/white] | [white]/balsa dir[/white] | [white]/balsa frente[/white] | [white]/balsa tras[/white] | [white]/balsa stop[/white]")
    t.add_row("Sensores (Corrente)", "[white]/corrente[/white] (Checar Segurança/Amperagem)")
    t.add_row("Radar M2-C (Distância)", "[white]/radar[/white] (Monitoramento Contínuo) | [white]/radar last[/white] (Foto de Momento)")
    t.add_row("Sensores Proximidade", "[white]/sensor status[/white] | [white]/sensor limiares[/white] | [white]/sensor limiares <I> <A> <C>[/white]")
    t.add_row("Câmera M2-B (Vídeo)", "[white]/cam[/white] (Live Feed OpenCV)")
    t.add_row("Logs e Históricos", "[white]/log[/white] (Resumo Geral) | [white]/history z <n>[/white] | [white]/history balsa <n>[/white] | [white]/history corrente[/white] | [white]/history radar[/white]")
    t.add_row("Conectividade ESP", "[white]/hb[/white] (Status heartbeat de todos os módulos)")
    t.add_row("Modo Automático Z", "[white]/auto on[/white] | [white]/auto off[/white] | [white]/auto status[/white]")
    t.add_row("Config da Bomba", "[white]/config[/white] (ver) | [white]/config set campo=valor[/white] (campos: diametro, corda, inf, sup, passo, p_frente, p_tras, p_esq, p_dir)")
    t.add_row("Geral", "[white]/info[/white] (Detalhes da Bomba) | [white]/clear[/white] (Limpar Tela) | [white]/exit[/white] ou [white]/quit[/white]")
    
    console.print(t)

def main():
    global posicao_atual_cm, DIAMETRO_CARRETEL_CM, COMPRIMENTO_CORDA_CM
    global TOKEN, USUARIO_ID, USUARIO_NOME, BOMBA_ID

    parser = argparse.ArgumentParser(description="Super CLI - Moderno G06")
    parser.add_argument("--bomba", type=int, help="ID da bomba", default=None)
    args = parser.parse_args()
    BOMBA_ID = args.bomba

    console.clear()
    
    if BOMBA_ID is None:
        BOMBA_ID = IntPrompt.ask("[bold cyan]Qual o ID da Bomba a ser visualizada?[/bold cyan]", default=1)

    # Login
    tentativas = 3
    login_data = None
    while tentativas > 0:
        login_data = api_login()
        if login_data: break
        tentativas -= 1
        if tentativas > 0: print_warning(f"Tentativas restantes: {tentativas}")

    if not login_data:
        print_error("Acesso bloqueado.")
        return

    TOKEN = login_data["token"]
    USUARIO_ID = login_data["usuario_id"]
    USUARIO_NOME = login_data["nome"]

    bomba = api_carregar_bomba()
    if not bomba:
        print_error(f"Bomba #{BOMBA_ID} não existe na base ou backend inacessível.")
        return

    DIAMETRO_CARRETEL_CM = float(bomba["diametro_carretel_cm"])
    COMPRIMENTO_CORDA_CM = float(bomba["comprimento_corda_cm"])

    # Carrega contexto
    orfaos_z = api_fechar_orfaos_z()
    if orfaos_z["total"] > 0: print_info(f"Limpeza de sessão: {orfaos_z['total']} operações Z abortadas.")
    
    orfaos_xy = api_fechar_orfaos_xy()
    if orfaos_xy["total"] > 0: print_info(f"Limpeza de sessão: {orfaos_xy['total']} operações XY abortadas.")

    estado_z = api_recuperar_posicao_z()
    if estado_z and estado_z.get("posicao_cm") is not None:
        posicao_atual_cm = estado_z["posicao_cm"]
    else:
        posicao_atual_cm = 0.0

    console.clear()
    print_header(bomba)
    
    style = Style.from_dict({
        'prompt': 'bold white',
    })
    session = PromptSession()

    while True:
        try:
            comando = session.prompt([('class:prompt', '⟩ ')], style=style).strip()
        except KeyboardInterrupt:
            comando = "sair"
        except EOFError:
            comando = "sair"

        if not comando: continue
        cmd_lower = comando.lower()

        if cmd_lower in ["/sair", "/exit", "/quit", "sair", "exit", "quit"]:
            if sistema_ligado_xy and registro_ativo_id_xy:
                api_enviar_comando_xy("parar")
                api_finalizar_movimento_xy("INTERROMPIDO")
            console.print("[dim]Desconectando...[/dim]")
            break
            
        elif cmd_lower in ["/clear", "clear"]:
            console.clear()
            print_header(bomba)
            
        elif cmd_lower in ["/help", "help", "?", "ajuda"]:
            print_help()
            
        elif cmd_lower in ["/info", "db info"]:
            db_bomba = api_carregar_bomba()
            if not db_bomba:
                print_error("Não foi possível carregar os dados da bomba.")
            else:
                panel = Panel.fit(
                    f"[bold yellow]ID:[/bold yellow] [white]{BOMBA_ID}[/white]\n"
                    f"[bold yellow]Nome:[/bold yellow] [white]{db_bomba['nome']}[/white]\n"
                    f"[bold yellow]Local:[/bold yellow] [white]{db_bomba.get('localizacao', 'N/A')}[/white]\n"
                    f"[bold yellow]Hardware:[/bold yellow] [white]Carretel {DIAMETRO_CARRETEL_CM}cm | Corda: {COMPRIMENTO_CORDA_CM}cm[/white]\n"
                    f"[bold yellow]Log Operacional:[/bold yellow] [white]{db_bomba.get('total_operacoes_z', 0)}x(Z) | {db_bomba.get('total_operacoes_xy', 0)}x(XY)[/white]",
                    title="[yellow]⚙️ Informações do Host[/yellow]",
                    border_style="dark_green"
                )
                console.print(panel)

        elif cmd_lower in ["/hb", "/heartbeat", "hb"]:
            processar_cmd_hb()

        elif cmd_lower.startswith("/auto"):
            processar_cmd_auto(cmd_lower)

        elif cmd_lower.startswith("/config"):
            processar_cmd_config(cmd_lower)
            
        elif cmd_lower.startswith("/history") or cmd_lower.startswith("/historico"):
            processar_cmd_history(cmd_lower)
        elif cmd_lower.startswith("/z"):
            processar_cmd_z(cmd_lower, comando)
        elif cmd_lower.startswith("/balsa"):
            processar_cmd_xy(cmd_lower)
        elif cmd_lower.startswith("/corrente"):
            processar_cmd_sensores(cmd_lower, "/corrente", "Corrente")
        elif cmd_lower.startswith("/sensor"):
            processar_cmd_sensor(cmd_lower)
        elif cmd_lower.startswith("/radar"):
            processar_cmd_sensores(cmd_lower, "/radar", "Sensores Ultrassônicos")
        elif cmd_lower.startswith("/cam"):
            processar_cmd_cam(cmd_lower)
        elif cmd_lower in ["/log", "log", "/logs", "logs"]:
            processar_cmd_log(cmd_lower)
        else:
            print_error("Comando desconhecido. Digite [bold white]/help[/bold white] para listar as ações possíveis.")

if __name__ == "__main__":
    main()
