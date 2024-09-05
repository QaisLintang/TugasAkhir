import mysql.connector
import pandas as pd
from datetime import datetime, timedelta
import os

# Configuration: Update these details with your MySQL server info
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'moodle'
}

# CSV file to insert
path = os.path.dirname(os.path.abspath(__file__))

# Table name where data will be inserted
table_name = 'backup_attempt'

columns =  ['attempt_id', 'id_peserta', 'firstname', 'lastname', 'course_name', 'quiz_name', 'unique_id', 'layout', 'timestart', 'timefinish', 'score']

# Connect to the database
try:
    # conn = mysql.connector.connect(**db_config)
    # cursor = conn.cursor()

    # Get the current time and the time 1 minute ahead (excluding seconds)
    # current_time = datetime.now().strftime('%Y-%m-%d_%H-%M')
    # prev_time = (datetime.now() - timedelta(minutes=1)).strftime('%Y-%m-%d_%H-%M')

    current_time = '2024-09-04_22-55'
    prev_time = '2024-09-04_22-54'

    # Function to find matching file based on the time pattern
    def find_matching_file(directory, time_pattern):
        found_file = []
        returned = None
        for filename in os.listdir(directory):
            if time_pattern in filename:
                found_file.append(filename)
        for file in found_file:
            if "_log_attempt.csv" in file:
                returned = file
        return returned
    
    def search_directory_containing_string(path, search_str):
        matching_dirs = []
        for root, dirs, files in os.walk(path):
            for dir_name in dirs:
                if search_str in dir_name:
                    matching_dirs.append(os.path.join(root, dir_name))
        if len(matching_dirs) > 0:
            return matching_dirs[len(matching_dirs) - 1]
        else:
            return None

    result = search_directory_containing_string(path, current_time)

    if not result:
        result = search_directory_containing_string(path, prev_time)

    # Check for the current time
    matching_file = find_matching_file(result, current_time)

    # If no matching file is found, check for the next minute
    if not matching_file:
        matching_file = find_matching_file(result, prev_time)

    if matching_file:
        df = pd.read_csv(os.path.join(result, matching_file))
    else:
        print("No matching file found.")

    # # Read the CSV file
    # data = pd.read_csv(csv_file, header=None)
    # data.columns = columns

    # # Generate the SQL INSERT statement dynamically
    # columns = ', '.join(data.columns)
    # placeholders = ', '.join(['%s'] * len(data.columns))
    # insert_stmt = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    # print(columns)
    # print(placeholders)
    # print(insert_stmt)

    # # Insert each row from the DataFrame into the SQL table
    # for row in data.itertuples(index=False, name=None):
    #     cursor.execute(insert_stmt, row)

    # # Commit the transaction
    # conn.commit()
    # print("Data inserted successfully.")

except mysql.connector.Error as err:
    print(f"Error: {err}")
    # conn.rollback()

finally:
    # cursor.close()
    # conn.close()
    print("end")