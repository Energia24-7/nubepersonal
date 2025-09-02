import os
from telethon import TelegramClient
from dotenv import load_dotenv
import asyncio

# Cargar credenciales desde config.env
load_dotenv("config.env")

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

# Sesión del bot
client = TelegramClient("bot_session", api_id, api_hash).start(bot_token=bot_token)

async def main():
    print("✅ Bot conectado y listo")

    # Ejemplo: leer los últimos 10 mensajes de un canal
    canal = "https://t.me/+NzmSbxBEQOI4YWZh"  # Cambia por @nombre o link
    async for mensaje in client.iter_messages(canal, limit=10):
        if mensaje.file:
            print("📂 Archivo encontrado:")
            print(f" - Nombre: {mensaje.file.name}")
            print(f" - Tamaño: {mensaje.file.size/1024:.2f} KB")
            print(f" - File ID: {mensaje.file.id}")
            print("-----------")

asyncio.run(main())
