# app.py (Flask program)

from flask import Flask, render_template, jsonify
from datetime import datetime
import pandas as pd
import urllib.parse
import pytz
import glob
from sklearn.ensemble import IsolationForest
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import threading
import time
from queue import Queue
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

model = 'models\iso_forest.joblib'
daftar_peserta = []
output_queue = Queue()

data_summary = [
    {
        'total_case'   : 0,
        'total_label_0': 0,
        'total_label_1': 0,
        'total_user'   : 0,
        'total_case_monthly': [
            {
                'januari'  : 0,
                'februari' : 0,
                'maret'    : 0,
                'april'    : 0,
                'mei'      : 0,
                'juni'     : 0,
                'juli'     : 0,
                'agustus'  : 0,
                'september': 0,
                'oktober'  : 0,
                'november' : 0,
                'desember' : 0
            }
        ]    
    }
]

# objek peserta
class peserta:
  def __init__(self, firstname, lastname, userid,timedateUser, timestart, timefinish, score, session):
    self.firstname = firstname
    self.lastname = lastname
    self.userid = userid
    self.timedateUser = datetime.fromtimestamp(timestart, pytz.timezone('Asia/Jakarta'))
    self.timestart = datetime.fromtimestamp(timestart, pytz.timezone('Asia/Jakarta')).strftime('%H:%M:%S')
    self.timefinish = datetime.fromtimestamp(timefinish, pytz.timezone('Asia/Jakarta')).strftime('%H:%M:%S')
    self.timetaken = datetime.fromtimestamp(timefinish - timestart, pytz.timezone('UTC')).strftime('%H:%M:%S')
    self.score = score
    self.status = 1
    self.session = session
    self.track_progress = "secure"

def get_time_shift():
    # Define Indonesian month names
    month_names_id = [
        "Januari", "Februari", "Maret", "April",
        "Mei", "Juni", "Juli", "Agustus",
        "September", "Oktober", "November", "Desember"
    ]
    timezone = pytz.timezone('Asia/Jakarta')

    # Get current time
    current_time = datetime.now()

    # Format current time with Indonesian month name
    formatted_date = current_time.strftime(f"%d {month_names_id[current_time.month - 1]} %Y")
    formatted_time = current_time.astimezone(timezone)

    # Determine phase based on current hour
    if 8 <= formatted_time.hour <= 10:
        shift = "Shift 1"
    elif 11 <= formatted_time.hour <= 13:
        shift = "Shift 2"
    elif 14 <= formatted_time.hour <= 16:
        shift = "Shift 3"
    else:
        shift = "Shift 4"
    
    return formatted_date, shift

def get_data(formatted_date, shift):
    download_dir = 'downloaded_files'
    username = 'serverlog'
    password = 'S3rverl0g!'

    # Create the download directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)

    # time = formatted_date
    # current_shift = shift
    time = '01 April 2024'
    current_shift = 'Shift 1'

    # Assuming 'time' and 'current_shift' are already defined
    encoded_time = urllib.parse.quote(time)
    encoded_shift = urllib.parse.quote(current_shift)

    url = f"https://sandbox.telkomuniversity.ac.id/laclog/lac-eprt-log/Quiz%20Attempts/{encoded_time}/{encoded_shift}/"
    command = f'!wget --user=serverlog --password=S3rverl0g! -r -np -nH --cut-dirs=3 -R "index.html*" {url}'

    delete_files_in_directory(download_dir)
    download_folder_with_auth(url, download_dir, username, password)

def create_dataframe():
    data_dir = 'downloaded_files'
    list_file = glob.glob(data_dir)

    if len(list_file) == 1:
        data = 'downloaded_files/Listening.xlsx'
        session = 'listening'
    elif len(list_file) == 2:
        data = 'downloaded_files/Grammar.xlsx'
        session = 'grammar'
    elif len(list_file) == 3:
        data = 'downloaded_files/Reading.xlsx'
        session = 'reading'

    df_data = pd.read_excel(data, header=0)

    return session, df_data

def getPeserta(df_data, session):
    for index, row in df_data.iterrows():
        # Check if the userid is already in daftar_peserta
        if not any(p.userid == row['id'] for p in daftar_peserta):
            newPeserta = peserta(row['firstname'], row['lastname'], row['id'], row['timestart'], row['timestart'], row['timefinish'], row['score'], session)
            daftar_peserta.append(newPeserta)

    # Convert 'timestart' and 'timefinish' to datetime if needed
    df_data['timestart'] = pd.to_datetime(df_data['timestart'])
    df_data['timefinish'] = pd.to_datetime(df_data['timefinish'])

    # Calculate time difference and convert to minutes
    df_data['diff_time'] = df_data['timefinish'] - df_data['timestart']
    df_data['diff_time_minute'] = df_data['diff_time'].dt.total_seconds() / 60


def add_value(row):
    if row['quiz_name'] == "Grammar":
        grammar_diff_time_minute = row['diff_time_minute']
        return grammar_diff_time_minute / 25
    elif row['quiz_name'] == "Reading":
        reading_diff_time_minute = row['diff_time_minute']
        return reading_diff_time_minute / 55
    elif row['quiz_name'] == "Listening":
        listening_diff_time_minute = row['diff_time_minute']
        return listening_diff_time_minute / 35
    
def predict(df_data, session):
  if session == 'listening':
    df_data['listening_diff_time_minute'] = 0.0
    df_data['listening_completion_ratio'] = 0.0
    df_data['listening_score'] = 0

    for index, row in df_data.iterrows():
        df_data.loc[index, 'listening_diff_time_minute'] = row['diff_time_minute']
        df_data.loc[index, 'listening_completion_ratio'] = add_value(row)
        df_data.loc[index, 'listening_score'] = row['score']

    # Selecting relevant features
    features = df_data[['listening_diff_time_minute', 'listening_completion_ratio', 'listening_score']]

    # Fitting the Isolation Forest
    iso_forest_listening = IsolationForest(contamination=0.1)
    df_data['anomaly_score_iso'] = iso_forest_listening.fit_predict(features)

  elif session == 'reading':
    df_data['reading_diff_time_minute'] = 0.0
    df_data['reading_completion_ratio'] = 0.0
    df_data['reading_score'] = 0

    for index, row in df_data.iterrows():
        df_data.loc[index, 'reading_diff_time_minute'] = row['diff_time_minute']
        df_data.loc[index, 'reading_completion_ratio'] = add_value(row)
        df_data.loc[index, 'reading_score'] = row['score']

    # Selecting relevant features
    features = df_data[['reading_diff_time_minute', 'reading_completion_ratio', 'reading_score']]

    # Fitting the Isolation Forest
    iso_forest_reading = IsolationForest(contamination=0.1)
    df_data['anomaly_score_iso'] = iso_forest_reading.fit_predict(features)

  elif session == 'grammar':
    df_data['grammar_diff_time_minute'] = 0.0
    df_data['grammar_completion_ratio'] = 0.0
    df_data['grammar_score'] = 0

    for index, row in df_data.iterrows():
        df_data.loc[index, 'grammar_diff_time_minute'] = row['diff_time_minute']
        df_data.loc[index, 'grammar_completion_ratio'] = add_value(row)
        df_data.loc[index, 'grammar_score'] = row['score']

    # Selecting relevant features
    features = df_data[['grammar_diff_time_minute', 'grammar_completion_ratio', 'grammar_score']]

    # Fitting the Isolation Forest
    iso_forest_grammar = IsolationForest(contamination=0.1)
    df_data['anomaly_score_iso'] = iso_forest_grammar.fit_predict(features)

def add_pred_value(df_data, session):
   for index, row in df_data.iterrows():
    for p in daftar_peserta:
        if p.userid == row['id']:
            p.status = row['anomaly_score_iso']
            if p.status == -1:
                if session == 'listening' or session == 'reading':
                    nilai_max = 50
                elif session == 'grammar':
                    nilai_max = 40
                converted_nilai = (p.score / nilai_max) * 100
                if converted_nilai < 40:
                    p.status = 1


def getCaseCounts(daftar_peserta):
    cases, cheat, good = 0, 0, 0

    for p in daftar_peserta:
        if p.status == "terindikasi":
            cases += 1
            cheat += 1
        else:
            good += 1

    return cases, cheat, good

def getMonthlyCases(daftar_peserta):
    month_names_id = [
        "Januari", "Februari", "Maret", "April",
        "Mei", "Juni", "Juli", "Agustus",
        "September", "Oktober", "November", "Desember"
    ]

    for p in daftar_peserta:
        if p.status == "terindikasi":
            data_summary[0]['total_case_monthly'][0][month_names_id[p.timedateUser.month - 1].lower()] += 1

    # for p in daftar_peserta:
    #     if p.status == -1:
    #         if p.timedateUser.month == 1:
    #             data_summary[0]['total_case_monthly'][0]['januari'] += 1
    #         elif p.timedateUser.month == 2:
    #             data_summary[0]['total_case_monthly'][0]['februari'] += 1
    #         elif p.timedateUser.month == 3:
    #             data_summary[0]['total_case_monthly'][0]['maret'] += 1
    #         elif p.timedateUser.month == 4:
    #             data_summary[0]['total_case_monthly'][0]['april'] += 1
    #         elif p.timedateUser.month == 5:
    #             data_summary[0]['total_case_monthly'][0]['mei'] += 1
    #         elif p.timedateUser.month == 6:
    #             data_summary[0]['total_case_monthly'][0]['juni'] += 1
    #         elif p.timedateUser.month == 7:
    #             data_summary[0]['total_case_monthly'][0]['juli'] += 1
    #         elif p.timedateUser.month == 8:
    #             data_summary[0]['total_case_monthly'][0]['agustus'] += 1
    #         elif p.timedateUser.month == 9:
    #             data_summary[0]['total_case_monthly'][0]['september'] += 1
    #         elif p.timedateUser.month == 10:
    #             data_summary[0]['total_case_monthly'][0]['oktober'] += 1
    #         elif p.timedateUser.month == 11:
    #             data_summary[0]['total_case_monthly'][0]['november'] += 1
    #         elif p.timedateUser.month == 12:
    #             data_summary[0]['total_case_monthly'][0]['desember'] += 1

def createSummary():
    cases, cheat, good = getCaseCounts(daftar_peserta)

    # actual data: cheat = -1, good =1
    # this function input: 0 = 1 (good), 1 = -1 (cheat)

    data_summary[0]['total_case'] = cases
    data_summary[0]['total_label_0'] = good
    data_summary[0]['total_label_1'] = cheat
    data_summary[0]['total_user'] = len(daftar_peserta)

    getMonthlyCases(daftar_peserta)

def renameStatusAndTrack(daftar_peserta):
    for p in daftar_peserta:
        if p.status == 1:
            p.status = "aman"
        else:
            p.status = "terindikasi"
            p.track_progress = "open"


def delete_files_in_directory(directory):
    # Get the list of files in the directory
    files = os.listdir(directory)
    for file_name in files:
        file_path = os.path.join(directory, file_name)
        try:
            os.remove(file_path)  # Delete the file
            print(f'Deleted: {file_path}')
        except Exception as e:
            print(f'Failed to delete: {file_path}, Error: {e}')

def download_folder_with_auth(url, download_dir, username, password):
    # Authenticate using basic auth
    auth = requests.auth.HTTPBasicAuth(username, password)

    # Get the contents of the folder (list of files)
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            file_name = link['href']
            if file_name.endswith('.xlsx'):  # Filter only Excel files, adjust as needed
                file_url = urljoin(url, file_name)
                file_path = os.path.join(download_dir, file_name)
                download_file(file_url, file_path, auth=auth)
        print('Folder downloaded successfully.')
    else:
        print(f'Failed to download folder. Status code: {response.status_code}')

def download_file(file_url, file_path, auth=None):
    # Download the file
    response = requests.get(file_url, auth=auth)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f'Downloaded: {file_path}')
    else:
        print(f'Failed to download file: {file_url}')

def download_data_loop():
    while True:
        waktu, shift = get_time_shift()
        get_data(waktu, shift)
        time.sleep(10)

def start_background_task():
    task_thread = threading.Thread(target=download_data_loop)
    task_thread.daemon = True  # This makes sure the thread will exit when the main program exits
    task_thread.start()

# Route to display usernames and IP addresses
@app.route('/')
def show_usernames():
    waktu, shift = get_time_shift()
    get_data(waktu, shift)
    session, df_data = create_dataframe()
    getPeserta(df_data, session)
    predict(df_data, session)
    add_pred_value(df_data, session)

    return render_template('usernames.html', user_data=daftar_peserta)

@app.route('/get_data')
def download_data_log():
    download_data_loop()

@app.route('/api/daftar_peserta', methods=['GET'])
def post_peserta():
    session, df_data = create_dataframe()
    getPeserta(df_data, session)
    predict(df_data, session)
    add_pred_value(df_data, session)

    renameStatusAndTrack(daftar_peserta)
    createSummary()

    list_data = []
    for p in daftar_peserta:
        data = {'userid' : p.userid, 'firstname': p.firstname, 'lastname': p.lastname, 'timedate': p.timedateUser ,
                'timestart' : p.timestart, 'timefinish' : p.timefinish, 'time_taken' : p.timetaken, 
                'score' : p.score, 'status' : p.status, 'session': p.session, 'track_progress': p.track_progress}
        list_data.append(data)

    return jsonify(list_data)

@app.route('/get_summary', methods=['GET'])
def getSummary():

    return jsonify(data_summary)

# @app.route('/detail_peserta') TBA
# def show_detail_peserta():
     
#     return jsonify(datas)

# Route to user peserta
# @app.route('/clients')
# def show_peserta():
#     waktu, shift = get_time_shift()
#     get_data(waktu, shift)
#     session, df_data = create_dataframe()
#     getPeserta(df_data)
#     predict(df_data, session)
#     add_pred_value(df_data)
#     datas = {
#         peserta: getPeserta
#     }   
#     return jsonify(datas)

if __name__ == '__main__':
    start_background_task()
    app.run(debug=True)