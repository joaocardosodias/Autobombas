from backend.db.connection import get_db
from backend.models.movimentacao_z import MovimentacaoZCreate, MovimentacaoZUpdate


def criar(dados: MovimentacaoZCreate) -> dict:
    with get_db() as cur:
        cur.execute("""
            INSERT INTO movimentacao_z
                (bomba_id, operador_id, comando_bruto, posicao_inicial_cm,
                 deslocamento_solicitado_cm, voltas_mqtt, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'EM_ANDAMENTO')
            RETURNING *;
        """, (
            dados.bomba_id, dados.operador_id, dados.comando_bruto,
            dados.posicao_inicial_cm, dados.deslocamento_solicitado_cm,
            dados.voltas_mqtt
        ))
        return cur.fetchone()


def atualizar(registro_id: int, dados: MovimentacaoZUpdate) -> dict | None:
    with get_db() as cur:
        cur.execute("""
            UPDATE movimentacao_z
            SET status = %s,
                deslocamento_real_cm = %s,
                posicao_final_cm = %s,
                timestamp_fim = NOW()
            WHERE id = %s
            RETURNING *;
        """, (
            dados.status, dados.deslocamento_real_cm,
            dados.posicao_final_cm, registro_id
        ))
        return cur.fetchone()


def listar_por_bomba(bomba_id: int, limite: int = 10) -> list[dict]:
    with get_db() as cur:
        cur.execute("""
            SELECT mz.*, u.name AS operador_nome
            FROM movimentacao_z mz
            LEFT JOIN usuarios u ON u.id = mz.operador_id
            WHERE mz.bomba_id = %s
            ORDER BY mz.timestamp_inicio DESC
            LIMIT %s;
        """, (bomba_id, limite))
        return cur.fetchall()


def fechar_orfaos(bomba_id: int) -> list[int]:
    with get_db() as cur:
        cur.execute("""
            UPDATE movimentacao_z
            SET status = 'INTERROMPIDO', timestamp_fim = NOW()
            WHERE bomba_id = %s AND status = 'EM_ANDAMENTO'
            RETURNING id;
        """, (bomba_id,))
        return [r["id"] for r in cur.fetchall()]


def tem_movimento_em_andamento(bomba_id: int) -> bool:
    """Retorna True se existe registro de movimentação Z EM_ANDAMENTO para a bomba."""
    with get_db() as cur:
        cur.execute("""
            SELECT 1 FROM movimentacao_z
            WHERE bomba_id = %s AND status = 'EM_ANDAMENTO'
            LIMIT 1;
        """, (bomba_id,))
        return cur.fetchone() is not None


def recuperar_posicao(bomba_id: int) -> dict | None:
    with get_db() as cur:
        cur.execute("""
            SELECT posicao_final_cm, status, timestamp_fim
            FROM movimentacao_z
            WHERE bomba_id = %s
              AND status IN ('CONCLUIDO', 'ABORTADO', 'SNAPSHOT')
              AND posicao_final_cm IS NOT NULL
            ORDER BY timestamp_fim DESC
            LIMIT 1;
        """, (bomba_id,))
        return cur.fetchone()


def salvar_posicao_final(bomba_id: int, posicao_cm: float, operador_id: int) -> dict | None:
    """
    Grava a posicao final conhecida como um snapshot no DB.
    Usado quando o modo auto para ou quando timeout ocorre,
    garantindo que /z status reflete a realidade.
    """
    with get_db() as cur:
        # Fecha todos os EM_ANDAMENTO orphaos
        cur.execute("""
            UPDATE movimentacao_z
            SET status = 'INTERROMPIDO', timestamp_fim = NOW()
            WHERE bomba_id = %s AND status = 'EM_ANDAMENTO'
        """, (bomba_id,))
        # Insere um snapshot de posicao
        cur.execute("""
            INSERT INTO movimentacao_z
                (bomba_id, operador_id, comando_bruto,
                 posicao_inicial_cm, deslocamento_solicitado_cm,
                 deslocamento_real_cm, posicao_final_cm,
                 voltas_mqtt, status, timestamp_fim)
            VALUES (%s, %s, 'auto:snapshot', %s, 0, 0, %s, 0, 'SNAPSHOT', NOW())
            RETURNING *;
        """, (bomba_id, operador_id, posicao_cm, posicao_cm))
        return cur.fetchone()


def concluir_em_andamento(bomba_id: int) -> dict | None:
    """Marca o registro EM_ANDAMENTO mais recente como CONCLUIDO."""
    with get_db() as cur:
        cur.execute("""
            SELECT id, posicao_inicial_cm, deslocamento_solicitado_cm, comando_bruto
            FROM movimentacao_z
            WHERE bomba_id = %s AND status = 'EM_ANDAMENTO'
            ORDER BY timestamp_inicio DESC LIMIT 1;
        """, (bomba_id,))
        reg = cur.fetchone()
        if not reg:
            return None
        desl = float(reg["deslocamento_solicitado_cm"])
        pos_ini = float(reg["posicao_inicial_cm"])
        # SUBIR = subtrái, DESCER = soma
        if reg["comando_bruto"] == "SUBIR":
            pos_final = max(0.0, pos_ini - desl)
        else:
            pos_final = pos_ini + desl
        cur.execute("""
            UPDATE movimentacao_z
            SET status = 'CONCLUIDO',
                deslocamento_real_cm = %s,
                posicao_final_cm = %s,
                timestamp_fim = NOW()
            WHERE id = %s
            RETURNING *;
        """, (desl, pos_final, reg["id"]))
        return cur.fetchone()


def abortar_em_andamento(bomba_id: int, voltas_feitas: float) -> dict | None:
    """Marca o registro EM_ANDAMENTO mais recente como ABORTADO, calculando deslocamento real."""
    import math
    with get_db() as cur:
        cur.execute("""
            SELECT id, posicao_inicial_cm, comando_bruto
            FROM movimentacao_z
            WHERE bomba_id = %s AND status = 'EM_ANDAMENTO'
            ORDER BY timestamp_inicio DESC LIMIT 1;
        """, (bomba_id,))
        reg = cur.fetchone()
        if not reg:
            return None
        cur.execute("SELECT diametro_carretel_cm FROM bombas WHERE id = %s;", (bomba_id,))
        bomba = cur.fetchone()
        if not bomba:
            return None
        cm_real = abs(voltas_feitas) * float(bomba["diametro_carretel_cm"]) * math.pi
        pos_ini = float(reg["posicao_inicial_cm"])
        # SUBIR = subtrái, DESCER = soma
        if reg["comando_bruto"] == "SUBIR":
            pos_final = max(0.0, pos_ini - cm_real)
        else:
            pos_final = pos_ini + cm_real
        cur.execute("""
            UPDATE movimentacao_z
            SET status = 'ABORTADO',
                deslocamento_real_cm = %s,
                posicao_final_cm = %s,
                timestamp_fim = NOW()
            WHERE id = %s
            RETURNING *;
        """, (cm_real, pos_final, reg["id"]))
        return cur.fetchone()


def listar_sessoes_gestor(
    page: int = 1,
    page_size: int = 10,
    bomba_id: int | None = None,
    status: str | list[str] | None = None,
) -> tuple[list[dict], int]:
    offset = (page - 1) * page_size
    filtros = [
        "COALESCE(mz.comando_bruto, '') NOT ILIKE 'auto:%%'",
        "COALESCE(mz.comando_bruto, '') NOT ILIKE '%%snapshot%%'",
        "COALESCE(mz.comando_bruto, '') NOT ILIKE '%%reset%%'",
    ]
    params: list = []

    if bomba_id is not None:
        filtros.append("mz.bomba_id = %s")
        params.append(bomba_id)

    if status is not None:
        if isinstance(status, list):
            placeholders = ", ".join(["%s"] * len(status))
            filtros.append(f"mz.status IN ({placeholders})")
            params.extend(status)
        else:
            filtros.append("mz.status = %s")
            params.append(status)

    where_clause = "WHERE " + " AND ".join(filtros)

    with get_db() as cur:
        cur.execute(f"""
            SELECT COUNT(*)::int AS total
            FROM movimentacao_z mz
            {where_clause};
        """, tuple(params))
        total = cur.fetchone()["total"]

        params_paginados = [*params, page_size, offset]
        cur.execute(f"""
            SELECT
                mz.id,
                mz.bomba_id,
                u.name AS operador,
                mz.timestamp_inicio AS inicio,
                mz.timestamp_fim AS fim,
                CASE
                    WHEN mz.status = 'EM_ANDAMENTO' THEN 'Em Andamento'
                    WHEN mz.status = 'CONCLUIDO' THEN 'Finalizada'
                    ELSE 'Alerta'
                END AS status
            FROM movimentacao_z mz
            JOIN usuarios u ON u.id = mz.operador_id
            {where_clause}
            ORDER BY mz.timestamp_inicio DESC
            LIMIT %s OFFSET %s;
        """, tuple(params_paginados))
        itens = cur.fetchall()

    return itens, total


def buscar_resumo_sessao_gestor(registro_id: int) -> dict | None:
    with get_db() as cur:
        cur.execute("""
            SELECT
                mz.id,
                mz.bomba_id,
                u.name AS operador,
                mz.status,
                mz.timestamp_inicio,
                mz.timestamp_fim
            FROM movimentacao_z mz
            JOIN usuarios u ON u.id = mz.operador_id
            WHERE mz.id = %s
            LIMIT 1;
        """, (registro_id,))
        return cur.fetchone()

