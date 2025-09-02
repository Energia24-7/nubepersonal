import os
import asyncio
from telethon import TelegramClient, events

# Lee las variables desde Render
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

# Inicializa el cliente como BOT
client = TelegramClient("bot_session", api_id, api_hash).start(bot_token=bot_token)

@client.on(events.NewMessage(pattern="/start"))
async def handler(event):
    await event.reply("👋 ¡Hola! Estoy corriendo en Render 24/7 🚀")

async def main():
    print("✅ Bot conectado y escuchando mensajes...")
    await client.run_until_disconnected()

asyncio.run(main())
