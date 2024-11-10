from flask import Flask, jsonify, request, render_template
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)

def connect_to_db():
    return psycopg2.connect(
                database=os.environ.get('POSTGRES_DB'),
                user=os.environ.get('POSTGRES_USER'),
                password=os.environ.get('POSTGRES_PASSWORD'),
                host='127.0.0.1',
                port=5432
            )

@app.route('/api/inst_types')
def get_inst_types():
    conn = connect_to_db()
    if not conn:
        return jsonify({"error": "Unable to connect to the database"}), 500

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT DISTINCT inst_type_nr, inst_type_navn FROM schools ORDER BY inst_type_nr")
            inst_types = cur.fetchall()

        return jsonify(inst_types)

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()

@app.route('/api/kommune_list')
def get_kommune_list():
    conn = connect_to_db()
    if not conn:
        return jsonify({"error": "Unable to connect to the database"}), 500

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT DISTINCT adm_kommune_navn FROM schools ORDER BY adm_kommune_navn")
            kommune_list = [row['adm_kommune_navn'] for row in  cur.fetchall()]

        return jsonify(kommune_list)

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()

@app.route('/')
def map_page():
    return render_template('map.html')

@app.route('/api/school_locations')
def get_school_locations():
    conn = connect_to_db()
    if not conn:
        return jsonify({"error": "Unable to connect to the database"}), 500

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, inst_navn, geo_bredde_grad, geo_laengde_grad, inst_type_navn, adm_kommune_navn FROM schools WHERE geo_bredde_grad IS NOT NULL AND geo_laengde_grad IS NOT NULL")
            schools = cur.fetchall()

        return jsonify(schools)

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()


@app.route('/api/school/<int:school_id>', methods=['GET'])
def get_school(school_id):
    conn = connect_to_db()
    if not conn:
        return jsonify({"error": "Unable to connect to the database"}), 500

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM schools WHERE id = %s", (school_id,))
            school = cur.fetchone()

        if school:
            # Ensure the web_adr has the correct prefix
            if school['web_adr']:
                if not school['web_adr'].startswith(('http://', 'https://')):
                    school['web_adr'] = 'http://' + school['web_adr']
            return jsonify(school)
        else:
            return jsonify({"error": "School not found"}), 404

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)
