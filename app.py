# app.py (Flask program)

from flask import Flask, render_template
import time
import mysql.connector
import datetime as datetime
import numpy as np
import pandas as pd
import urllib.parse
import subprocess
import pytz
import glob
from sklearn.ensemble import IsolationForest

app = Flask(__name__)

model = 'models\iso_forest.joblib'
daftar_peserta = []

class peserta:
  def __init__(self, firstname, lastname, userid, timestart, timefinish, score):
    self.firstname = firstname
    self.lastname = lastname
    self.userid = userid
    self.timestart = timestart
    self.timefinish = timefinish
    self.score = score
    self.status = 1

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
    # time = formatted_date
    # current_shift = shift
    time = '01 April 2024'
    current_shift = 'Shift 1'

    # Assuming 'time' and 'current_shift' are already defined
    encoded_time = urllib.parse.quote(time)
    encoded_shift = urllib.parse.quote(current_shift)

    url = f"https://sandbox.telkomuniversity.ac.id/laclog/lac-eprt-log/Quiz%20Attempts/{encoded_time}/{encoded_shift}/"
    command = f'wget --user=serverlog --password=S3rverl0g! -r -np -nH --cut-dirs=3 -R "index.html*" {url}'

    subprocess.run(command, shell=True)

def create_dataframe(current_shift):
    data_dir = f'/content/01 April 2024/{current_shift}/*'
    list_file = glob.glob(data_dir)

    if len(list_file) == 1:
        data = f'/content/01 April 2024/{current_shift}/Listening.xlsx'
        session = 'listening'
    elif len(list_file) == 2:
        data = f'/content/01 April 2024/{current_shift}/Grammar.xlsx'
        session = 'grammar'
    elif len(list_file) == 3:
        data = f'/content/01 April 2024/{current_shift}/Reading.xlsx'
        session = 'reading'

    df_data = pd.read_excel(data, header=0)

    return session, df_data

def getPeserta(df_data):
  for index, row in df_data.iterrows():
    # Check if the userid is already in daftar_peserta
    if not any(p.userid == row['id'] for p in daftar_peserta):
        newPeserta = peserta(row['firstname'], row['lastname'], row['id'], row['timestart'], row['timefinish'], row['score'])
        daftar_peserta.append(newPeserta)

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

def add_pred_value(df_data):
   for index, row in df_data.iterrows():
    for p in daftar_peserta:
        if p.userid == row['id']:
            p.status = row['anomaly_score_iso']

# Route to display usernames and IP addresses
@app.route('/')
def show_usernames():
    time, shift = get_time_shift()
    get_data(time, shift)
    session, df_data = create_dataframe(shift)
    getPeserta(df_data)
    predict(df_data, session)
    add_pred_value(df_data)

    return render_template('usernames.html', user_data=daftar_peserta)


if __name__ == '__main__':
    app.run(debug=True)
