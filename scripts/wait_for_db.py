import time
import os
import psycopg2
from urllib.parse import urlparse

def wait_for_db():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not set. Skipping wait.")
        return

    result = urlparse(database_url)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    
    print(f"Waiting for database at {hostname}:{port}...")
    
    retries = 30
    while retries > 0:
        try:
            conn = psycopg2.connect(
                dbname=database,
                user=username,
                password=password,
                host=hostname,
                port=port
            )
            conn.close()
            print("Database is ready!")
            return
        except psycopg2.OperationalError:
            retries -= 1
            print(f"Database unavailable, waiting 1 second... ({retries} retries left)")
            time.sleep(1)
            
    raise Exception("Could not connect to the database after multiple retries.")

if __name__ == "__main__":
    wait_for_db()
