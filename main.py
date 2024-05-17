from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv

load_dotenv()  # This will load environment variables from .env file

app = Flask(__name__)
CORS(app)

# Configure database connection pool using environment variables
dbconfig = {
    "host": os.getenv("DATABASE_HOST"),
    "user": os.getenv("DATABASE_USER"),
    "password": os.getenv("DATABASE_PASSWORD"),
    "database": os.getenv("DATABASE_NAME")
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


@app.route('/api/bowling', methods=['GET'])
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


@app.route('/api/batsmen', methods=['GET'])
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
#Get teams ffrom
@app.route('/api/matches', methods=['GET'])
def get_average_run_rates():
    # Get the country parameter from the request
    country = request.args.get('country')

    # Check if the country parameter is provided
    if not country:
        return jsonify({"error": "Country parameter is missing"}), 400

    try:
        # Connect to the database
        connection = pool.get_connection()
        if connection.is_connected():
            # Create a cursor to execute SQL queries
            cursor = connection.cursor()

            # Query to get the average run rate for each year for the specified country
            query = """
                SELECT YEAR(STR_TO_DATE(match_date, '%b %d, %Y')) AS year, AVG(team_1_score) AS runRate
                FROM matches
                WHERE team_1 = %s OR team_2 = %s
                GROUP BY YEAR(STR_TO_DATE(match_date, '%b %d, %Y'))
            """

            # Execute the query with the country parameter
            cursor.execute(query, (country, country))

            # Fetch all rows from the result
            rows = cursor.fetchall()

            # Convert the rows to a list of dictionaries
            average_run_rates = [{'year': row[0], 'runs': row[1]} for row in rows]

            # Close the cursor and connection
            cursor.close()
            connection.close()

            # Return the average run rates as JSON response
            return jsonify(average_run_rates), 200
        else:
            return jsonify({"error": "Database connection failed"}), 500

    except Error as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500



@app.route('/api/unique-batsmen', methods=['GET'])
def get_unique_batsmen():
    country = request.args.get('country')
    if not country:
        return jsonify({"error": "Country parameter is required"}), 400

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT DISTINCT player FROM batting WHERE team = %s"
        cursor.execute(query, (country,))
        batsmen = [row['player'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify(batsmen), 200
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/unique-bolwers', methods=['GET'])
def get_unique_bowlers2():
    country = request.args.get('country')
    if not country:
        return jsonify({"error": "Country parameter is required"}), 400

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT DISTINCT player FROM bowling WHERE team = %s"
        cursor.execute(query, (country,))
        batsmen = [row['player'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify(batsmen), 200
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/bowling/countries', methods=['GET'])
def get_unique_bowlers5():


    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT DISTINCT first_ball FROM master"
        cursor.execute(query)
        batsmen = [row['first_ball'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify(batsmen), 200
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/batting/countries', methods=['GET'])
def get_opposite_countries2():


    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT DISTINCT first_bat FROM master"
        cursor.execute(query)
        batsmen = [row['first_bat'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify(batsmen), 200
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/unique-bolwers2', methods=['GET'])
def get_unique_bowlers3():
    country = request.args.get('country')
    if not country:
        return jsonify({"error": "Country parameter is required"}), 400

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT DISTINCT bowler FROM master  WHERE first_ball = %s"
        cursor.execute(query)
        batsmen = [row['bowler'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify(batsmen), 200
    else:
        return jsonify({"error": "Database connection failed"}), 500

# @app.route('/api/unique-bowlers', methods=['GET'])
# def get_unique_bowlers():
#     conn = get_db_connection()
#     if conn:
#         cursor = conn.cursor(dictionary=True)
#         query = "SELECT DISTINCT player FROM bowling"
#         cursor.execute(query)
#         bowlers = [row['player'] for row in cursor.fetchall()]
#         cursor.close()
#         conn.close()
#         return jsonify(bowlers), 200
#     else:
#         return jsonify({"error": "Database connection failed"}), 500


@app.route('/api/countries', methods=['GET'])
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


@app.route('/api/other-data', methods=['GET'])
def get_other_data():
    # Print incoming parameters
    # Assign parameters to variables
    selected_team = request.args.get('selectedTeam')
    opposite_team = request.args.get('oppositeTeam')
    players = request.args.get('players')

    # Now you can use these variables as needed in your code
    print("Selected Team:", selected_team)
    print("Opposite Team:", opposite_team)
    print("Players:", players)

    data = {
        "xlabel": "Date",
        "ylabel": "strike_rate",
        "title": "Player predicted performance interconnection with ",
        "legend": [
            "Angelo Mathews",
            "Predicted Performance",
            "Dasun Shanaka",
            "Predicted Performance",
            "Kusal Mendis",
            "Predicted Performance"
        ],
        "x_values": [
            "2008-01-01",
            "2010-01-01",
            "2012-01-01",
            "2014-01-01",
            "2016-01-01",
            "2018-01-01",
            "2020-01-01",
            "2022-01-01",
            "2024-01-01"
        ],
        "y_values": [
            -50.0, 0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0
        ],
        "player_details": {
            "Angelo Mathews": [{
                "player": "Angelo Mathews",
                "date": "2009-06-10",
                "runs": 3,
                "balls": 2,
                "strike_rate": 150.0,
                "fours": 0,
                "sixes": 0,
                "predicted_runs": 3.0
            },
                {
                    "player": "Angelo Mathews",
                    "date": "2009-06-12",
                    "runs": 9,
                    "balls": 8,
                    "strike_rate": 112.5,
                    "fours": 1,
                    "sixes": 0,
                    "predicted_runs": 9.0
                }],
            "Dasun Shanaka": [{
                "player": "Dasun Shanaka",
                "date": "2015-08-01",
                "runs": 7,
                "balls": 4,
                "strike_rate": 175.0,
                "fours": 1,
                "sixes": 0,
                "predicted_runs": 7.0
            },
                {
                    "player": "Dasun Shanaka",
                    "date": "2016-02-09",
                    "runs": 3,
                    "balls": 8,
                    "strike_rate": 37.5,
                    "fours": 0,
                    "sixes": 0,
                    "predicted_runs": 3.0
                }],
            "Kusal Mendis": [{
                "player": "Kusal Mendis",
                "date": "2016-07-05",
                "runs": 21,
                "balls": 16,
                "strike_rate": 131.25,
                "fours": 0,
                "sixes": 1,
                "predicted_runs": 21.0
            },
                {
                    "player": "Kusal Mendis",
                    "date": "2016-09-06",
                    "runs": 22,
                    "balls": 13,
                    "strike_rate": 169.23,
                    "fours": 2,
                    "sixes": 2,
                    "predicted_runs": 22.0
                }]
        }
    }

    return jsonify(data)

@app.route('/api/other-data2', methods=['GET'])
def get_other_data2():
    # Print incoming parameters
    # Assign parameters to variables
    selected_team = request.args.get('selectedTeam')
    opposite_team = request.args.get('oppositeTeam')
    players = request.args.get('players')

    # Now you can use these variables as needed in your code
    print("Selected Team:", selected_team)
    print("Opposite Team:", opposite_team)
    print("Players:", players)

    data = {
  "xlabel": "Batting Position",
  "ylabel": "Runs",
  "title": "Runs vs Batting Position",
  "legend": [
      "Charith Asalanka",
      "Kamindu Mendis",
      "Kusal Mendis",
      "Sadeera Samarawickrama"
  ],
  "x_values": [
      1,
      2,
      3,
      4,
      5,
      6,
      7,
      8,
      9,
      10,
      11
  ],
  "y_values": [
      0.0,
      10.0,
      20.0,
      30.0,
      40.0,
      50.0,
      60.0
  ],
  "player_details": {
      "Charith Asalanka": [
          {
              "player": "Charith Asalanka",
              "batting_position": 3,
              "runs": 40.5,
              "balls": 26.0,
              "fours": 2.5,
              "sixes": 2.5,
              "strike_rate": 98.29499999999999
          },
          {
              "player": "Charith Asalanka",
              "batting_position": 5,
              "runs": 25.0,
              "balls": 13.333333333333334,
              "fours": 0.3333333333333333,
              "sixes": 3.0,
              "strike_rate": 156.50666666666666
          }
      ],
      "Kamindu Mendis": [
          {
              "player": "Kamindu Mendis",
              "batting_position": 3,
              "runs": 22.666666666666668,
              "balls": 17.666666666666668,
              "fours": 2.0,
              "sixes": 1.3333333333333333,
              "strike_rate": 124.24666666666667
          }
      ],
      "Kusal Mendis": [
          {
              "player": "Kusal Mendis",
              "batting_position": 1,
              "runs": 53.0,
              "balls": 27.0,
              "fours": 8.0,
              "sixes": 2.0,
              "strike_rate": 196.29
          },
          {
              "player": "Kusal Mendis",
              "batting_position": 2,
              "runs": 54.142857142857146,
              "balls": 33.714285714285715,
              "fours": 4.0,
              "sixes": 3.2857142857142856,
              "strike_rate": 154.46571428571428
          }
      ],
      "Sadeera Samarawickrama": [
          {
              "player": "Sadeera Samarawickrama",
              "batting_position": 4,
              "runs": 34.0,
              "balls": 29.5,
              "fours": 4.0,
              "sixes": 0.5,
              "strike_rate": 95.355
          },
          {
              "player": "Sadeera Samarawickrama",
              "batting_position": 8,
              "runs": 7.0,
              "balls": 7.0,
              "fours": 1.0,
              "sixes": 0.0,
              "strike_rate": 100.0
          }
      ]
  }
}

    return jsonify(data)

@app.route('/api/bowling/other-data1', methods=['GET'])
def get_other_data3():
    # Print incoming parameters
    # Assign parameters to variables
    selected_team = request.args.get('selectedTeam')
    opposite_team = request.args.get('oppositeTeam')
    players = request.args.get('players')

    # Now you can use these variables as needed in your code
    print("Selected Team:", selected_team)
    print("Opposite Team:", opposite_team)
    print("Players:", players)

    data = {"xlabel": "Date", "ylabel": "bowling_average", "title": "Player Predicted Performance Interconnection with bowling_average", "legend": ["Angelo Mathews", "Angelo Mathews Predicted", "Tillakaratne Dilshan", "Tillakaratne Dilshan Predicted", "Wanindu Hasaranga", "Wanindu Hasaranga Predicted", "Maheesh Theekshana", "Maheesh Theekshana Predicted"], "x_values": ["2008-01-01", "2010-01-01", "2012-01-01", "2014-01-01", "2016-01-01", "2018-01-01", "2020-01-01", "2022-01-01", "2024-01-01"], "y_values": [-10.0, 0.0, 10.0, 20.0, 30.0, 40.0, 50.0], "player_details": {"Angelo Mathews": [{"player": "Angelo Mathews", "date": "2009-12-09", "economy_rate": 7.5, "bowling_average": 15.0, "strike_rate": 12.0, "wickets_per_over": 0.5, "dots_per_over": 1.0, "predicted_performance": 1.9999800493902424}, {"player": "Angelo Mathews", "date": "2009-12-12", "economy_rate": 15.473684210526317, "bowling_average": 0.0, "strike_rate": 0.0, "wickets_per_over": 0.0, "dots_per_over": 0.6315789473684211, "predicted_performance": 2.6215383249182477e-05}, {"player": "Angelo Mathews", "date": "2010-05-11", "economy_rate": 9.666666666666666, "bowling_average": 0.0, "strike_rate": 0.0, "wickets_per_over": 0.0, "dots_per_over": 2.0, "predicted_performance": 2.621538324746163e-05}, {"player": "Angelo Mathews", "date": "2012-08-07", "economy_rate": 7.666666666666667, "bowling_average": 0.0, "strike_rate": 0.0, "wickets_per_over": 0.0, "dots_per_over": 2.0, "predicted_performance": 2.6215383242798694e-05}, {"player": "Angelo Mathews", "date": "2014-04-06", "economy_rate": 6.25, "bowling_average": 25.0, "strike_rate": 24.0, "wickets_per_over": 0.25, "dots_per_over": 2.0, "predicted_performance": 1.0000011162010187}, {"player": "Angelo Mathews", "date": "2016-03-01", "economy_rate": 5.333333333333333, "bowling_average": 0.0, "strike_rate": 0.0, "wickets_per_over": 0.0, "dots_per_over": 3.6666666666666665, "predicted_performance": 2.6215383242437872e-05}, {"player": "Angelo Mathews", "date": "2017-09-06", "economy_rate": 11.0, "bowling_average": 0.0, "strike_rate": 0.0, "wickets_per_over": 0.0, "dots_per_over": 1.0, "predicted_performance": 2.6215383249182477e-05}, {"player": "Angelo Mathews", "date": "2017-12-20", "economy_rate": 6.333333333333333, "bowling_average": 19.0, "strike_rate": 18.0, "wickets_per_over": 0.3333333333333333, "dots_per_over": 2.3333333333333335, "predicted_performance": 1.0000011162010187}, {"player": "Angelo Mathews", "date": "2017-12-22", "economy_rate": 6.857142857142857, "bowling_average": 0.0, "strike_rate": 0.0, "wickets_per_over": 0.0, "dots_per_over": 3.0, "predicted_performance": 2.6215383242437872e-05}, {"player": "Angelo Mathews", "date": "2020-01-10", "economy_rate": 12.666666666666666, "bowling_average": 0.0, "strike_rate": 0.0, "wickets_per_over": 0.0, "dots_per_over": 1.3333333333333333, "predicted_performance": 2.6215383249182477e-05}], "Tillakaratne Dilshan": [{"player": "Tillakaratne Dilshan", "date": "2009-12-09", "economy_rate": 14.0, "bowling_average": 14.0, "strike_rate": 6.0, "wickets_per_over": 1.0, "dots_per_over": 1.0, "predicted_performance": 1.0000011162010187}, {"player": "Tillakaratne Dilshan", "date": "2009-12-12", "economy_rate": 10.0, "bowling_average": 0.0, "strike_rate": 0.0, "wickets_per_over": 0.0, "dots_per_over": 2.0, "predicted_performance": 2.6215383246628964e-05}, {"player": "Tillakaratne Dilshan", "date": "2010-05-11", "economy_rate": 7.0, "bowling_average": 0.0, "strike_rate": 0.0, "wickets_per_over": 0.0, "dots_per_over": 0.5, "predicted_performance": 2.6215383241966027e-05}, {"player": "Tillakaratne Dilshan", "date": "2016-02-14", "economy_rate": 4.0, "bowling_average": 0.0, "strike_rate": 0.0, "wickets_per_over": 0.0, "dots_per_over": 2.0, "predicted_performance": 2.6215383241966027e-05}], "Wanindu Hasaranga": [{"player": "Wanindu Hasaranga", "date": "2020-01-07", "economy_rate": 7.5, "bowling_average": 15.0, "strike_rate": 12.0, "wickets_per_over": 0.5, "dots_per_over": 1.5, "predicted_performance": 1.9999800493902415}, {"player": "Wanindu Hasaranga", "date": "2020-01-10", "economy_rate": 6.75, "bowling_average": 27.0, "strike_rate": 24.0, "wickets_per_over": 0.25, "dots_per_over": 1.75, "predicted_performance": 1.0000011162010187}, {"player": "Wanindu Hasaranga", "date": "2021-07-25", "economy_rate": 7.0, "bowling_average": 14.0, "strike_rate": 12.0, "wickets_per_over": 0.5, "dots_per_over": 2.0, "predicted_performance": 1.9999800493902415}, {"player": "Wanindu Hasaranga", "date": "2021-07-28", "economy_rate": 7.5, "bowling_average": 30.0, "strike_rate": 24.0, "wickets_per_over": 0.25, "dots_per_over": 2.0, "predicted_performance": 1.0000011162010187}, {"player": "Wanindu Hasaranga", "date": "2021-07-29", "economy_rate": 2.25, "bowling_average": 2.25, "strike_rate": 6.0, "wickets_per_over": 1.0, "dots_per_over": 3.75, "predicted_performance": 3.9998754532603695}, {"player": "Wanindu Hasaranga", "date": "2022-09-06", "economy_rate": 9.75, "bowling_average": 0.0, "strike_rate": 0.0, "wickets_per_over": 0.0, "dots_per_over": 1.0, "predicted_performance": 2.6215383249182477e-05}, {"player": "Wanindu Hasaranga", "date": "2023-01-03", "economy_rate": 5.5, "bowling_average": 22.0, "strike_rate": 24.0, "wickets_per_over": 0.25, "dots_per_over": 2.5, "predicted_performance": 1.0000011162010187}, {"player": "Wanindu Hasaranga", "date": "2023-01-05", "economy_rate": 13.666666666666666, "bowling_average": 41.0, "strike_rate": 18.0, "wickets_per_over": 0.3333333333333333, "dots_per_over": 1.6666666666666667, "predicted_performance": 1.0000011162010187}, {"player": "Wanindu Hasaranga", "date": "2023-01-07", "economy_rate": 9.0, "bowling_average": 36.0, "strike_rate": 24.0, "wickets_per_over": 0.25, "dots_per_over": 1.25, "predicted_performance": 1.0000011162010187}], "Maheesh Theekshana": [{"player": "Maheesh Theekshana", "date": "2022-09-06", "economy_rate": 7.25, "bowling_average": 29.0, "strike_rate": 24.0, "wickets_per_over": 0.25, "dots_per_over": 1.5, "predicted_performance": 1.0000011162010187}, {"player": "Maheesh Theekshana", "date": "2023-01-03", "economy_rate": 7.25, "bowling_average": 29.0, "strike_rate": 24.0, "wickets_per_over": 0.25, "dots_per_over": 1.5, "predicted_performance": 1.0000011162010187}, {"player": "Maheesh Theekshana", "date": "2023-01-05", "economy_rate": 8.25, "bowling_average": 0.0, "strike_rate": 0.0, "wickets_per_over": 0.0, "dots_per_over": 1.75, "predicted_performance": 2.621538324451954e-05}, {"player": "Maheesh Theekshana", "date": "2023-01-07", "economy_rate": 12.0, "bowling_average": 0.0, "strike_rate": 0.0, "wickets_per_over": 0.0, "dots_per_over": 1.0, "predicted_performance": 2.6215383249182477e-05}]}}


    return jsonify(data)

@app.route('/api/bowling/other-data2', methods=['GET'])
def get_other_data4():
    # Print incoming parameters
    # Assign parameters to variables
    selected_team = request.args.get('selectedTeam')
    opposite_team = request.args.get('oppositeTeam')
    players = request.args.get('players')

    # Now you can use these variables as needed in your code
    print("Selected Team:", selected_team)
    print("Opposite Team:", opposite_team)
    print("Players:", players)

    data = {
    "xlabel": "Over",
    "ylabel": "avg_runs",
    "title": "avg_runs vs Bowling over.",
    "legend": [
        "PVD Chameera",
        "SL Malinga",
        "MD Shanaka"
    ],
    "x_values": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20
    ],
    "y_values": [
        0.0,
        2.0,
        4.0,
        6.0,
        8.0,
        10.0,
        12.0,
        14.0,
        16.0,
        18.0
    ],
    "player_details": {
        "PVD Chameera": [
            {
                "bowler": "PVD Chameera",
                "over": 2,
                "avg_extras": 0.3,
                "avg_wickets": 0.3,
                "avg_runs": 6.0
            },
            {
                "bowler": "PVD Chameera",
                "over": 3,
                "avg_extras": 0.6,
                "avg_wickets": 0.2,
                "avg_runs": 8.6
            },
            {
                "bowler": "PVD Chameera",
                "over": 4,
                "avg_extras": 0.3333333333333333,
                "avg_wickets": 0.0,
                "avg_runs": 6.0
            },
            {
                "bowler": "PVD Chameera",
                "over": 5,
                "avg_extras": 0.0,
                "avg_wickets": 0.25,
                "avg_runs": 6.0
            },
            {
                "bowler": "PVD Chameera",
                "over": 6,
                "avg_extras": 0.2,
                "avg_wickets": 0.2,
                "avg_runs": 7.8
            },
            {
                "bowler": "PVD Chameera",
                "over": 7,
                "avg_extras": 1.3333333333333333,
                "avg_wickets": 0.16666666666666666,
                "avg_runs": 10.5
            },
            {
                "bowler": "PVD Chameera",
                "over": 8,
                "avg_extras": 0.25,
                "avg_wickets": 0.25,
                "avg_runs": 4.25
            },
            {
                "bowler": "PVD Chameera",
                "over": 9,
                "avg_extras": 1.0,
                "avg_wickets": 0.0,
                "avg_runs": 2.5
            },
            {
                "bowler": "PVD Chameera",
                "over": 10,
                "avg_extras": 0.0,
                "avg_wickets": 0.0,
                "avg_runs": 16.0
            },
            {
                "bowler": "PVD Chameera",
                "over": 11,
                "avg_extras": 0.25,
                "avg_wickets": 0.5,
                "avg_runs": 7.25
            },
            {
                "bowler": "PVD Chameera",
                "over": 13,
                "avg_extras": 0.0,
                "avg_wickets": 0.5,
                "avg_runs": 6.5
            },
            {
                "bowler": "PVD Chameera",
                "over": 14,
                "avg_extras": 0.5,
                "avg_wickets": 0.5,
                "avg_runs": 11.5
            },
            {
                "bowler": "PVD Chameera",
                "over": 15,
                "avg_extras": 0.6666666666666666,
                "avg_wickets": 0.3333333333333333,
                "avg_runs": 5.666666666666667
            },
            {
                "bowler": "PVD Chameera",
                "over": 16,
                "avg_extras": 0.5,
                "avg_wickets": 0.0,
                "avg_runs": 7.0
            },
            {
                "bowler": "PVD Chameera",
                "over": 17,
                "avg_extras": 1.0,
                "avg_wickets": 0.5,
                "avg_runs": 11.0
            },
            {
                "bowler": "PVD Chameera",
                "over": 18,
                "avg_extras": 0.6,
                "avg_wickets": 0.2,
                "avg_runs": 11.6
            },
            {
                "bowler": "PVD Chameera",
                "over": 19,
                "avg_extras": 0.5555555555555556,
                "avg_wickets": 0.1111111111111111,
                "avg_runs": 9.333333333333334
            },
            {
                "bowler": "PVD Chameera",
                "over": 20,
                "avg_extras": 0.625,
                "avg_wickets": 1.375,
                "avg_runs": 6.375
            },
            {
                "bowler": "PVD Chameera",
                "over": 21,
                "avg_extras": 0.6923076923076923,
                "avg_wickets": 0.46153846153846156,
                "avg_runs": 10.846153846153847
            }
        ],
        "SL Malinga": [
            {
                "bowler": "SL Malinga",
                "over": 2,
                "avg_extras": 1.0,
                "avg_wickets": 0.1875,
                "avg_runs": 6.3125
            },
            {
                "bowler": "SL Malinga",
                "over": 3,
                "avg_extras": 1.2,
                "avg_wickets": 0.0,
                "avg_runs": 7.2
            },
            {
                "bowler": "SL Malinga",
                "over": 4,
                "avg_extras": 0.16666666666666666,
                "avg_wickets": 0.16666666666666666,
                "avg_runs": 5.333333333333333
            },
            {
                "bowler": "SL Malinga",
                "over": 5,
                "avg_extras": 0.6,
                "avg_wickets": 0.2,
                "avg_runs": 9.2
            },
            {
                "bowler": "SL Malinga",
                "over": 6,
                "avg_extras": 0.4166666666666667,
                "avg_wickets": 0.08333333333333333,
                "avg_runs": 7.333333333333333
            },
            {
                "bowler": "SL Malinga",
                "over": 7,
                "avg_extras": 0.36363636363636365,
                "avg_wickets": 0.09090909090909091,
                "avg_runs": 6.818181818181818
            },
            {
                "bowler": "SL Malinga",
                "over": 9,
                "avg_extras": 0.5,
                "avg_wickets": 0.0,
                "avg_runs": 10.0
            },
            {
                "bowler": "SL Malinga",
                "over": 10,
                "avg_extras": 0.0,
                "avg_wickets": 0.5,
                "avg_runs": 6.5
            },
            {
                "bowler": "SL Malinga",
                "over": 11,
                "avg_extras": 0.0,
                "avg_wickets": 2.0,
                "avg_runs": 4.0
            },
            {
                "bowler": "SL Malinga",
                "over": 12,
                "avg_extras": 0.6666666666666666,
                "avg_wickets": 0.6666666666666666,
                "avg_runs": 5.666666666666667
            },
            {
                "bowler": "SL Malinga",
                "over": 13,
                "avg_extras": 0.0,
                "avg_wickets": 0.6666666666666666,
                "avg_runs": 5.0
            },
            {
                "bowler": "SL Malinga",
                "over": 14,
                "avg_extras": 0.0,
                "avg_wickets": 0.25,
                "avg_runs": 10.25
            },
            {
                "bowler": "SL Malinga",
                "over": 15,
                "avg_extras": 1.2,
                "avg_wickets": 0.2,
                "avg_runs": 8.2
            },
            {
                "bowler": "SL Malinga",
                "over": 16,
                "avg_extras": 2.0,
                "avg_wickets": 0.5,
                "avg_runs": 10.5
            },
            {
                "bowler": "SL Malinga",
                "over": 17,
                "avg_extras": 0.14285714285714285,
                "avg_wickets": 0.14285714285714285,
                "avg_runs": 6.857142857142857
            },
            {
                "bowler": "SL Malinga",
                "over": 18,
                "avg_extras": 0.17647058823529413,
                "avg_wickets": 0.17647058823529413,
                "avg_runs": 10.470588235294118
            },
            {
                "bowler": "SL Malinga",
                "over": 19,
                "avg_extras": 0.08333333333333333,
                "avg_wickets": 0.25,
                "avg_runs": 9.416666666666666
            },
            {
                "bowler": "SL Malinga",
                "over": 20,
                "avg_extras": 0.45,
                "avg_wickets": 0.9,
                "avg_runs": 7.1
            },
            {
                "bowler": "SL Malinga",
                "over": 21,
                "avg_extras": 1.1538461538461537,
                "avg_wickets": 1.0,
                "avg_runs": 8.153846153846153
            }
        ],
        "MD Shanaka": [
            {
                "bowler": "MD Shanaka",
                "over": 8,
                "avg_extras": 0.0,
                "avg_wickets": 0.5,
                "avg_runs": 7.0
            },
            {
                "bowler": "MD Shanaka",
                "over": 9,
                "avg_extras": 0.0,
                "avg_wickets": 0.0,
                "avg_runs": 4.0
            },
            {
                "bowler": "MD Shanaka",
                "over": 10,
                "avg_extras": 0.0,
                "avg_wickets": 1.0,
                "avg_runs": 4.333333333333333
            },
            {
                "bowler": "MD Shanaka",
                "over": 11,
                "avg_extras": 0.0,
                "avg_wickets": 0.0,
                "avg_runs": 8.5
            },
            {
                "bowler": "MD Shanaka",
                "over": 12,
                "avg_extras": 0.5,
                "avg_wickets": 0.25,
                "avg_runs": 4.75
            },
            {
                "bowler": "MD Shanaka",
                "over": 13,
                "avg_extras": 0.25,
                "avg_wickets": 0.0,
                "avg_runs": 7.75
            },
            {
                "bowler": "MD Shanaka",
                "over": 14,
                "avg_extras": 0.5,
                "avg_wickets": 0.0,
                "avg_runs": 10.75
            },
            {
                "bowler": "MD Shanaka",
                "over": 15,
                "avg_extras": 0.0,
                "avg_wickets": 1.0,
                "avg_runs": 4.0
            },
            {
                "bowler": "MD Shanaka",
                "over": 16,
                "avg_extras": 0.0,
                "avg_wickets": 1.0,
                "avg_runs": 9.0
            },
            {
                "bowler": "MD Shanaka",
                "over": 17,
                "avg_extras": 0.5,
                "avg_wickets": 0.25,
                "avg_runs": 8.75
            },
            {
                "bowler": "MD Shanaka",
                "over": 18,
                "avg_extras": 1.0,
                "avg_wickets": 1.0,
                "avg_runs": 8.0
            },
            {
                "bowler": "MD Shanaka",
                "over": 19,
                "avg_extras": 1.0,
                "avg_wickets": 0.2,
                "avg_runs": 14.6
            },
            {
                "bowler": "MD Shanaka",
                "over": 20,
                "avg_extras": 0.5,
                "avg_wickets": 0.5,
                "avg_runs": 7.5
            },
            {
                "bowler": "MD Shanaka",
                "over": 21,
                "avg_extras": 1.0,
                "avg_wickets": 1.0,
                "avg_runs": 7.5
            }
        ]
    }
}
    return jsonify(data)

if __name__ == '__main__':
    port = os.getenv("PORT", 5000)  # Default to 5000 if no port specified in .env
    app.run(debug=True, port=int(port))
