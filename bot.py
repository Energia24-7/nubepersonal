import os
import threading
import asyncio
from flask import Flask, render_template_string, send_from_directory
from telethon import TelegramClient

# -----------------------------
# Configuración
# -----------------------------
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
channel_username = os.getenv("CHANNEL_USERNAME")  # Ej: "MiCanal" sin @

FILES_DIR = "files"
os.makedirs(FILES_DIR, exist_ok=True)

# -----------------------------
# Cliente Telethon usando sesión preautenticada
# -----------------------------
SESSION_NAME = 'user_session'  # Archivo: user_session.session
client = TelegramClient(SESSION_NAME, api_id, api_hash)

# -----------------------------
# Función de polling para revisar canal
# -----------------------------
async def check_channel():
    await client.connect()
    if not await client.is_user_authorized():
        print("❌ Sesión no autorizada. Debes subir user_session.session")
        return

    print("🤖 Bot conectado y revisando canal...")
    channel = await client.get_entity(channel_username)
    downloaded_files = set(os.listdir(FILES_DIR))

    while True:
        try:
            async for message in client.iter_messages(channel, limit=20):
                if message.file:
                    filename = message.file.name or f"{message.id}.bin"
                    if filename not in downloaded_files:
                        path = os.path.join(FILES_DIR, filename)
                        await message.download_media(path)
                        downloaded_files.add(filename)
                        print(f"[LOG] 📂 Archivo guardado: {filename}")
        except Exception as e:
            print(f"[ERROR] {e}")
        await asyncio.sleep(10)  # Revisa cada 10 segundos

# -----------------------------
# Hilo para ejecutar el bot
# -----------------------------
def run_bot():
    asyncio.run(check_channel())

# -----------------------------
# Flask app para interfaz web
# -----------------------------
app = Flask(__name__)

@app.route("/")
def home():
    files = os.listdir(FILES_DIR)
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Gestor de Archivos Telegram</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container py-5">
            <h1 class="mb-4 text-center">📂 Archivos subidos desde Telegram</h1>
            
            {% if files %}
            <table class="table table-bordered table-striped">
                <thead class="table-dark">
                    <tr>
                        <th>#</th>
                        <th>Nombre del archivo</th>
                        <th>Acción</th>
                    </tr>
                </thead>
                <tbody>
                    {% for f in files %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td>{{ f }}</td>
                        <td>
                            <a href="/download/{{f}}" class="btn btn-primary btn-sm">⬇ Descargar</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <div class="alert alert-info text-center">
                Aún no hay archivos subidos. 📭
            </div>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html, files=files)

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(FILES_DIR, filename, as_attachment=True)

# -----------------------------
# Ejecutar bot + Flask
# -----------------------------
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
