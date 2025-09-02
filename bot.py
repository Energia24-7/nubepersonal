import os
import threading
from flask import Flask
from telethon import TelegramClient, events

# Variables de entorno que configuraste en Render
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

# Inicia cliente de Telethon
client = TelegramClient("bot", api_id, api_hash).start(bot_token=bot_token)

# Ejemplo de comando en Telegram
@client.on(events.NewMessage(pattern="/start"))
async def handler(event):
    await event.reply("✅ Bot corriendo en Render 🚀")

# Hilo para correr el bot
def run_bot():
    print("🤖 Iniciando bot...")
    client.run_until_disconnected()

# Flask para mantener el puerto abierto
app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Bot está activo en Render ✅"

if __name__ == "__main__":
    # Ejecuta bot en segundo plano
    threading.Thread(target=run_bot).start()
    # Flask mantiene puerto que Render necesita
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
