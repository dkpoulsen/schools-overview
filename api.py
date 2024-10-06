from flask import Flask, jsonify, request, render_template
from school_data_mapper import connect_to_db
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

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

@app.route('/map')
def map_page():
    return render_template('map.html')

@app.route('/api/school_locations')
def get_school_locations():
    conn = connect_to_db()
    if not conn:
        return jsonify({"error": "Unable to connect to the database"}), 500

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, inst_navn, geo_bredde_grad, geo_laengde_grad, inst_type_navn FROM schools WHERE geo_bredde_grad IS NOT NULL AND geo_laengde_grad IS NOT NULL")
            schools = cur.fetchall()

        return jsonify(schools)

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()

def get_paginated_schools(cur, page, per_page, search_term=None):
    offset = (page - 1) * per_page

    if search_term:
        cur.execute("SELECT COUNT(*) FROM schools WHERE name ILIKE %s", (f'%{search_term}%',))
        total_count = cur.fetchone()['count']

        cur.execute("""
            SELECT * FROM schools
            WHERE name ILIKE %s
            ORDER BY id
            LIMIT %s OFFSET %s
        """, (f'%{search_term}%', per_page, offset))
    else:
        cur.execute("SELECT COUNT(*) FROM schools")
        total_count = cur.fetchone()['count']

        cur.execute("""
            SELECT * FROM schools
            ORDER BY id
            LIMIT %s OFFSET %s
        """, (per_page, offset))

    schools = cur.fetchall()
    total_pages = (total_count + per_page - 1) // per_page

    return schools, total_count, total_pages

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
            return jsonify(school)
        else:
            return jsonify({"error": "School not found"}), 404

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/schools', methods=['GET'])
def get_schools():
    conn = connect_to_db()
    if not conn:
        return jsonify({"error": "Unable to connect to the database"}), 500

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_term = request.args.get('search', None)

    # Error handling for invalid page and per_page values
    if page < 1:
        return jsonify({"error": "Page number must be 1 or greater"}), 400
    if per_page < 1 or per_page > 100:
        return jsonify({"error": "Per page value must be between 1 and 100"}), 400

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            schools, total_count, total_pages = get_paginated_schools(cur, page, per_page, search_term)

            # Check if the requested page is out of range
            if page > total_pages:
                return jsonify({"error": f"Page {page} does not exist. Total pages: {total_pages}"}), 404

        result = {
            "schools": schools,
            "page": page,
            "per_page": per_page,
            "total_count": total_count,
            "total_pages": total_pages
        }

        return jsonify(result)

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
