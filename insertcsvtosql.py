import mysql.connector
import pandas as pd

# Configuration: Update these details with your MySQL server info
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'moodle'
}

# CSV file to insert
csv_file = 'downloaded_files\dump-sql-1.csv'

# Table name where data will be inserted
table_name = 'backup_attempt'

columns =  ['attempt_id', 'id_peserta', 'firstname', 'lastname', 'course_name', 'quiz_name', 'unique_id', 'layout', 'timestart', 'timefinish', 'score']

# Connect to the database
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Read the CSV file
    data = pd.read_csv(csv_file, header=None)
    data.columns = columns

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
