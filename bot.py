import os
import asyncio
import threading
from flask import Flask, send_from_directory, render_template_string
from telethon import TelegramClient, events

# ======================
# Configuración
# ======================
API_ID = int(os.getenv("API_ID", "123456"))  # tu API_ID de my.telegram.org
API_HASH = os.getenv("API_HASH", "tu_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "tu_bot_token")

SESSION = "bot_session"  # nombre de archivo de sesión
FILES_DIR = "files"      # carpeta donde se guardan archivos
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1001234567890"))  # tu canal

# Crear carpeta si no existe
os.makedirs(FILES_DIR, exist_ok=True)

# Cliente de Telethon como BOT
client = TelegramClient(SESSION, API_ID, API_HASH)

# ======================
# Flask (para Render)
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
    if event.message.file:  # si el mensaje tiene archivo
        path = os.path.join(FILES_DIR, event.message.file.name or "unnamed")
        await event.message.download_media(file=path)
        print(f"✅ Archivo guardado: {path}")

# ======================
# Hilos: Flask + Bot
# ======================
def run_flask():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

def run_bot():
    asyncio.run(client.start(bot_token=BOT_TOKEN))
    client.run_until_disconnected()

if __name__ == "__main__":
    # Flask en un hilo
    threading.Thread(target=run_flask, daemon=True).start()
    # Bot en el principal
    run_bot()
