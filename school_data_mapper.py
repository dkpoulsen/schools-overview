import csv
import psycopg2
from psycopg2 import sql
from collections import defaultdict

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

    # Generate and print the report
    generate_report_by_state(conn)

    conn.close()

def generate_report_by_state(conn):
    """Generate a report of the schools by state."""
    with conn.cursor() as cur:
        cur.execute("SELECT state, COUNT(*) AS school_count FROM schools GROUP BY state ORDER BY school_count DESC")
        rows = cur.fetchall()

    school_counts_by_state = defaultdict(int)
    for state, count in rows:
        school_counts_by_state[state] = count

    print("Schools by State:")
    print("-" * 40)
    print("{:<20} {:<10}".format("State", "Schools"))
    print("-" * 40)

    for state, count in sorted(school_counts_by_state.items(), key=lambda x: x[1], reverse=True):
        print("{:<20} {:<10}".format(state, count))
    print("-" * 40)

if __name__ == "__main__":
    extract_and_map_data()
