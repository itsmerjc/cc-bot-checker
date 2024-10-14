from quart import Quart
import subprocess
import asyncio

app = Quart(__name__)

async def run_script_loop():
    while True:
        subprocess.run(['python', 'itsmerjc.py'])
        await asyncio.sleep(10)  # Async-friendly sleep

@app.route('/')
async def hello_world():
    asyncio.create_task(run_script_loop())  # Run loop in the background
    return 'Script running in the background. Hello from Koyeb!'

if __name__ == "__main__":
    app.run()
