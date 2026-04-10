from backend.db.connection import get_db
from backend.models.bomba import BombaConfigUpdate

# Limite padrão de proximidade quando não configurado no banco
DIST_MINIMA_PADRAO_M = 0.30


def listar_todas() -> list:
    with get_db() as cur:
        cur.execute("SELECT id, nome, localizacao FROM bombas ORDER BY id;")
        return cur.fetchall()


def buscar_por_id(bomba_id: int) -> dict | None:
    with get_db() as cur:
        cur.execute("""
            SELECT b.*,
                   COALESCE(z.total, 0) AS total_operacoes_z,
                   COALESCE(xy.total, 0) AS total_operacoes_xy
            FROM bombas b
            LEFT JOIN (
                SELECT bomba_id, COUNT(*) AS total
                FROM movimentacao_z GROUP BY bomba_id
            ) z ON z.bomba_id = b.id
            LEFT JOIN (
                SELECT bomba_id, COUNT(*) AS total
                FROM movimentacao_xy GROUP BY bomba_id
            ) xy ON xy.bomba_id = b.id
            WHERE b.id = %s;
        """, (bomba_id,))
        return cur.fetchone()


def atualizar_config(bomba_id: int, dados: BombaConfigUpdate) -> dict | None:
    """Atualiza apenas os campos fornecidos (partial update)."""
    campos = {
        "diametro_carretel_cm": dados.diametro_carretel_cm,
        "comprimento_corda_cm": dados.comprimento_corda_cm,
        "limite_inferior":      dados.limite_inferior,
        "limite_superior":      dados.limite_superior,
        "passo_auto_cm":        dados.passo_auto_cm,
        "limite_prox_frente_m": dados.limite_prox_frente_m,
        "limite_prox_tras_m":   dados.limite_prox_tras_m,
        "limite_prox_esq_m":    dados.limite_prox_esq_m,
        "limite_prox_dir_m":    dados.limite_prox_dir_m,
    }
    atualizacoes = {k: v for k, v in campos.items() if v is not None}
    if not atualizacoes:
        return None

    set_clause = ", ".join(f"{col} = %s" for col in atualizacoes)
    valores = list(atualizacoes.values()) + [bomba_id]

    with get_db() as cur:
        cur.execute(
            f"UPDATE bombas SET {set_clause} WHERE id = %s RETURNING *;",
            valores,
        )
        return cur.fetchone()


def get_limite_proximidade(bomba_id: int) -> dict:
    """Retorna os limites de proximidade configuraods para cada direção."""
    bomba = buscar_por_id(bomba_id)
    if not bomba:
        return {d: DIST_MINIMA_PADRAO_M for d in ("frente", "tras", "esq", "dir")}
    return {
        "frente": float(bomba["limite_prox_frente_m"] or DIST_MINIMA_PADRAO_M),
        "tras":   float(bomba["limite_prox_tras_m"]   or DIST_MINIMA_PADRAO_M),
        "esq":    float(bomba["limite_prox_esq_m"]    or DIST_MINIMA_PADRAO_M),
        "dir":    float(bomba["limite_prox_dir_m"]    or DIST_MINIMA_PADRAO_M),
    }
