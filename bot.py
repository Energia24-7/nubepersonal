import os
import asyncio
import logging
from telethon import TelegramClient, events
from flask import Flask, send_from_directory

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Credenciales de la API de Telegram
API_ID = int(os.getenv("API_ID", "14622520"))
API_HASH = os.getenv("API_HASH", "tu_api_hash")
SESSION = "bot_session"

# ⚠️ IMPORTANTE: Usa el ID real del canal con -100 al inicio
CHANNEL_ID = -1002987420895  

# Directorio de subida
FILES_DIR = "files"
os.makedirs(FILES_DIR, exist_ok=True)

# Inicializar cliente de Telethon
client = TelegramClient(SESSION, API_ID, API_HASH)

# Flask para servir archivos
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot y servidor Flask corriendo en Render"

@app.route("/files/<path:filename>")
def serve_file(filename):
    return send_from_directory(FILES_DIR, filename)

# Escuchar mensajes en el canal
@client.on(events.NewMessage(chats=CHANNEL_ID))
async def handler(event):
    if event.message.file:
        path = await event.message.download_media(file=FILES_DIR)
        logger.info(f"📥 Archivo recibido: {path}")
    else:
        logger.info("Mensaje recibido, pero sin archivo.")

# Función para correr el bot
async def run_bot():
    logger.info("🤖 Iniciando bot de Telegram...")
    await client.start()
    logger.info("✅ Bot conectado a Telegram.")
    await client.run_until_disconnected()

# Ejecutar bot en un hilo separado
def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())

if __name__ == "__main__":
    import threading

    # Hilo para el bot
    t = threading.Thread(target=start_bot, daemon=True)
    t.start()

    # Correr Flask en el puerto de Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

