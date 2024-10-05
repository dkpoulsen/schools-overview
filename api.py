from flask import Flask, jsonify, request, render_template
from school_data_mapper import connect_to_db
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

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

    # Error handling for invalid page and per_page values
    if page < 1:
        return jsonify({"error": "Page number must be 1 or greater"}), 400
    if per_page < 1 or per_page > 100:
        return jsonify({"error": "Per page value must be between 1 and 100"}), 400

    offset = (page - 1) * per_page

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) FROM schools")
            total_count = cur.fetchone()['count']

            # Check if the requested page is out of range
            total_pages = (total_count + per_page - 1) // per_page
            if page > total_pages:
                return jsonify({"error": f"Page {page} does not exist. Total pages: {total_pages}"}), 404

            cur.execute("""
                SELECT * FROM schools
                ORDER BY id
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            schools = cur.fetchall()

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
