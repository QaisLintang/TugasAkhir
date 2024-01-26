# app.py (Flask program)

from flask import Flask, render_template
import csv
import time

class peserta:
    def __init__(self, user_full_name, IP_address, status, session):
        self.user_full_name = user_full_name
        self.IP_address = IP_address
        self.status = status
        self.session = session

data = {}

app = Flask(__name__)

# Read CSV file and create a dictionary with usernames as keys and corresponding IP addresses as values
def read_csv(file_path):
    global data
    with open(file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if "Quiz:" in row["Event context"]:
                if "-" != row['User full name']:
                    nama_peserta = row['User full name']
                    status = check_cheating(data, row['User full name'], row['IP address'])
                    data[nama_peserta] = peserta(row['User full name'], row["IP address"], status)
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
    # Assuming your CSV file is named 'data.csv' and is in the same directory as this script
    i = 0
    while True:
        if (i % 30) == 0:
            csv_file_path = 'dummy_data.csv'
            user_data = read_csv(csv_file_path)
            return render_template('usernames.html', user_data=user_data)
        elif (i % 60) == 0:
            csv_file_path = 'dummy_IP_Change_data.csv'
            user_data = read_csv(csv_file_path)
            return render_template('usernames.html', user_data=user_data)
        else:
            i += 1
            # time.sleep(1)

if __name__ == '__main__':
    app.run(debug=True)
