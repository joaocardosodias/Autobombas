import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

dsn = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_URL")
if not dsn:
    raise RuntimeError("No database URL provided in environment variables")

conn = psycopg2.connect(dsn)
cur = conn.cursor()

with open("schema.sql", "r", encoding="utf-8") as file:
    sql = file.read()

cur.execute(sql)
conn.commit()

cur.close()
conn.close()
#
print("Banco criado")