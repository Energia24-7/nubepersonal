import os
import threading
import asyncio
from datetime import datetime
from flask import Flask, render_template_string, send_from_directory
from telethon import TelegramClient, events

# -----------------------------
# Configuración
# -----------------------------
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
channel_username = os.getenv("CHANNEL_USERNAME")  # Ej: "MiCanal" sin @

FILES_DIR = "files"
os.makedirs(FILES_DIR, exist_ok=True)

# Filtros
ALLOWED_EXTENSIONS = {"jpg", "png", "pdf"}   # extensiones válidas
MAX_FILE_SIZE_MB = 10                        # máximo 10 MB
MIN_DATE = datetime(2025, 1, 1)              # ignora archivos subidos antes de esta fecha

# -----------------------------
# Cliente Telethon usando sesión
# -----------------------------
SESSION_NAME = 'user_session'  # Archivo: user_session.session
client = TelegramClient(SESSION_NAME, api_id, api_hash)


# -----------------------------
# Handler de mensajes nuevos
# -----------------------------
@client.on(events.NewMessage(chats=channel_username))
async def handler(event):
    message = event.message

    if not message.file:
        return  # ignorar si no es archivo

    # Fecha de subida
    if message.date.replace(tzinfo=None) < MIN_DATE:
        print(f"⏭ Ignorado por fecha: {message.id}")
        return

    # Tamaño en MB
    size_mb = (message.file.size or 0) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        print(f"⏭ Ignorado por tamaño: {message.id} ({size_mb:.2f} MB)")
        return

    # Nombre del archivo
    if message.photo:
        filename = f"photo_{message.id}.jpg"
    else:
        filename = message.file.name or f"file_{message.id}.bin"

    # Validar extensión
    ext = filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        print(f"⏭ Ignorado por extensión: {filename}")
        return

    # Descargar si no existe
    path = os.path.join(FILES_DIR, filename)
    if not os.path.exists(path):
        await message.download_media(path)
        print(f"✅ Guardado: {filename}")


# -----------------------------
# Hilo para ejecutar el bot
# -----------------------------
def run_bot():
    asyncio.run(client.start())
    print("🤖 Bot escuchando mensajes en tiempo real...")
    client.run_until_disconnected()


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
            <h1 class="mb-4 text-center">📂 Archivos desde Telegram</h1>
            
            {% if files %}
            <table class="table table-bordered table-striped">
                <thead class="table-dark">
                    <tr>
                        <th>#</th>
                        <th>Archivo</th>
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
                Aún no hay archivos disponibles. 📭
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
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
