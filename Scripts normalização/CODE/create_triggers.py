import psycopg2
from DML.config import DB_CONFIG
 
def create_triggers():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SET search_path TO public;")
    conn.commit()
    
    cur.execute("""
        -- COLA O CODIGO AQUI POR FAVOR!
        """
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Triggers criadas com sucesso.")
 
 