from backend.db.connection import get_db
from backend.models.movimentacao_xy import MovimentacaoXYCreate, MovimentacaoXYUpdate


def criar(dados: MovimentacaoXYCreate) -> dict:
    with get_db() as cur:
        cur.execute("""
            INSERT INTO movimentacao_xy
                (bomba_id, operador_id, direcao, status)
            VALUES (%s, %s, %s, 'EM_ANDAMENTO')
            RETURNING *;
        """, (dados.bomba_id, dados.operador_id, dados.direcao))
        return cur.fetchone()


def atualizar(registro_id: int, dados: MovimentacaoXYUpdate) -> dict | None:
    with get_db() as cur:
        cur.execute("""
            UPDATE movimentacao_xy
            SET status = %s,
                duracao_ms = %s,
                timestamp_fim = NOW()
            WHERE id = %s
            RETURNING *;
        """, (dados.status, dados.duracao_ms, registro_id))
        return cur.fetchone()


def listar_por_bomba(bomba_id: int, limite: int = 10) -> list[dict]:
    with get_db() as cur:
        cur.execute("""
            SELECT mx.*, u.name AS operador_nome
            FROM movimentacao_xy mx
            JOIN usuarios u ON u.id = mx.operador_id
            WHERE mx.bomba_id = %s
            ORDER BY mx.timestamp_inicio DESC
            LIMIT %s;
        """, (bomba_id, limite))
        return cur.fetchall()


def fechar_orfaos(bomba_id: int) -> list[int]:
    with get_db() as cur:
        cur.execute("""
            UPDATE movimentacao_xy
            SET status = 'INTERROMPIDO', timestamp_fim = NOW()
            WHERE bomba_id = %s AND status = 'EM_ANDAMENTO'
            RETURNING id;
        """, (bomba_id,))
        return [r["id"] for r in cur.fetchall()]


def tem_em_andamento(bomba_id: int) -> bool:
    """Retorna True se há movimentação XY EM_ANDAMENTO para essa bomba."""
    with get_db() as cur:
        cur.execute("""
            SELECT 1 FROM movimentacao_xy
            WHERE bomba_id = %s AND status = 'EM_ANDAMENTO'
            LIMIT 1;
        """, (bomba_id,))
        return cur.fetchone() is not None


def buscar_em_andamento(bomba_id: int) -> list[dict]:
    """Retorna a lista de movimentações XY EM_ANDAMENTO para essa bomba."""
    with get_db() as cur:
        cur.execute("""
            SELECT * FROM movimentacao_xy
            WHERE bomba_id = %s AND status = 'EM_ANDAMENTO';
        """, (bomba_id,))
        return cur.fetchall()

