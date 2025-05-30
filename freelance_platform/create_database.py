import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    # u041fu043eu0434u043au043bu044eu0447u0435u043du0438u0435 u043a PostgreSQL u0431u0435u0437 u0443u043au0430u0437u0430u043du0438u044f u0431u0430u0437u044b u0434u0430u043du043du044bu0445
    conn = psycopg2.connect(
        user="postgres",
        password="postgres",
        host="127.0.0.1",
        port="5432"
    )
    
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    cursor = conn.cursor()
    
    # u041fu0440u043eu0432u0435u0440u043au0430 u0441u0443u0449u0435u0441u0442u0432u043eu0432u0430u043du0438u044f u0431u0430u0437u044b u0434u0430u043du043du044bu0445
    cursor.execute("SELECT datname FROM pg_database WHERE datname = 'freelance_db';")
    exists = cursor.fetchone()
    
    if not exists:
        # u0421u043eu0437u0434u0430u043du0438u0435 u0431u0430u0437u044b u0434u0430u043du043du044bu0445
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier('freelance_db')))
        print("u0411u0430u0437u0430 u0434u0430u043du043du044bu0445 'freelance_db' u0443u0441u043fu0435u0448u043du043e u0441u043eu0437u0434u0430u043du0430")
    else:
        print("u0411u0430u0437u0430 u0434u0430u043du043du044bu0445 'freelance_db' u0443u0436u0435 u0441u0443u0449u0435u0441u0442u0432u0443u0435u0442")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    try:
        create_database()
    except Exception as e:
        print(f"u041eu0448u0438u0431u043au0430: {e}")
