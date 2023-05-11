import telebot
import os
from PIL import Image
from io import BytesIO
import subprocess

# Bot token
bot = telebot.TeleBot("6222507134:AAEHzpOSwXlqeAQwpljb-DGtKieaCl22Cic")

# Lightroom presets list
PRESETS = [
    ("Preset1", "/path/to/preset1.lrtemplate"),
    ("tamooo2", "/path/to/preset2.lrtemplate"),
    ("Preset3", "/path/to/preset3.lrtemplate")
]

# Apply a Lightroom preset to an image
def apply_preset(image_bytes, preset_path):
    with subprocess.Popen(['lightroom', '-e', '-p', preset_path, '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        output, err = proc.communicate(input=image_bytes)
        if err:
            raise Exception(err.decode())
        return output

# Handle incoming messages
@bot.message_handler(content_types=["photo"])
def handle_photos(message):
    # Download the photo as bytes
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_bytes = bot.download_file(file_info.file_path)

    # Apply the selected preset to the image
    image = Image.open(BytesIO(file_bytes))
    preset_name = "Preset1"  # Replace with code to get the selected preset name from the user
    preset_path = next(path for name, path in PRESETS if name == preset_name)
    output_bytes = apply_preset(file_bytes, preset_path)

    # Send the processed image back to the user
    bot.send_photo(message.chat.id, output_bytes)

    # Forward the processed image to the owner chat
    owner_chat_id = "1053520914"  # Replace with your own owner chat ID
    bot.forward_message(owner_chat_id, message.chat.id, message.message_id)

# Handle the /start command
@bot.message_handler(commands=["start"])
def handle_start(message):
    # Check if the user is a member of the required channel
    channel_username = "tamo_tech"  # Replace with your own channel username
    user_id = message.from_user.id
    try:
        member = bot.get_chat_member(channel_username, user_id)
        if member.status == "member" or member.status == "creator":
            # User is a member of the channel, send welcome message
            owner_id = "YOUR_OWNER_ID"
            bot.send_message(message.chat.id, f"Welcome to the Lightroom Bot! This bot allows you to apply Lightroom presets to your photos.\n\nSend me a photo and choose a preset to apply.\n\nFor assistance, contact @{owner_id} or visit our social page: YOUR_SOCIAL_LINK")
        else:
            # User is not a member of the channel, send join message
            channel_link = f"https://t.me/{channel_username}"
            bot.send_message(message.chat.id, f"To use this bot, you must join our channel first: {channel_link}")
    except Exception as e:
        print(e)

# Start the bot
bot.polling()