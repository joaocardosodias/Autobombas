import os
import sys
from datetime import datetime

from dotenv import load_dotenv
import psycopg2

# Carrega o .env da raiz do projeto
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

dsn = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_URL")
if not dsn:
    print("ERRO: Nenhuma URL de banco encontrada nas variáveis de ambiente.")
    sys.exit(1)

# --- 1. Testar conexão ---
print("Tentando conectar ao banco de dados...")
try:
    conn = psycopg2.connect(dsn)
    conn.autocommit = False
    cur = conn.cursor()
    print("Conexao estabelecida com sucesso!\n")
except Exception as e:
    print(f"ERRO: Falha na conexao: {e}")
    sys.exit(1)



# --- Encerrar ---
cur.close()
conn.close()
print("\nConexao encerrada.")
