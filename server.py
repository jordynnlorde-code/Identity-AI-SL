import os
import requests

from flask import Flask, jsonify, render_template
from flask_cors import CORS

from identity_routes import identity_bp
from relay_routes import relay_bp
from memory_routes import memory_bp
from hud_routes import hud

from logger import REQUEST_LOG
from hud_rate_limit import get_used_today

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

CORS(app)

# --------------------------------------------------
# REGISTER BLUEPRINTS
# --------------------------------------------------

app.register_blueprint(identity_bp)
app.register_blueprint(relay_bp)
app.register_blueprint(memory_bp)
app.register_blueprint(hud)

# --------------------------------------------------
# WEB PAGES
# --------------------------------------------------

@app.route("/")
def homepage():
    return render_template("index.html")


@app.route("/status/html")
def status_html():
    return render_template("status.html")


@app.route("/admin")
def admin_dashboard():
    return render_template("admin.html")


# --------------------------------------------------
# HEALTH
# --------------------------------------------------

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })


# --------------------------------------------------
# STATUS ENDPOINTS
# --------------------------------------------------

@app.route("/status")
def status():
    return jsonify({
        "status": "running"
    })


@app.route("/status/groq")
def status_groq():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return jsonify({
            "groq": "fail",
            "error": "GROQ_API_KEY not configured"
        }), 500

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "user",
                        "content": "ping"
                    }
                ]
            },
            timeout=5
        )

        if response.status_code == 200:
            return jsonify({
                "groq": "ok"
            })

        return jsonify({
            "groq": "fail",
            "status_code": response.status_code
        }), 500

    except Exception as e:
        return jsonify({
            "groq": "fail",
            "error": str(e)
        }), 500


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


# --------------------------------------------------
# ADMIN API
# --------------------------------------------------

@app.route("/api/logs")
def get_logs():
    return jsonify(REQUEST_LOG)


@app.route("/api/rate")
def rate_status():
    return jsonify({
        "used_today": get_used_today()
    })


# --------------------------------------------------
# ERROR HANDLERS
# --------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Not Found"
    }), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({
        "error": "Internal Server Error"
    }), 500


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )