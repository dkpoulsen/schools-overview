import csv
import psycopg2
from psycopg2 import sql

def connect_to_db():
    """Connect to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname="schools_db",
            user="schools_user",
            password="schools_password",
            host="localhost",
            port="5432"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Unable to connect to the database: {e}")
        return None

def create_table(conn):
    """Create the schools table if it doesn't exist."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schools (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                address VARCHAR(255),
                city VARCHAR(100),
                state VARCHAR(50),
                zip_code VARCHAR(20)
            )
        """)
        conn.commit()

def insert_data(conn, data):
    """Insert data into the schools table."""
    with conn.cursor() as cur:
        insert_query = sql.SQL("""
            INSERT INTO schools (name, address, city, state, zip_code)
            VALUES (%s, %s, %s, %s, %s)
        """)
        cur.executemany(insert_query, data)
        conn.commit()

def extract_and_map_data():
    """Extract data from CSV and map it to the database."""
    conn = connect_to_db()
    if not conn:
        return

    create_table(conn)

    with open('schools.csv', 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header row
        data = [tuple(row) for row in csv_reader]

    insert_data(conn, data)
    print(f"Inserted {len(data)} rows into the database.")

    conn.close()

if __name__ == "__main__":
    extract_and_map_data()
