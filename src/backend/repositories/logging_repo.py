from backend.db.connection import get_db

def buscar_todos_os_dados() -> dict:
    """Busca todas as informacoes do banco de dados (todas as tabelas)."""
    with get_db() as cur:
        # 1. Usuarios
        cur.execute("SELECT id, name, email, role, created_at, updated_at FROM usuarios;")
        usuarios = cur.fetchall()

        # 2. Bombas
        cur.execute("SELECT * FROM bombas;")
        bombas = cur.fetchall()

        # 3. Movimentacao Z
        cur.execute("SELECT * FROM movimentacao_z;")
        movimentacao_z = cur.fetchall()

        # 4. Movimentacao XY
        cur.execute("SELECT * FROM movimentacao_xy;")
        movimentacao_xy = cur.fetchall()

        # 5. Leituras Corrente
        cur.execute("SELECT * FROM leituras_corrente;")
        leituras_corrente = cur.fetchall()

        # 6. Leituras Distancia
        cur.execute("SELECT * FROM leituras_distancia;")
        leituras_distancia = cur.fetchall()

    return {
        "usuarios": usuarios,
        "bombas": bombas,
        "movimentacao_z": movimentacao_z,
        "movimentacao_xy": movimentacao_xy,
        "leituras_corrente": leituras_corrente,
        "leituras_distancia": leituras_distancia
    }
