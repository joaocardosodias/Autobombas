from backend.db.connection import get_db
from backend.models.leitura_distancia import LeituraDistanciaCreate


def criar(dados: LeituraDistanciaCreate) -> dict:
    with get_db() as cur:
        cur.execute("""
            INSERT INTO leituras_distancia
                (bomba_id, operador_id, distancia_frente_m, distancia_tras_m, distancia_esq_m, distancia_dir_m)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *;
        """, (
            dados.bomba_id, dados.operador_id,
            dados.distancia_frente_m,
            dados.distancia_tras_m,
            dados.distancia_esq_m,
            dados.distancia_dir_m
        ))
        return cur.fetchone()


def listar_por_bomba(bomba_id: int, limite: int = 10) -> list[dict]:
    with get_db() as cur:
        cur.execute("""
            SELECT ld.*, u.name AS operador_nome
            FROM leituras_distancia ld
            JOIN usuarios u ON u.id = ld.operador_id
            WHERE ld.bomba_id = %s
            ORDER BY ld.timestamp_leitura DESC
            LIMIT %s;
        """, (bomba_id, limite))
        return cur.fetchall()


def ultima_leitura(bomba_id: int) -> dict | None:
    with get_db() as cur:
        cur.execute("""
            SELECT ld.*, u.name AS operador_nome
            FROM leituras_distancia ld
            JOIN usuarios u ON u.id = ld.operador_id
            WHERE ld.bomba_id = %s
            ORDER BY ld.timestamp_leitura DESC
            LIMIT 1;
        """, (bomba_id,))
        return cur.fetchone()
