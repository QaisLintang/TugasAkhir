import subprocess

url = "https://sandbox.telkomuniversity.ac.id/laclog/lac-eprt-log/Quiz%20Attempts/1%20April%202024/Shift%201/"
command = f'wget --user=serverlog --password=S3rverl0g! -r -np -nH --cut-dirs=3 -R "index.html*" {url}'

subprocess.run(command, shell=True)