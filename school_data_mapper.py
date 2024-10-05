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
                ncessch VARCHAR(12),
                name VARCHAR(255),
                lstreet VARCHAR(255),
                lcity VARCHAR(100),
                lstate VARCHAR(2),
                lzip VARCHAR(5),
                lzip4 VARCHAR(4),
                type INTEGER,
                status INTEGER,
                union VARCHAR(3),
                ulocal INTEGER,
                latcod NUMERIC(10, 7),
                loncod NUMERIC(10, 7)
            )
        """)
        conn.commit()

def insert_data(conn, data):
    """Insert data into the schools table."""
    with conn.cursor() as cur:
        insert_query = sql.SQL("""
            INSERT INTO schools (ncessch, name, lstreet, lcity, lstate, lzip, lzip4, type, status, union, ulocal, latcod, loncod)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """)
        cur.executemany(insert_query, data)
        conn.commit()

def extract_and_map_data():
    """Extract data from CSV and map it to the database."""
    conn = connect_to_db()
    if not conn:
        return

    create_table(conn)

    with open('schools.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header row
        data = []
        for row in csv_reader:
            # Convert empty strings to None for numeric fields
            processed_row = [
                row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                int(row[7]) if row[7] else None,
                int(row[8]) if row[8] else None,
                row[9],
                int(row[10]) if row[10] else None,
                float(row[11]) if row[11] else None,
                float(row[12]) if row[12] else None
            ]
            data.append(tuple(processed_row))

    insert_data(conn, data)
    print(f"Inserted {len(data)} rows into the database.")

    # Generate and print the report
    generate_report_by_state(conn)

    conn.close()

def generate_report_by_state(conn):
    """Generate a report of the schools by state."""
    with conn.cursor() as cur:
        cur.execute("SELECT lstate, COUNT(*) AS school_count FROM schools GROUP BY lstate ORDER BY school_count DESC")
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
