from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/')
def hello_world():
    # Run another Python script
    subprocess.run(['python', 'itsmerjc.py'])
    return 'Hello from Koyeb'

if __name__ == "__main__":
    app.run()
