import telebot
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials

# Telegram Bot Token
BOT_TOKEN = '8141760098:AAF1C1GS-9Q9BIEltlYAiapByCv4gwtBjEs'
bot = telebot.TeleBot(BOT_TOKEN)

# Google Drive Credentials
GOOGLE_CREDENTIALS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def upload_to_gdrive(file_path, file_name):
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': file_name}
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

@bot.message_handler(content_types=['document', 'photo'])
def handle_files(message):
    file_id = message.document.file_id if message.content_type == 'document' else message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    file_name = message.document.file_name if message.content_type == 'document' else f"{file_id}.jpg"
    file_path = f"./{file_name}"

    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    drive_file_id = upload_to_gdrive(file_path, file_name)
    bot.reply_to(message, f"File uploaded to Google Drive with ID: {drive_file_id}")
    os.remove(file_path)

bot.polling()
