from flask import Flask
import os
import random
from datetime import datetime
from telethon import TelegramClient, errors, events
import asyncio
import threading

# Flask app
app = Flask(__name__)

# Telegram API credentials
api_id = '25686279'
api_hash = '585e642db1018af44e670f344fb616ef'
phone_number = '+639644135150'
client = TelegramClient('session_name_itsmerjc', api_id, api_hash)

# Luhn algorithm to generate the last check digit
def luhn_residue(digits):
    sum_digits = 0
    for i, digit in enumerate(reversed(digits)):
        n = int(digit)
        if i % 2 == 0:  # Double every second digit
            n = n * 2
            if n > 9:  # If doubling results in a number greater than 9, subtract 9
                n = n - 9
        sum_digits += n
    return (10 - (sum_digits % 10)) % 10

# Generate a credit card number based on the provided BIN
def generate_card_number(bin_format):
    digits = list(bin_format)
    
    while len(digits) < 15:
        digits.append(str(random.randint(0, 9)))  # Randomly generate digits until we have 15 digits
    
    check_digit = luhn_residue(digits)  # Generate the check digit using Luhn algorithm
    digits.append(str(check_digit))  # Add the check digit as the final digit
    
    return ''.join(digits)

# Generate random expiry date
def generate_expiry_date():
    current_year = datetime.now().year % 100  # Get the last two digits of the current year (e.g., 24 for 2024)
    current_month = datetime.now().month

    # Generate a future month and year, ensuring the date is valid
    future_year = random.randint(current_year, current_year + 7)  # Random year up to 7 years from now
    if future_year == current_year:
        month = random.randint(current_month, 12)  # Ensure month is not earlier than the current month
    else:
        month = random.randint(1, 12)  # Any valid month for future years

    return f"{str(month).zfill(2)}|{str(future_year).zfill(2)}"

# Generate random CVV
def generate_cvv():
    return str(random.randint(0, 999)).zfill(3)

# Generate card details
def generate_card(bin_format):
    card_number = generate_card_number(bin_format)
    expiry_date = generate_expiry_date()
    cvv = generate_cvv()
    return f"{card_number}|{expiry_date}|{cvv}"

# Function to handle /setbin command and save BINs to the file
@client.on(events.NewMessage(pattern=r'/setbin (.+)'))
async def set_bin(event):
    bin_data = event.pattern_match.group(1)
    bin_list = [bin.strip() for bin in bin_data.split(',') if bin.strip()]
    
    if bin_list:
        write_bin_list('kido.txt', bin_list)
        await event.reply(f"BIN list has been updated:\n{', '.join(bin_list)}")
    else:
        await event.reply("Please provide valid BIN numbers.")

# Start the Telegram bot
async def start_bot():
    await client.start(phone=phone_number)
    me = await client.get_me()
    print(f"Logged in as: {me.username} ({me.id})")

    chat_id = 'bmb0H9EiKU0YzZl'  # Replace with the correct chat ID or username
    bin_file = 'kido.txt'

    # Read the BINs from the file
    bin_list = read_bin_list(bin_file)

    # Send card details in a loop
    while True:
        for bin_format in bin_list:
            card_details = generate_card(bin_format)
            full_command = f"$avs {card_details}"

            try:
                sent_message = await client.send_message(chat_id, full_command)
                print(f"Sent: {full_command}")
            except Exception as e:
                print(f"Error occurred: {e}")
                continue

            # Wait before the next iteration
            await asyncio.sleep(20)

# Start the Telegram bot in a background thread
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

# Flask route to start the bot
@app.route('/start_bot')
def start_bot_route():
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    return "Telegram bot started."

# Flask route to check if the app is running
@app.route('/')
def hello_world():
    return 'Hello from Flask and Telegram bot!'

# Flask route to stop the bot (optional, you'll have to handle how to stop it)
@app.route('/stop_bot')
def stop_bot_route():
    # Logic to stop the bot (needs to be implemented based on your setup)
    return "Bot stopped (not implemented)."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
