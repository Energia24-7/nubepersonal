import os
import threading
from flask import Flask, send_from_directory, render_template_string
from telethon import TelegramClient, events

# ======================
# Configuración
# ======================
API_ID = int(os.getenv("API_ID", "123456"))  # tu API_ID
API_HASH = os.getenv("API_HASH", "tu_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "tu_bot_token")

SESSION = "bot_session"
FILES_DIR = "files"
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1001234567890"))

os.makedirs(FILES_DIR, exist_ok=True)

# Cliente BOT
client = TelegramClient(SESSION, API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ======================
# Flask
# ======================
app = Flask(__name__)

@app.route("/")
def index():
    files = os.listdir(FILES_DIR)
    file_list = "".join(
        f"<li><a href='/files/{f}' target='_blank'>{f}</a></li>" for f in files
    )
    return render_template_string("""
        <h1>📂 Archivos subidos</h1>
        <ul>{{ file_list|safe }}</ul>
    """, file_list=file_list)

@app.route("/files/<path:filename>")
def download_file(filename):
    return send_from_directory(FILES_DIR, filename, as_attachment=True)

# ======================
# Bot Handlers
# ======================
@client.on(events.NewMessage(chats=CHANNEL_ID))
async def handler(event):
    if event.message.file:
        path = os.path.join(FILES_DIR, event.message.file.name or "unnamed")
        await event.message.download_media(file=path)
        print(f"✅ Archivo guardado: {path}")

# ======================
# Hilos
# ======================
def run_flask():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

def run_bot():
    print("🤖 Bot iniciado y escuchando el canal...")
    client.run_until_disconnected()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
