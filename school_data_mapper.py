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
                hovedskole_inst VARCHAR(10),
                inst_nr VARCHAR(10),
                inst_navn VARCHAR(255),
                enhedsart VARCHAR(50),
                inst_adr VARCHAR(255),
                postnr VARCHAR(10),
                postdistrikt VARCHAR(100),
                tlf_nr VARCHAR(20),
                e_mail VARCHAR(255),
                web_adr VARCHAR(255),
                inst_type_nr VARCHAR(10),
                inst_type_navn VARCHAR(100),
                inst_type_gruppe VARCHAR(100),
                underv_niv VARCHAR(50),
                inst_leder VARCHAR(100),
                cvr_nr VARCHAR(20),
                kommune_nr VARCHAR(10),
                adm_kommune_navn VARCHAR(100),
                bel_kommune VARCHAR(10),
                bel_kommune_navn VARCHAR(100),
                bel_region VARCHAR(10),
                region_navn VARCHAR(100),
                ejer_kode VARCHAR(10),
                ejerkode_navn VARCHAR(100),
                p_nr VARCHAR(20),
                vejkode VARCHAR(10),
                geo_bredde_grad NUMERIC(10, 7),
                geo_laengde_grad NUMERIC(10, 7)
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
        cur.executemany(insert_query, data)
        conn.commit()

def extract_and_map_data():
    """Extract data from CSV and map it to the database."""
    conn = connect_to_db()
    if not conn:
        return

    create_table(conn)

    with open('schools.csv', 'r', encoding='utf-16-le') as file:
        csv_reader = csv.reader(file, delimiter='\t')
        next(csv_reader)  # Skip header row
        data = []
        for row in csv_reader:
            # Convert empty strings to None for numeric fields
            processed_row = [
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19],
                row[20], row[21], row[22], row[23], row[24], row[25],
                float(row[26]) if row[26] else None,
                float(row[27]) if row[27] else None
            ]
            data.append(tuple(processed_row))

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
        school_counts_by_region[region] = count

    print("Schools by Region:")
    print("-" * 50)
    print("{:<30} {:<10}".format("Region", "Schools"))
    print("-" * 50)

    for region, count in sorted(school_counts_by_region.items(), key=lambda x: x[1], reverse=True):
        print("{:<30} {:<10}".format(region, count))
    print("-" * 50)

if __name__ == "__main__":
    extract_and_map_data()
