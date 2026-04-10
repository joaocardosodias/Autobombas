from backend.db.connection import get_db


def buscar_por_email(email: str) -> dict | None:
    with get_db() as cur:
        cur.execute(
            "SELECT id, name, email, senha_hash, role FROM usuarios WHERE email = %s;",
            (email,)
        )
        return cur.fetchone()


def buscar_por_id(usuario_id: int) -> dict | None:
    with get_db() as cur:
        cur.execute(
            "SELECT id, name, email, role, created_at FROM usuarios WHERE id = %s;",
            (usuario_id,)
        )
        return cur.fetchone()
    
def listar_todos() -> list[dict]:
    with get_db() as cur:
        cur.execute(
            "SELECT id, name as nome, email, role, created_at FROM usuarios ORDER BY id DESC;"
        )
        return cur.fetchall()
    
def criar(nome: str, email: str, senha_hash: str, role: str) -> dict:
    with get_db() as cur:
        cur.execute(
            """
            INSERT INTO usuarios (name, email, senha_hash, role)
            VALUES (%s, %s, %s, %s)
            RETURNING id, name as nome, email, role, created_at;
            """,
            (nome, email, senha_hash, role)
        )
        return cur.fetchone()
    
def deletar(usuario_id: int) -> bool:
    with get_db() as cur:
        cur.execute("DELETE FROM usuarios WHERE id = %s RETURNING id;", (usuario_id,))
        return cur.fetchone() is not None