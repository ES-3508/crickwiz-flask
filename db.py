import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

def import_sql_dump(filename, host, user, password, database):
    # Connect to the MySQL database
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        print("Successfully connected to the database")

        cursor = connection.cursor()

        # Open and read the SQL dump file
        with open(filename, 'r', encoding='utf-8') as file:
            sql_dump = file.read()

        # Split the dump by semicolon to get individual commands (simple split by ';' may need to be adjusted for more complex dumps)
        sql_commands = sql_dump.split(';')

        # Execute each SQL command
        for command in sql_commands:
            try:
                if command.strip():
                    cursor.execute(command)
            except Error as e:
                print(f"Error occurred: {e}")

        connection.commit()
        print("SQL dump has been imported successfully")

    except Error as error:
        print(f"Error while connecting to MySQL: {error}")

    finally:
        # Closing database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


# Usage
# import_sql_dump('db/cricket_info_batting.sql', 'localhost', 'root', 'Achini@143', 'crickwiz')
import_sql_dump('db/cricket_info_bowling.sql', 'os.getenv("DATABASE_HOST")', os.getenv("DATABASE_USER"), os.getenv("DATABASE_PASSWORD"), os.getenv("DATABASE_NAME"))
import_sql_dump('db/cricket_info_bowling_wickets.sql', 'os.getenv("DATABASE_HOST")', os.getenv("DATABASE_USER"), os.getenv("DATABASE_PASSWORD"), os.getenv("DATABASE_NAME"))
import_sql_dump('db/cricket_info_matches.sql', 'localhost', 'os.getenv("DATABASE_HOST")', os.getenv("DATABASE_USER"), os.getenv("DATABASE_PASSWORD"), os.getenv("DATABASE_NAME"))
