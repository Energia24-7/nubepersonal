import os
import asyncio
import threading
from telethon import TelegramClient
from flask import Flask, send_from_directory, render_template_string

# =====================
# Configuración
# =====================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = "user_session"  # Archivo .session creado en tu PC
CHANNEL_ID = os.getenv("CHANNEL_ID", "NombreDelCanal")  # sin @
DOWNLOAD_DIR = "files"

# Crear carpeta si no existe
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Cliente de usuario
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# =====================
# Lógica para leer canal
# =====================
async def check_channel():
    await client.start()  # Usará user_session.session, no pedirá número ni OTP
    print("✅ Cliente conectado como usuario")

    channel = await client.get_entity(CHANNEL_ID)

    async for message in client.iter_messages(channel, limit=20):  # últimos 20 mensajes
        if message.file:
            path = os.path.join(DOWNLOAD_DIR, message.file.name or f"file_{message.id}")
            if not os.path.exists(path):
                await message.download_media(file=path)
                print(f"📥 Archivo guardado: {path}")

    # Loop para nuevos mensajes
    while True:
        async for message in client.iter_messages(channel, limit=5):
            if message.file:
                path = os.path.join(DOWNLOAD_DIR, message.file.name or f"file_{message.id}")
                if not os.path.exists(path):
                    await message.download_media(file=path)
                    print(f"📥 Nuevo archivo: {path}")
        await asyncio.sleep(15)  # cada 15s revisa el canal

# =====================
# Servidor Flask
# =====================
app = Flask(__name__)

@app.route("/")
def index():
    files = os.listdir(DOWNLOAD_DIR)
    html = """
    <h1>📂 Archivos descargados</h1>
    <ul>
      {% for file in files %}
        <li><a href="/files/{{file}}">{{file}}</a></li>
      {% endfor %}
    </ul>
    """
    return render_template_string(html, files=files)

@app.route("/files/<path:filename>")
def download_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

# =====================
# Ejecutar bot y web
# =====================
def run_bot():
    asyncio.run(check_channel())

def run_web():
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()
    run_web()

