from backend.db.connection import get_db
from backend.models.leitura_corrente import LeituraCorrenteCreate


def criar(dados: LeituraCorrenteCreate) -> dict:
    with get_db() as cur:
        cur.execute("""
            INSERT INTO leituras_corrente (bomba_id, operador_id, corrente_a)
            VALUES (%s, %s, %s)
            RETURNING *;
        """, (dados.bomba_id, dados.operador_id, dados.corrente_a))
        return cur.fetchone()


def listar_por_bomba(bomba_id: int, limite: int = 10) -> list[dict]:
    with get_db() as cur:
        cur.execute("""
            SELECT lc.id, lc.bomba_id, lc.operador_id, lc.corrente_a, lc.timestamp_leitura,
                   u.name AS operador_nome
            FROM leituras_corrente lc
            LEFT JOIN usuarios u ON u.id = lc.operador_id
            WHERE lc.bomba_id = %s
            ORDER BY lc.timestamp_leitura DESC
            LIMIT %s;
        """, (bomba_id, limite))
        return cur.fetchall()


def ultima_leitura(bomba_id: int) -> dict | None:
    with get_db() as cur:
        cur.execute("""
            SELECT lc.id, lc.bomba_id, lc.operador_id, lc.corrente_a, lc.timestamp_leitura,
                   u.name AS operador_nome
            FROM leituras_corrente lc
            LEFT JOIN usuarios u ON u.id = lc.operador_id
            WHERE lc.bomba_id = %s
            ORDER BY lc.timestamp_leitura DESC
            LIMIT 1;
        """, (bomba_id,))
        return cur.fetchone()
