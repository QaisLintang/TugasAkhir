import mysql.connector

# Replace these values with your actual database credentials
db_config = {
    'host': '180.250.135.11',
    'user': 'root',
    'password': 'admin@123',
    'database': 'moodle',
}

# Connect to the MySQL database
print("connecting...")
conn = mysql.connector.connect(**db_config)

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Example query
cursor.execute("SELECT * FROM mdl_sessions")
rows = cursor.fetchall()

for row in rows:
    print(row)

# Close the cursor and connection
cursor.close()
conn.close()
