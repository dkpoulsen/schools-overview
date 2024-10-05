from flask import Flask, jsonify, request
from school_data_mapper import connect_to_db
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

@app.route('/api/schools', methods=['GET'])
def get_schools():
    conn = connect_to_db()
    if not conn:
        return jsonify({"error": "Unable to connect to the database"}), 500

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) FROM schools")
            total_count = cur.fetchone()['count']

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
            "total_pages": (total_count + per_page - 1) // per_page
        }

        return jsonify(result)

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
