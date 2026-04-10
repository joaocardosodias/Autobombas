from backend.db.connection import get_db

def listar_atividades_consolidadas(
    page: int = 1,
    page_size: int = 10,
    bomba_id: int | None = None,
    status: str | None = None,
) -> tuple[list[dict], int]:
    
    offset = (page - 1) * page_size


    filtros_z = [
        "COALESCE(z.comando_bruto, '') NOT ILIKE 'auto:%%'", 
        "COALESCE(z.comando_bruto, '') NOT ILIKE '%%snapshot%%'"
    ]
    filtros_xy = ["1=1"] 
    params_z = []
    params_xy = []

    if bomba_id is not None:
        filtros_z.append("z.bomba_id = %s")
        params_z.append(bomba_id)
        filtros_xy.append("xy.bomba_id = %s")
        params_xy.append(bomba_id)

    if status and status != "all":
        filtros_z.append("z.status = %s")
        params_z.append(status)
        filtros_xy.append("xy.status = %s")
        params_xy.append(status)

    where_z = " AND ".join(filtros_z)
    where_xy = " AND ".join(filtros_xy)

    atividades = []
    total = 0

    with get_db() as cur:
        # --- BLOCO 1: COUNT SEGURO ---
        try:
            cur.execute(f"SELECT COUNT(*) FROM movimentacao_z z WHERE {where_z}", tuple(params_z))
            res_z = cur.fetchone()
            count_z = (res_z["count"] if isinstance(res_z, dict) else res_z[0]) if res_z else 0

            cur.execute(f"SELECT COUNT(*) FROM movimentacao_xy xy WHERE {where_xy}", tuple(params_xy))
            res_xy = cur.fetchone()
            count_xy = (res_xy["count"] if isinstance(res_xy, dict) else res_xy[0]) if res_xy else 0
            
            total = count_z + count_xy
        except Exception as e:
            print(f"[ERRO COUNT] {e}")

        # --- BLOCO 2: QUERY DE DADOS ---
        query_base = f"""
            SELECT 
                'z_' || id::text as id, bomba_id, 'MOVIMENTACAO_Z' as tipo, 
                timestamp_inicio as ts, timestamp_fim, status, operador_id, 
                posicao_inicial_cm as z_i, posicao_final_cm as z_f, NULL as direcao
            FROM movimentacao_z z 
            WHERE {where_z}
            
            UNION ALL
            
            SELECT 
                'xy_' || id::text as id, bomba_id, 'MOVIMENTACAO_XY' as tipo, 
                timestamp_inicio as ts, timestamp_fim, status, operador_id, 
                NULL as z_i, NULL as z_f, direcao
            FROM movimentacao_xy xy 
            WHERE {where_xy}
            
            ORDER BY ts DESC
            LIMIT %s OFFSET %s
        """
        
        # Sincronização rigorosa de parâmetros (Z primeiro, XY depois, Paginação por último)
        params_query = tuple(params_z + params_xy + [page_size, offset])
        
        try:
            # DEBUG: O número de %s deve ser igual ao len(params_query)
            # print(f"DEBUG: Query %s={query_base.count('%s')} | Params={len(params_query)}")
            
            cur.execute(query_base, params_query)
            linhas = cur.fetchall()

            for row in linhas:
                # Conversão universal para dicionário
                if not isinstance(row, dict):
                    colnames = [desc[0] for desc in cur.description]
                    d = dict(zip(colnames, row))
                else:
                    d = row

                # Busca do nome do operador isolada
                nome_op = "Sistema"
                if d.get("operador_id"):
                    cur.execute("SELECT name FROM usuarios WHERE id = %s", (d["operador_id"],))
                    u = cur.fetchone()
                    if u:
                        nome_op = u["name"] if isinstance(u, dict) else u[0]

                # Lógica de Descrição formatada
                if d["tipo"] == "MOVIMENTACAO_Z":
                    val_i = float(d.get("z_i") or 0)
                    val_f = float(d.get("z_f") or 0)
                    dist = val_f - val_i
                    sentido = "Desceu" if dist > 0 else "Subiu" if dist < 0 else "Movimentação"
                    desc = f"{sentido} {abs(dist):.1f}cm"
                else:
                    direcao = str(d.get("direcao") or "N/A").capitalize()
                    desc = f"Moveu balsa para {direcao}"

                atividades.append({
                    "id": d["id"],
                    "bomba_id": d["bomba_id"],
                    "tipo": d["tipo"],
                    "timestamp": d["ts"],
                    "timestamp_fim": d["timestamp_fim"],
                    "operador": nome_op,
                    "status": d["status"],
                    "descricao": desc,
                    "perigoso": d["status"] in ["ABORTADO", "INTERROMPIDO"]
                })

        except Exception as e:
            print(f"[ERRO LISTAGEM] {e}")
            import traceback
            traceback.print_exc()

    return atividades, total

def buscar_atividade_por_id(atividade_id: str) -> dict | None:
    if not atividade_id or "_" not in atividade_id:
        return None
        
    prefixo, real_id = atividade_id.split("_")
    tabela = "movimentacao_z" if prefixo == "z" else "movimentacao_xy"
    
    with get_db() as cur:
        try:
            cur.execute(f"SELECT * FROM {tabela} WHERE id = %s", (real_id,))
            reg = cur.fetchone()
            if not reg: return None
            
            if not isinstance(reg, dict):
                colnames = [desc[0] for desc in cur.description]
                r = dict(zip(colnames, reg))
            else:
                r = reg

            return {
                "id": atividade_id,
                "bomba_id": r.get("bomba_id"),
                "tipo": "MOVIMENTACAO_Z" if prefixo == "z" else "MOVIMENTACAO_XY",
                "timestamp": r.get("timestamp_inicio"),
                "timestamp_fim": r.get("timestamp_fim"),
                "status": r.get("status"),
                "operador": "Consultando...",
                "descricao": "Operação detalhada",
                "perigoso": r.get("status") in ["ABORTADO", "INTERROMPIDO"]
            }
        except Exception as e:
            print(f"[ERRO BUSCA ID] {e}")
            return None