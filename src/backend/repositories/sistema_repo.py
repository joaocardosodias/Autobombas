import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
 
from datetime import datetime, timedelta
from backend.db.connection import get_db
from backend.services import mqtt_service
 

JANELA_ATIVO_MINUTOS = 3

def get_status_sistema(bomba_id: int) -> dict:
    agora = datetime.now()
    limite = agora - timedelta(minutes=JANELA_ATIVO_MINUTOS)

    with get_db() as cur:
        # 1. Busca dados básicos da bomba
        cur.execute(
            "SELECT id, nome, localizacao FROM bombas WHERE id = %s",
            (bomba_id,)
        )
        bomba = cur.fetchone()
        
        if not bomba:
            return None

        # 2. Verifica ÚLTIMA MOVIMENTAÇÃO (XY)
        cur.execute("""
            SELECT timestamp_inicio 
            FROM movimentacao_xy 
            WHERE bomba_id = %s 
            ORDER BY timestamp_inicio DESC 
            LIMIT 1
        """, (bomba_id,))
        row_mov = cur.fetchone()
        
        # Pega o valor da coluna 'timestamp_inicio' se existir
        ultima_mov = row_mov["timestamp_inicio"] if row_mov else None
        mov_ativa = ultima_mov is not None and ultima_mov >= limite

        # 3. Verifica SENSOR DE CORRENTE
        cur.execute("""
            SELECT timestamp_leitura 
            FROM leituras_corrente 
            WHERE bomba_id = %s 
            ORDER BY timestamp_leitura DESC 
            LIMIT 1
        """, (bomba_id,))
        row_corrente = cur.fetchone()
        ultima_corrente = row_corrente["timestamp_leitura"] if row_corrente else None
        corrente_ativa = ultima_corrente is not None and ultima_corrente >= limite

        # 4. Verifica SENSOR DE DISTÂNCIA
        cur.execute("""
            SELECT timestamp_leitura 
            FROM leituras_distancia 
            WHERE bomba_id = %s 
            ORDER BY timestamp_leitura DESC 
            LIMIT 1
        """, (bomba_id,))
        row_dist = cur.fetchone()
        ultima_dist = row_dist["timestamp_leitura"] if row_dist else None
        dist_ativa = ultima_dist is not None and ultima_dist >= limite

        
        # Consideramos CONECTADO se houve qualquer sinal de vida (sensores ou movimento)
        sensores = [
            {
                "tipo": "corrente",
                "bomba_id": bomba_id,
                "ultima_leitura": ultima_corrente,
                "ativo": corrente_ativa,
            },
            {
                "tipo": "distancia",
                "bomba_id": bomba_id,
                "ultima_leitura": ultima_dist,
                "ativo": dist_ativa,
            }
        ]

        total_ativos = sum(1 for s in sensores if s["ativo"])

        conectado = total_ativos > 0
 
        return {
            "conectado": conectado,
            "timestamp": datetime.now(),
            "total_sensores_ativos": total_ativos,
            "sensores": sensores,
            "bomba_id": bomba["id"],
            "bomba_nome": bomba["nome"],
            "bomba_localizacao": bomba.get("localizacao"),
        }


def get_heartbeat_todos() -> list:
    """Retorna o estado de heartbeat de todos os módulos ESP."""
    return mqtt_service.get_heartbeat_status()


def get_heartbeat_modulo(tipo: str, modulo_id: int) -> dict | None:
    """Retorna o heartbeat de um módulo específico, ou None se desconhecido."""
    todos = mqtt_service.get_heartbeat_status()
    chave = f"{tipo}/{modulo_id}"
    for item in todos:
        if item["modulo"] == chave:
            return item
    return None