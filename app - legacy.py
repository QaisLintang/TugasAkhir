# app.py (Flask program)

from flask import Flask, render_template
import time
import mysql.connector

db_config = {
    'host': '180.250.135.11',
    'user': 'vm-b',
    'password': 'admin@123',
    'database': 'moodle',
}

class peserta:
    def __init__(self, username, userId, sid, first_IP, last_IP, status, timecreated, timemodified):
        self.username = username
        self.userId = userId
        self.first_IP = first_IP
        self.last_IP = last_IP
        self.sid = sid
        self.timecreated = timecreated
        self.timemodified = timemodified
        self.status = status

data = {}

app = Flask(__name__)

# # Read CSV file and create a dictionary with usernames as keys and corresponding IP addresses as values
# def read_csv(file_path):
#     global data
#     with open(file_path, 'r') as csv_file:
#         reader = csv.DictReader(csv_file)
#         for row in reader:
#             if "Quiz:" in row["Event context"]:
#                 if "-" != row['User full name']:
#                     nama_peserta = row['User full name']
#                     status = check_cheating(data, row['User full name'], row['IP address'])
#                     data[nama_peserta] = peserta(row['User full name'], row["IP address"], status)
#     return data

def load_data():
    global data

    conn = mysql.connector.connect(**db_config)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Example query
    cursor.execute(
        """ 
        select mdl_user.id, mdl_user.username,mdl_sessions.userid, mdl_sessions.sid,mdl_sessions.firstip, mdl_sessions.lastip, FROM_UNIXTIME(mdl_sessions.timecreated) AS timecreated, FROM_UNIXTIME(mdl_sessions.timemodified) AS timemodified  
        from mdl_user
        inner join mdl_sessions on mdl_user.id=mdl_sessions.userid;
        """)
    rows = cursor.fetchall()

    for row in rows:
        if data:
            if row[2] in data:
                if data[row[2]].sid != row[3]:
                    data[row[2]].sid = row[3]
                if data[row[2]].first_IP != row[4]:
                    data[row[2]].first_IP = row[4]
                if data[row[2]].last_IP != row[5]:
                    data[row[2]].last_IP = row[5]
                if data[row[2]].timecreated != row[6]:
                    data[row[2]].timecreated = row[6]
                if data[row[2]].timemodified != row[7]:
                    data[row[2]].timemodified = row[7]
            else:
                data[row[2]] = peserta(row[1], row[2], row[3], row[4], row[5], "good", row[6], row[7])
        else:
            data[row[2]] = peserta(row[1], row[2], row[3], row[4], row[5], "good", row[6], row[7])
    
    return data
                    

def check_cheating(data, current_name, current_IP):
    if len(data) == 0:
        return "good"
    elif current_name not in data:
        return "good"
    else:
        for name in data:
            obj = data[name]
            if obj.user_full_name == name:
                if obj.IP_address != current_IP:
                    obj.status = (f"WARNING, IP changed from {obj.IP_address} to {current_IP}")
                    obj.IP_address = current_IP
                else:
                    obj.status = "good"


# Route to display usernames and IP addresses
@app.route('/')
def show_usernames():
    user_data = load_data()

    return render_template('usernames.html', user_data=user_data)


if __name__ == '__main__':
    app.run(debug=True)
