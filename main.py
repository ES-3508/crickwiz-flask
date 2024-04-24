from flask import Flask, jsonify, request
import mysql.connector
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS on the Flask app
app = Flask(__name__)

# Configure database connection pool
dbconfig = {
    "host": "localhost",
    "user": "root",
    "password": "Achini@143",
    "database": "crickwiz"
}
pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool",
                                                   pool_size=5,
                                                   pool_reset_session=True,
                                                   **dbconfig)

def get_db_connection():
    try:
        conn = pool.get_connection()
        if conn.is_connected():
            print("Database connection successful")
        return conn
    except Exception as e:
        print(f"Error while connecting to MySQL from pool: {e}")
        return None

@app.route('/bowling', methods=['GET'])
def get_bowling_data():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        base_query = "SELECT * FROM bowling WHERE 1=1"
        query_params = []
        allowed_params = ["Id", "match_id", "team", "opposite_team", "player", "profile_url",
                          "overs", "maidens", "runs", "wickets", "economy_rate", "dot", "fours",
                          "sixes", "wide_balls", "no_balls", "bowling_position", "created_at", "updated_at"]
        for param, value in request.args.items():
            if param in allowed_params:
                base_query += f" AND {param} = %s"
                query_params.append(value)
        cursor.execute(base_query, query_params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows), 200
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/batsmen', methods=['GET'])
def get_batsmen_data():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        base_query = "SELECT * FROM batting WHERE 1=1"
        query_params = []
        for param, value in request.args.items():
            if param in ["Id", "match_id", "team", "opposite_team", "player", "profile_url", "batting_position", "captain",
                         "wicket_keeper", "dismissal_method", "bowler", "dismissal_participate_player", "runs", "balls",
                         "minutes", "fours", "sixes", "strike_rate", "created_at", "updated_at"]:
                base_query += f" AND {param} = %s"
                query_params.append(value)
        cursor.execute(base_query, query_params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows), 200
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/wickets', methods=['GET'])
def get_bowling_wickets():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        base_query = "SELECT * FROM bowling_wickets WHERE 1=1"
        query_params = []
        for param, value in request.args.items():
            if param in ["Id", "match_id", "team", "opposite_team", "player", "profile_url", "bowling_position", "overs",
                         "out_player", "runs", "wicket_position", "total_wickets", "created_at", "updated_at"]:
                base_query += f" AND {param} = %s"
                query_params.append(value)
        cursor.execute(base_query, query_params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows), 200
    else:
        return jsonify({"error": "Database connection failed"}), 500


@app.route('/unique-batsmen', methods=['GET'])
def get_unique_batsmen():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT DISTINCT player FROM batting"
        cursor.execute(query)
        batsmen = [row['player'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify(batsmen), 200
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/unique-bowlers', methods=['GET'])
def get_unique_bowlers():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT DISTINCT player FROM bowling"
        cursor.execute(query)
        bowlers = [row['player'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify(bowlers), 200
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/unique-countries', methods=['GET'])
def get_unique_countries():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        # This assumes you have a 'team' column in both 'batting' and 'bowling' tables
        query = """
        SELECT DISTINCT team FROM (
            SELECT team FROM batting
            UNION
            SELECT team FROM bowling
        ) AS combined_teams
        """
        cursor.execute(query)
        countries = [row['team'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify(countries), 200
    else:
        return jsonify({"error": "Database connection failed"}), 500


if __name__ == '__main__':
    app.run(debug=True)
