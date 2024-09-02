import mysql.connector
from datetime import datetime, timedelta

# Replace these values with your actual database credentials
db_config = {
    'host': '180.250.135.11',
    'user': 'logging',
    'password': 'password1sampai8',
    'database': 'log_analyzer_db',
}

# Connect to the MySQL database
conn = mysql.connector.connect(**db_config)

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Get the current date and time
current_time = datetime.now()

# Define the test times (7 AM, 11 AM, 2 PM) as UNIX timestamps
test_times = [
    datetime.combine(current_time.date(), datetime.min.time()) + timedelta(hours=7),
    datetime.combine(current_time.date(), datetime.min.time()) + timedelta(hours=11),
    datetime.combine(current_time.date(), datetime.min.time()) + timedelta(hours=14)
]

# Convert test times to UNIX format
test_times_unix = [int(time.timestamp()) for time in test_times]

# Determine which test data to retrieve based on the current time
if current_time < test_times[1]:
    selected_test_time = test_times_unix[0]
elif current_time < test_times[2]:
    selected_test_time = test_times_unix[1]
else:
    selected_test_time = test_times_unix[2]

query = """ 
    SELECT id_peserta, firstname, lastname, quiz_name, unique_id, timestart, timefinish, score 
    FROM backup_attempt
    WHERE timestart >= %s AND timestart < %s;
    """
selected_test_time = 1724842800

next_test_time = selected_test_time + 4 * 60 * 60  # Add 4 hours to cover the entire time range

print(selected_test_time)
print(next_test_time)

cursor.execute(query, (selected_test_time, next_test_time))

rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]

# # Example query
# cursor.execute("""SELECT id_peserta, firstname, lastname, quiz_name, unique_id, timestart, timefinish, score 
#             FROM backup_attempt
#             ;""")
# rows = cursor.fetchall()

for row in rows:
    print(row)

# Close the cursor and connection
cursor.close()
conn.close()
