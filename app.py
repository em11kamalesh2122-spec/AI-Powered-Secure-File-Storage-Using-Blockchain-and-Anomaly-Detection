from flask import Flask, request, render_template_string, send_file, redirect
from encryption import encrypt_file, decrypt_file, calculate_hash
from blockchain import check_access, upload_file_to_blockchain, verify_wallet
from ai_module.anomaly_detection import detect_anomaly, check_risk
from werkzeug.utils import secure_filename

from alerts import security_alert

import os
import datetime
import threading
import time
import jwt

SECRET_KEY = os.environ.get("SECRET_KEY", "supersecret123")

from collections import defaultdict

app = Flask(__name__)

import requests

def get_ip_location(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        return {
            "country": res.get("country"),
            "city": res.get("city"),
            "lat": res.get("lat"),
            "lon": res.get("lon")
        }
    except:
        return {}

# ===============================
# FOLDERS
# ===============================

UPLOAD_FOLDER = 'uploads'
ENCRYPTED_FOLDER = 'encrypted_files'
DECRYPTED_FOLDER = 'decrypted_files'
QUARANTINE_FOLDER = 'quarantine_files'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)
os.makedirs(DECRYPTED_FOLDER, exist_ok=True)
os.makedirs(QUARANTINE_FOLDER, exist_ok=True)

files=os.listdir(ENCRYPTED_FOLDER)


# ===============================
# GLOBAL VARIABLES
# ===============================

attack_counter = 0

failed_attempts = defaultdict(int)
total_attempts = defaultdict(int)
risk_scores = defaultdict(int)

file_hashes = {}
file_owners = {}

file_access_counter = defaultdict(int)

access_logs = []

blocked_ips = set()

threat_level = "🟢 LOW RISK"
system_lockdown = False

last_tx_hash = ""

total_files = 0
total_access = 0
total_failed = 0

blocked_ip_count = 0
attack_detected = 0
quarantined_files = 0

user_last_access = {}

file_risk = {}

zero_trust = True

active_sessions = {}

users = {
    "user1": {"password": "1234", "role": "user"},
    "admin": {"password": "admin123", "role": "admin"}
}

unauthorized_users = set()

attack_map = []


# ===============================
# Verify Token
# ===============================
def verify_token(token):

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return data['user']
    except:
        return None
# ===============================
# Decode Token
# ===============================
def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except:
        return None


# ===============================
# AI INTRUSION PREDICTION
# ===============================

def predict_intrusion():

    total_fail = sum(failed_attempts.values())
    total_try = sum(total_attempts.values())

    if total_try == 0:
        return "🟢 System behaviour normal"

    ratio = total_fail / total_try

    if ratio >= 0.6:
        return "🔴 High probability of cyber attack"
    elif ratio >= 0.3:
        return "🟡 Suspicious activity detected"
    else:
        return "🟢 System stable"

# ===============================
# AI Score
# ===============================
def get_ai_score():
    score = sum(risk_scores.values()) + sum(failed_attempts.values())
    return score


# ===============================
# Risk Engine
# ===============================
def calculate_risk(user, ip):

    score = 0

    score += failed_attempts[user] * 2

    if total_attempts[user] > 5:
        score += 2

    if ip in blocked_ips:
        score += 5

    return score




# ===============================
# RESET THREAT AFTER ATTACK
# ===============================

def reset_threat():

    global threat_level, system_lockdown

    time.sleep(30)

    threat_level = "🟢 LOW RISK"
    system_lockdown = False

    access_logs.append("✅ System threat level reset")


# ===============================
# MAIN PAGE UI
# ===============================

HTML = """

<html>
<head>

<title>AI Secure Storage</title>

<style>

body{
font-family:Consolas,monospace;
background:#020617;
color:#00ffff;
text-align:center;
padding:20px;
}

.container{
background:#020617;
padding:30px;
border-radius:12px;
width:90%;
max-width:600px;
margin:auto;

box-shadow:
0 0 20px #00ffff,
inset 0 0 20px #00ffff;
}

button{
padding:10px;
background:#00c6ff;
border:none;
border-radius:6px;
cursor:pointer;
}

h2,h3{
text-shadow:0 0 10px #00ffff;
}

input{
width:90%;
padding:10px;
margin:10px;
border:1px solid #00ffff;
border-radius:6px;
background:black;
color:#00ffff;
}

button{
padding:10px;
background:#00ffff;
border:none;
border-radius:6px;
cursor:pointer;
font-weight:bold;
}

ul{
list-style:none;
padding:0;
}

li{
background:#020617;
margin:5px;
padding:10px;
border:1px solid #00ffff;
border-radius:6px;
}

.badge{
padding:6px;
border-radius:8px;
font-weight:bold;
}

.low{background:green}
.medium{background:orange}
.high{background:red}

.alert-banner{
background:#ff1e1e;
padding:15px;
border-radius:8px;
font-weight:bold;
margin-top:20px;
animation: blink 1s infinite;
}

@keyframes blink{
0%{opacity:1;}
50%{opacity:0.3;}
100%{opacity:1;}
}

@media (max-width:600px){
.container{
width:95%;
padding:15px;
}
input{
width:100%;
}
}

</style>

</head>

<body>
<h3>👋 Welcome {{user}}</h3>

<p>
This system provides:
<br>🔐 Secure encrypted storage
<br>⛓ Blockchain-based access control
<br>🤖 AI intrusion detection
<br>🛡 Real-time cyber defense monitoring
</p>
<h3>🚨 Unauthorized Users</h3>
<ul>
{% for u in unauth_users %}
<li>{{u}}</li>
{% endfor %}
</ul>


<div class="container">

<h2>🔐 Secure File Upload</h2>

<form method="POST" enctype="multipart/form-data">
<input type="file" name="file" required><br><br>

<input type="text" name="owner" placeholder="Ethereum Owner Address" required><br><br>

<button type="submit">Upload & Encrypt</button>
</form>

<h4>Available Files</h4>
<ul>
{% for f in files %}
<li>
{{f}} -
{% if file_risk.get(f) == "HIGH" %}
<span style="color:red;">🔥 HIGH</span>
{% elif file_risk.get(f) == "MEDIUM" %}
<span style="color:orange;">⚠ MEDIUM</span>
{% else %}
<span style="color:green;">✅ LOW</span>
{% endif %}
</li>

{% endfor %}
</ul>


<hr>

<h3>⬇ Secure Download</h3>

<form method="POST" action="/download">
<input type="text" name="filename" placeholder="Filename" required><br><br>
<input type="text" name="eth_address" placeholder="Ethereum Address" required><br><br>
<input type="hidden" name="token" value="{{token}}"><br><br>

<button type="submit">Verify & Download</button>
</form>

<hr>

<a href="/dashboard?token={{token}}">📊 Security Dashboard</a><br><br>
<a href="/simulate_attack?token={{token}}">⚠ Simulate Cyber Attack</a><br><br>
<a href="/simulate_ransomware?token={{token}}">🧨 Simulate Ransomware</a><br><br>
<a href="/simulate_hacker?token={{token}}">💻 Hacker Terminal Simulation</a><br><br>


<hr>

<h3>Threat Level</h3>

{% if "HIGH" in threat %}
<div class="alert-banner">
🚨 CYBER ATTACK / RANSOMWARE DETECTED 🚨
</div>
{% endif %}

{% if "LOW" in threat %}
<span class="badge low">{{threat}}</span>
{% elif "MEDIUM" in threat %}
<span class="badge medium">{{threat}}</span>
{% else %}
<span class="badge high">{{threat}}</span>
{% endif %}


<h4>Recent Logs</h4>

<ul>
{% for log in logs %}
<li>{{log}}</li>
{% endfor %}
</ul>

<p>{{msg}}</p>
<p style="color:red;">{{error}}</p>

</div><br><br>
<a href="/logout"><button>🚪 Logout</button></a>


</body>
</html>

"""
# ===============================
# DASHBOARD PAGE UI
# ===============================
DASHBOARD_HTML = """

<html>
<head>

<title>AI Cyber Defense SOC Dashboard</title>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

body{
background:#0a0f1c;
color:#00ffff;
font-family:Consolas,monospace;
text-align:center;
padding:20px;
}

h1{
text-shadow:0 0 10px #00ffff;
}

.card{
display:flex;
justify-content:center;
flex-wrap:wrap;
gap:20px;
}

.card-content{

background:#111827;
border:1px solid #00ffff;
padding:20px;
border-radius:10px;
width:200px;

box-shadow:
0 0 10px #00ffff,
inset 0 0 10px #00ffff;

}

canvas{

background:#0f172a;
margin-top:40px;

}

.alert{

background:red;
padding:15px;
margin:20px;
font-weight:bold;

}

ul{

list-style:none;

}

li{

background:#111827;
margin:5px;
padding:8px;

}

</style>

</head>

<body>

<h1>🛡 AI Cyber Defense SOC Dashboard</h1>

{% if "HIGH" in threat %}
<div class="alert">
🚨 SYSTEM LOCKDOWN ACTIVE
</div>
{% endif %}

<div class="card">

<div class="card-content">
<h3>Total Files</h3>
<h2>{{files}}</h2>
</div>

<div class="card-content">
<h3>Total Access</h3>
<h2>{{access}}</h2>
</div>

<div class="card-content">
<h3>Failed Attempts</h3>
<h2>{{failed}}</h2>
</div>

<div class="card-content">
<h3>Threat Level</h3>
<h2>{{threat}}</h2>
</div>

<div class="card-content">
<h3>AI Prediction</h3>
<h2>{{prediction}}</h2>
</div>

<div class="card-content">
<h3>Risk Score</h3>
<h2>{{risk}}</h2>
</div>

<div class="card-content">
<h3>Blocked IPs</h3>
<h2>{{blocked}}</h2>
</div>

<div class="card-content">
<h3>Attacks Detected</h3>
<h2>{{attacks}}</h2>
</div>

<div class="card-content">
<h3>Quarantined Files</h3>
<h2>{{quarantine}}</h2>
</div>

<div class="card-content">
<h3>AI Threat Score</h3>
<h2>{{ai_score}}</h2>
</div>


</div>

<h2>System Activity</h2>

<canvas id="chart" width="400" height="200"></canvas>

<script>

new Chart(document.getElementById("chart"),{

type:"line",

data:{
labels:["Access","Failed"],
datasets:[{
label:"Activity",
data:[{{access}},{{failed}}],
borderWidth:3
}]
}

});

</script>

<h2>🌍 Global Cyber Attack Monitor</h2>

<div id="map" style="height:400px;width:80%;margin:auto;"></div>

<script>

var map=L.map('map').setView([20,0],2);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

function attack(){

var locs={{attack_map|safe}};

var l=locs[Math.floor(Math.random()*locs.length)];

var c=L.circle(l,{
color:'red',
fillOpacity:0.5,
radius:500000
}).addTo(map);

setTimeout(()=>map.removeLayer(c),3000);

}

setInterval(attack,2000);

</script>

<h2>Recent Logs</h2>

<ul>

{% for log in logs %}

<li>{{log}}</li>

{% endfor %}

</ul>

<br>

<a href="/upload?token={{token}}">Back</a>

<h2>⚡ Live Attack Feed</h2>

<div id="feed" style="height:150px;overflow:auto;background:#000;padding:10px;border-radius:8px;"></div>

<script>
function addLog(){
    let msgs = [
        "⚠ Brute force attempt detected",
        "🚨 Unauthorized wallet access",
        "🧨 Ransomware signature detected",
        "🤖 AI anomaly spike",
        "🔐 Encryption key mismatch"
    ];

    let msg = msgs[Math.floor(Math.random()*msgs.length)];

    let div = document.getElementById("feed");
    let p = document.createElement("p");

    p.innerText = new Date().toLocaleTimeString() + " - " + msg;

    div.prepend(p);
}

setInterval(addLog, 2000);
</script>
<script>
function alertSound(){
    let msg = new SpeechSynthesisUtterance("Warning. Cyber attack detected");
    speechSynthesis.speak(msg);
}

setInterval(alertSound, 10000);
</script>



</body>
</html>

"""
# ===============================
# Login 
# ===============================

@app.route('/', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username in users and users[username]["password"] == password:

            token = jwt.encode({
                'user': username,
                'role': users[username]["role"],
                'exp': time.time() + 600 #10min session 
            }, SECRET_KEY, algorithm="HS256")

            return redirect(f"/upload?token={token}")


        else:
            return "❌ Invalid credentials"
    failed_attempts = 3

    check_risk(
    user="kamalesh",
    ip=request.remote_addr,
    file="login",
    failed_attempts=failed_attempts
)

    return """
<html>
<head>
<title>Secure Login</title>

<style>
body{
background: linear-gradient(to right, #141e30, #243b55);
font-family: Arial;
color:white;
display:flex;
justify-content:center;
align-items:center;
height:100vh;
}

.box{
background:#1c1c1c;
padding:30px;
border-radius:12px;
width:300px;
text-align:center;
box-shadow:0 0 15px #00c6ff;
}

input{
width:90%;
padding:10px;
margin:10px;
border:none;
border-radius:6px;
}

button{
padding:10px 20px;
background:#00c6ff;
border:none;
border-radius:6px;
cursor:pointer;
color:white;
font-weight:bold;
}

h2{
margin-bottom:20px;
}

</style>
</head>

<body>

<div class="box">

<h2>🔐 Secure Login</h2>

<form method="POST">
<input name="username" placeholder="Username" required><br>
<input name="password" type="password" placeholder="Password" required><br>

<button>Login</button>
</form>

</div>

</body>
</html>
"""

# ===============================
# FILE UPLOAD
# ===============================

@app.route('/upload', methods=['GET','POST'])
def upload():

    global total_files
    
    token = request.args.get('token')

    data = decode_token(token)

    if not data:
        return """
<script>
alert("⏳ Session Expired! Please login again");
window.location.href="/";
</script>
"""

    role = data.get("role")

    if role not in ["user", "admin"]:
        return "🚫 Unauthorized"

    if not token or not verify_token(token):
        return redirect("/")

    msg=""
    error=""
    filename=""

    if request.method == 'POST':

        f = request.files['file']
        owner = request.form['owner']
        
        if not verify_wallet(owner):
            return "❌ Invalid Owner Wallet"

        if not f:
            error = "No file uploaded"
            return render_template_string(HTML, msg=msg, error=error, logs=access_logs[-5:], threat=threat_level)

        filename = secure_filename(f.filename)

        # ✅ FILE TYPE CHECK (FIXED POSITION)
        if not filename.endswith(('.txt', '.pdf', '.docx')):
            error = "❌ Invalid file type"
            return render_template_string(HTML, msg=msg, error=error, logs=access_logs[-5:], threat=threat_level)

        path = os.path.join(UPLOAD_FOLDER, filename)
        f.save(path)

        enc_path = os.path.join(ENCRYPTED_FOLDER, filename + ".enc")

        encrypt_file(path, enc_path)

        os.remove(path)

        file_hash = calculate_hash(enc_path)

        file_hashes[filename] = file_hash
        file_owners[filename] = owner
        
        file_risk[filename] = "LOW"

        try:
            upload_file_to_blockchain(filename)
            msg = "✅ File encrypted & stored securely"
        except Exception as e:
            error = str(e)

        total_files += 1
        
        msg = f"✅ File uploaded: {filename}"
    
    
    return render_template_string(
    HTML,
    msg=msg,
    error=error,
    logs=access_logs[-5:],
    threat=threat_level,
    files=os.listdir(ENCRYPTED_FOLDER),
    file_risk=file_risk,
    token=token,
    user=data.get("user")

    )


# ===============================
# FILE DOWNLOAD
# ===============================

@app.route('/download', methods=['POST'])
def download():

    global threat_level, system_lockdown, total_access, total_failed
    global blocked_ip_count, attack_detected, quarantined_files

    token = request.form.get('token')

    user_from_token = verify_token(token)

    if not user_from_token:
        return "❌ Invalid or expired token"


    filename = request.form['filename']
    user = request.form['eth_address']
    # 🔐 SESSION LOCK CHECK
    if user in active_sessions:
        if time.time() - active_sessions[user] < 2:
            return "⚠ Suspicious repeated session blocked"

    ip = request.remote_addr
    location = get_ip_location(ip)

    access_logs.append(
        f"🌍 {ip} | {location.get('city')} | {location.get('country')}"
    )

    
    print("Requested file:", filename)
    print("Available files:", os.listdir(ENCRYPTED_FOLDER))

    enc_path = os.path.join(ENCRYPTED_FOLDER, filename + ".enc")
    dec_path = os.path.join(DECRYPTED_FOLDER, f"{user}_{filename}")
    
    now = time.time()
    if user in user_last_access:
        if now - user_last_access[user] < 3:
            if risk_scores[user] >= 6:

                threat_level = "🔴 HIGH RISK"
                system_lockdown = True

                file_risk[filename] = "HIGH"   # ✅ tagging

                if ip not in blocked_ips:
                    blocked_ips.add(ip)
                    attack_detected += 1
                    blocked_ip_count += 1

                access_logs.append(f"🚫 IP BLOCKED: {ip}")

                # 💣 AUTO DELETE (EXTREME MODE)
                if risk_scores[user] >= 8:
                    if os.path.exists(enc_path):
                        os.remove(enc_path)

                    access_logs.append("💣 File deleted due to extreme threat")
                    return "💣 File destroyed due to high risk attack"

                security_alert(user, ip, filename, risk_scores[user])

                threading.Thread(target=reset_threat).start()

                return "⛔ Access Denied"
            unauthorized_users.add(user)



            risk_scores[user] += 2
            access_logs.append("⚡ Rapid request detected")
    
    
    if zero_trust and (risk_scores[user] > 3 or ip in blocked_ips):

        return "🚫 Zero Trust Policy Blocked Access"



    user_last_access[user] = now


    if system_lockdown:
        return "🚨 SYSTEM LOCKDOWN ACTIVE"

    if ip in blocked_ips:
        return "🚫 Your IP is blocked"

    total_access += 1
    total_attempts[user] += 1
    
   
    file_access_counter[filename] += 1

    

    if not os.path.exists(enc_path):
        return "File not found"

    # =========================
    # HASH VERIFY
    # =========================

    stored_hash = file_hashes.get(filename)
    current_hash = calculate_hash(enc_path)

    if stored_hash != current_hash:

        quarantine_path = os.path.join(QUARANTINE_FOLDER, filename + ".enc")

        os.rename(enc_path, quarantine_path)
        quarantined_files += 1

        access_logs.append("⚠ File moved to quarantine")

        return "File integrity compromised"

    # =========================
    # BLOCKCHAIN ACCESS CHECK
    # =========================
    if not verify_wallet(user):
        return "❌ Invalid wallet address"

    access_allowed = check_access(filename, user)

    if not access_allowed:

        failed_attempts[user] += 1
        total_failed += 1

        risk_scores[user] += 2

        access_logs.append(
            f"{datetime.datetime.now()} | UNAUTHORIZED ACCESS | {user} | {ip}"
        )

        anomaly = detect_anomaly(user)


        if anomaly:
            risk_scores[user] += 3
            threat_level = "🟡 MEDIUM RISK"
            access_logs.append("🤖 AI detected abnormal behaviour")

        return "⛔ Unauthorized Access"


    else:

        risk_scores[user] = max(0, risk_scores[user] - 1)

        access_logs.append(
            f"{datetime.datetime.now()} |ACCESS GRANTED | {user} | {ip}"
        )
        active_sessions[user] = time.time()#session Track

    detect_anomaly(user)

    # =========================
    # HIGH RISK TRIGGER
    # =========================
    risk_scores[user] = calculate_risk(user, ip)

    if risk_scores[user] >= 6:
        if location and location.get("lat"):
            attack_map.append([location['lat'], location['lon']])


        threat_level = "🔴 HIGH RISK"
        system_lockdown = True
        
        if ip not in blocked_ips:
            blocked_ips.add(ip)
            attack_detected += 1
            blocked_ip_count += 1


        access_logs.append(f"🚫 IP BLOCKED: {ip}")

        security_alert(user, ip, filename, risk_scores[user])

        threading.Thread(target=reset_threat).start()

        return "⛔ Access Denied"
    elif risk_scores[user] >= 3:
        file_risk[filename] = "🟡 MEDIUM"
    else:
        file_risk[filename] = "🟢 LOW"

    # =========================
    # FILE DECRYPTION
    # =========================

    decrypt_file(enc_path, dec_path)

    return send_file(dec_path, as_attachment=True)


# ===============================
# CYBER ATTACK SIMULATION
# ===============================

@app.route('/simulate_attack')
def simulate_attack():

    global threat_level,attack_counter

    attack_counter+=1

    threat_level="🔴 HIGH RISK"

    access_logs.append("⚠ Simulated Cyber Attack")

    threading.Thread(target=reset_threat).start()

    return redirect("/")


# ===============================
# RANSOMWARE SIMULATION
# ===============================

@app.route('/simulate_ransomware')
def simulate_ransomware():

    global threat_level

    threat_level="🔴 HIGH RISK"

    access_logs.append("🧨 Ransomware behaviour detected")

    threading.Thread(target=reset_threat).start()

    return """
<h1 style='color:red;'>⚠ YOUR FILES ARE ENCRYPTED ⚠</h1>
<p>Send 1 ETH to recover files</p>
<a href='/'>Try Recovery</a>
"""



# ===============================
# DASHBOARD
# ===============================

@app.route('/dashboard')
def dashboard():
    
    ai_score = get_ai_score()
    ai_score=ai_score

    token = request.args.get('token')
    data = decode_token(token)

    if not data or data.get("role") != "admin":
        return "🚫 Admin access only"


    prediction = predict_intrusion()

    total_risk = sum(risk_scores.values())

    return render_template_string(
    DASHBOARD_HTML,
    files=total_files,
    access=total_access,
    failed=total_failed,
    threat=threat_level,
    prediction=prediction,
    risk=total_risk,
    blocked=blocked_ip_count,
    attacks=attack_detected,
    attack_map=attack_map,
    quarantine=quarantined_files,
    logs=access_logs[-10:],
    unauth_users=list(unauthorized_users),
    token=token   
)





# ===============================
# HACKER TERMINAL SIMULATION
# ===============================

@app.route('/simulate_hacker')
def simulate_hacker():

    return "<h2>⚠ Hacker Simulation Running...</h2><br><a href='/'>Return</a>"
# ===============================
# Logout
# ===============================
@app.route('/logout')
def logout():
    return redirect("/")



# ===============================

if __name__ == '__main__':
    app.run(debug=True)
