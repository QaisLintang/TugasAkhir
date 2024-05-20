from flask import Flask, request, jsonify
import os
import requests
from requests.auth import HTTPBasicAuth
import urllib.parse

app = Flask(__name__)

# Delete function
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

# Download function
def download_folder_with_auth(url, download_dir, username, password):
    # First, clean the download directory
    delete_files_in_directory(download_dir)

    # Authenticate using basic auth
    auth = HTTPBasicAuth(username, password)

    # Get the contents of the folder (list of files)
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        for file_name in response.json()['files']:
            file_url = f"{url}/{file_name}"
            file_path = os.path.join(download_dir, file_name)
            download_file(file_url, file_path, auth=auth)
        print('Files downloaded successfully.')
    else:
        print('Failed to download files.')

def download_file(file_url, file_path, auth=None):
    # Download the file
    response = requests.get(file_url, auth=auth)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f'Downloaded: {file_path}')
    else:
        print(f'Failed to download file: {file_url}')

# Define local data
time = '01 April 2024'
current_shift = 'Shift 1'
encoded_time = urllib.parse.quote(time)
encoded_shift = urllib.parse.quote(current_shift)
base_url = "https://sandbox.telkomuniversity.ac.id/laclog/lac-eprt-log/Quiz%20Attempts/"
url = f"{base_url}{encoded_time}/{encoded_shift}/"
download_dir = 'downloaded_files'
username = 'serverlog'
password = 'S3rverl0g!'

# Trigger download on Flask app startup
download_folder_with_auth(url, download_dir, username, password)

if __name__ == '__main__':
    app.run(debug=True)
