import os
import sqlite3
import requests
import time
from flask import Flask, jsonify, render_template
from flask_cors import CORS

from identity_routes import identity_bp
from relay_routes import relay_bp
from memory_routes import memory_bp
from hud_routes import hud
from hud_rate_limit import get_used_today

# -----------------------------
# GLOBAL REQUEST LOG
# -----------------------------
REQUEST_LOG = []

def log_request(data):
    timestamp = time.strftime("%H:%M:%S")
    REQUEST_LOG.append(f"[{timestamp}] {data}")
    if len(REQUEST_LOG) > 50:
        REQUEST_LOG.pop(0)

# -----------------------------
# FLASK APP
# -----------------------------
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# -----------------------------
# BLUEPRINTS
# -----------------------------
app.register_blueprint(identity_bp)
app.register_blueprint(relay_bp)
app.register_blueprint(memory_bp)
app.register_blueprint(hud)

# -----------------------------
# WEB PAGES
# -----------------------------
@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/status/html")
def status_html():
    return render_template("status.html")

@app.route("/admin")
def admin_dashboard():
    return render_template("admin.html")

# -----------------------------
# JSON STATUS
# -----------------------------
@app.route("/status")
def status():
    return jsonify({"status": "running"})

@app.route("/status/groq")
def status_groq():
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": "ping"}]
            },
            timeout=5
        )
        return jsonify({"groq": "ok", "status_code": r.status_code})
    except Exception as e:
        return jsonify({"groq": "fail", "error": str(e)}), 500

@app.route("/status/memory")
def status_memory():
    try:
        exists = os.path.exists("hud_limits.db")
        size = os.path.getsize("hud_limits.db") if exists else 0
        return jsonify({
            "memory": "ok" if exists else "missing",
            "file_exists": exists,
            "file_size": size
        })
    except Exception as e:
        return jsonify({"memory": "fail", "error": str(e)}), 500

# -----------------------------
# ADMIN API
# -----------------------------
@app.route("/api/logs")
def get_logs():
    return jsonify(REQUEST_LOG)

@app.route("/api/rate")
def rate_status():
    used = get_used_today()
    remaining = 30 - used
    return jsonify({
        "used": used,
        "remaining": remaining,
        "limit": 30
    })

# -----------------------------
# ERROR HANDLERS
# -----------------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal Server Error"}), 500

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
