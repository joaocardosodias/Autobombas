import os
import sys
import bcrypt
import psycopg2
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

dsn = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_URL")
if not dsn:
    print("ERRO: Nenhuma URL de banco encontrada.")
    sys.exit(1)

conn = psycopg2.connect(dsn)
conn.autocommit = True
cur = conn.cursor()

# --- 1. Aplicar schema ---


schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
with open(schema_path, "r", encoding="utf-8") as f:
    cur.execute(f.read())
print("Schema aplicado.\n")

# --- Senhas hash ---
senha_gestor   = bcrypt.hashpw(b"gestor",   bcrypt.gensalt()).decode()
senha_operador = bcrypt.hashpw(b"operador", bcrypt.gensalt()).decode()

# --- 2. Gestor ---
cur.execute("""
    INSERT INTO usuarios (name, email, senha_hash, role)
    VALUES (%s, %s, %s, 'gestor')
    RETURNING id;
""", ("gestor", "gestor@gestor.com", senha_gestor))
gestor_id = cur.fetchone()[0]
print(f"Gestor criado   -> ID: {gestor_id} | email: gestor@gestor.com | senha: gestor")

# --- 3. Operador ---
cur.execute("""
    INSERT INTO usuarios (name, email, senha_hash, role)
    VALUES (%s, %s, %s, 'operador')
    RETURNING id;
""", ("operador", "operador@operador.com", senha_operador))
operador_id = cur.fetchone()[0]
print(f"Operador criado -> ID: {operador_id} | email: operador@operador.com | senha: operador")

# --- 4. Bomba ---
cur.execute("""
    INSERT INTO bombas (nome, localizacao, operador_id, diametro_carretel_cm, comprimento_corda_cm)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id;
""", ("Bomba 01", "Módulo 1-A", operador_id, 0.852, 35.0))
bomba_id = cur.fetchone()[0]
print(f"Bomba criada    -> ID: {bomba_id} | Módulo 1-A | Operador #{operador_id}\n")

print("=== Seed concluido ===")
print(f"  CLI: python3 cli.py --bomba {bomba_id}")

cur.close()
conn.close()
