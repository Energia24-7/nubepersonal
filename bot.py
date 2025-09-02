import os
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv("config.env")

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

client = TelegramClient("bot_session", api_id, api_hash).start(bot_token=bot_token)

async def main():
    print("✅ Bot conectado")

with client:
    client.loop.run_until_complete(main())
