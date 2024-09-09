import mysql.connector
import pandas as pd
import os
from datetime import datetime, timedelta

# Configuration: Update these details with your MySQL server info
db_config = {
    'user': 'logging',
    'password': 'password1sampai8',
    'host': '180.250.135.11',
    'database': 'log_analyzer_db'
}

# CSV file to insert
#hari = os.system('$(date +%Y-%m-%d)')
path = '/home/linux/backup-sql'

# Table name where data will be inserted
table_name = 'backup_attempt'

columns =  ['attempt_id', 'id_peserta', 'firstname', 'lastname', 'course_name', 'quiz_name', 'unique_id', 'layout', 'timestart', 'timefinish', 'score']

# Connect to the database
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Get the current time and the time 1 minute ahead (excluding seconds)
    current_time = datetime.now().strftime('%Y-%m-%d-%H:%M')
    prev_time = (datetime.now() - timedelta(minutes=1)).strftime('%Y-%m-%d-%H:%M')

    current_time_csv = datetime.now().strftime('%Y-%m-%d_%H:%M')
    prev_time_csv = (datetime.now() - timedelta(minutes=1)).strftime('%Y-%m-%d-%H:%M')

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
                    print("found")
                    matching_dirs.append(os.path.join(root, dir_name))
        if len(matching_dirs) > 0:
            return matching_dirs[len(matching_dirs) - 1]
        else:
            return None

    result = search_directory_containing_string(path, current_time)

    if not result:
        result = search_directory_containing_string(path, prev_time)

    print(result)

    # If no matching file is found, check for the next minute
    if not matching_file:
        matching_file = find_matching_file(result, prev_time_csv)

    if matching_file:
        print(f"Found file: {matching_file}")
        # Load the CSV file into a DataFrame
        data = pd.read_csv(os.path.join(result, matching_file), header=None)
        data.columns = columns
    else:
        print("data not found???")
        data = None
        print("No matching file found.")

    # Generate the SQL INSERT statement dynamically
    columns = ', '.join(data.columns)
    placeholders = ', '.join(['%s'] * len(data.columns))
    insert_stmt = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    print(columns)
    print(placeholders)
    print(insert_stmt)

    # Insert each row from the DataFrame into the SQL table
    for row in data.itertuples(index=False, name=None):
        cursor.execute(insert_stmt, row)

    # Commit the transaction
    conn.commit()
    print("Data inserted successfully.")

except mysql.connector.Error as err:
    print(f"Error: {err}")
    conn.rollback()

finally:
    cursor.close()
    conn.close()