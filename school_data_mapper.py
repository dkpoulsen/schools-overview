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

# Make the connect_to_db function available for import
__all__ = ['connect_to_db']

def create_table(conn):
    """Create the schools table if it doesn't exist."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schools (
                id SERIAL PRIMARY KEY,
                hovedskole_inst VARCHAR(10) NULL,
                inst_nr VARCHAR(10) NULL,
                inst_navn VARCHAR(255) NULL,
                enhedsart VARCHAR(50) NULL,
                inst_adr VARCHAR(255) NULL,
                postnr VARCHAR(10) NULL,
                postdistrikt VARCHAR(100) NULL,
                tlf_nr VARCHAR(20) NULL,
                e_mail VARCHAR(255) NULL,
                web_adr VARCHAR(255) NULL,
                inst_type_nr VARCHAR(10) NULL,
                inst_type_navn VARCHAR(100) NULL,
                inst_type_gruppe VARCHAR(100) NULL,
                underv_niv VARCHAR(50) NULL,
                inst_leder VARCHAR(100) NULL,
                cvr_nr VARCHAR(20) NULL,
                kommune_nr VARCHAR(10) NULL,
                adm_kommune_navn VARCHAR(100) NULL,
                bel_kommune VARCHAR(10) NULL,
                bel_kommune_navn VARCHAR(100) NULL,
                bel_region VARCHAR(10) NULL,
                region_navn VARCHAR(100) NULL,
                ejer_kode VARCHAR(10) NULL,
                ejerkode_navn VARCHAR(100) NULL,
                p_nr VARCHAR(20) NULL,
                vejkode VARCHAR(10) NULL,
                geo_bredde_grad NUMERIC(10, 7) NULL,
                geo_laengde_grad NUMERIC(10, 7) NULL
            )
        """)
        conn.commit()

def insert_data(conn, data):
    """Insert data into the schools table."""
    with conn.cursor() as cur:
        insert_query = sql.SQL("""
            INSERT INTO schools (hovedskole_inst, inst_nr, inst_navn, enhedsart, inst_adr, postnr, postdistrikt, 
                                 tlf_nr, e_mail, web_adr, inst_type_nr, inst_type_navn, inst_type_gruppe, underv_niv, 
                                 inst_leder, cvr_nr, kommune_nr, adm_kommune_navn, bel_kommune, bel_kommune_navn, 
                                 bel_region, region_navn, ejer_kode, ejerkode_navn, p_nr, vejkode, geo_bredde_grad, 
                                 geo_laengde_grad)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """)
        # Filter out None values to avoid inserting NULL for empty strings
        filtered_data = [[None if val == '' else val for val in row] for row in data]
        cur.executemany(insert_query, filtered_data)
        conn.commit()

def extract_and_map_data():
    """Extract data from CSV and map it to the database."""
    conn = connect_to_db()
    if not conn:
        return

    create_table(conn)

    with open('schools.csv', 'r', encoding='utf-16-le', newline='') as file:
        csv_reader = csv.reader(file, delimiter=';')
        print("First few rows of the CSV file:")
        for i, row in enumerate(csv_reader):
            print(f"Row {i}: {row}")
            if i == 5:  # Print first 5 rows (including header)
                break
        
        # Reset file pointer to the beginning
        file.seek(0)
        next(csv_reader)  # Skip header row
        data = []
        rows_processed = 0
        for row in csv_reader:
            rows_processed += 1
            if len(row) < 28:
                print(f"Skipping row {rows_processed} with insufficient data: {row}")
                continue
            # Convert empty strings to None for all fields
            processed_row = [None if val.strip() == '' else val.strip() for val in row[:26]]
            # Handle numeric fields separately
            processed_row.extend([
                float(row[26].replace(',', '.')) if row[26].strip() else None,
                float(row[27].replace(',', '.')) if row[27].strip() else None
            ])
            data.append(tuple(processed_row))
        
        print(f"Total rows read: {rows_processed}")
        print(f"Total rows processed: {len(data)}")

    insert_data(conn, data)
    print(f"Inserted {len(data)} rows into the database.")

    # Generate and print the report
    generate_report_by_region(conn)

    conn.close()

def generate_report_by_region(conn):
    """Generate a report of the schools by region."""
    with conn.cursor() as cur:
        cur.execute("SELECT region_navn, COUNT(*) AS school_count FROM schools GROUP BY region_navn ORDER BY school_count DESC")
        rows = cur.fetchall()

    school_counts_by_region = defaultdict(int)
    for region, count in rows:
        school_counts_by_region[region or "Unknown"] = count

    print("Schools by Region:")
    print("-" * 50)
    print("{:<30} {:<10}".format("Region", "Schools"))
    print("-" * 50)

    for region, count in sorted(school_counts_by_region.items(), key=lambda x: x[1], reverse=True):
        print("{:<30} {:<10}".format(region or "Unknown", count))
    print("-" * 50)

if __name__ == "__main__":
    extract_and_map_data()
