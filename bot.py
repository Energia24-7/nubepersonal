import os
import threading
from flask import Flask, render_template_string, send_from_directory
from telethon import TelegramClient, events

# -----------------------------
# Configuración
# -----------------------------
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
channel_username = os.getenv("CHANNEL_USERNAME")  # ej: "MiCanal"

FILES_DIR = "files"
os.makedirs(FILES_DIR, exist_ok=True)

# -----------------------------
# Cliente de usuario Telethon
# -----------------------------
client = TelegramClient("user_session", api_id, api_hash)

@client.on(events.NewMessage(func=lambda e: e.file))
async def handler(event):
    # Filtrar solo el canal que te interesa
    if event.chat.username == channel_username:
        filename = event.file.name or "archivo.bin"
        file_path = os.path.join(FILES_DIR, filename)
        await event.download_media(file_path)
        print(f"📂 Archivo guardado: {filename}")

# -----------------------------
# Hilo para el bot
# -----------------------------
def run_bot():
    print("🤖 Bot corriendo y escuchando archivos...")
    client.start()
    client.run_until_disconnected()

# -----------------------------
# Flask app
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
