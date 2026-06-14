import os
import sqlite3
import requests
from flask import Flask, jsonify, render_template
from flask_cors import CORS

from identity_routes import identity_bp
from relay_routes import relay_bp
from memory_routes import memory_bp
from hud_routes import hud

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# -----------------------------
# REGISTER API BLUEPRINTS
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

# -----------------------------
# JSON STATUS (BASE)
# -----------------------------
@app.route("/status")
def status():
    return jsonify({"status": "running"})

# -----------------------------
# GROQ STATUS CHECK
# -----------------------------
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
        return jsonify({
            "groq": "ok",
            "status_code": r.status_code
        })
    except Exception as e:
        return jsonify({
            "groq": "fail",
            "error": str(e)
        }), 500

# -----------------------------
# MEMORY FILE STATUS CHECK
# -----------------------------
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
        return jsonify({
            "memory": "fail",
            "error": str(e)
        }), 500

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
