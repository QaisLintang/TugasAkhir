import mysql.connector

# Replace these values with your actual database credentials
db_config = {
    'host': '180.250.135.11',
    'user': 'vm-b',
    'password': 'admin@123',
    'database': 'moodle',
}

# Connect to the MySQL database
print("connecting...")
conn = mysql.connector.connect(**db_config)

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Example query
cursor.execute("select mdl_user.id, mdl_user.username,mdl_sessions.userid, mdl_sessions.sid,mdl_sessions.firstip, mdl_sessions.lastip, FROM_UNIXTIME(mdl_sessions.timecreated) , FROM_UNIXTIME(mdl_sessions.timemodified) from mdl_user inner join mdl_sessions on mdl_user.id=mdl_sessions.userid;")
rows = cursor.fetchall()

for row in rows:
    print(row)

# Close the cursor and connection
cursor.close()
conn.close()
