import os
from telethon import TelegramClient, events

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

# Inicializa el cliente como BOT
client = TelegramClient("bot_session", api_id, api_hash).start(bot_token=bot_token)

@client.on(events.NewMessage(pattern="/start"))
async def start_handler(event):
    await event.reply("👋 Hola, estoy corriendo en Render 24/7 🚀")

print("✅ Bot conectado y escuchando mensajes...")

# Esto reemplaza asyncio.run(main())
client.run_until_disconnected()
