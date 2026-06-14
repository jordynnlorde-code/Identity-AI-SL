import os
import requests

from flask import Flask, jsonify, render_template
from flask_cors import CORS

from identity_routes import identity_bp
from relay_routes import relay_bp
from memory_routes import memory_bp
from hud_routes import hud

from logger import REQUEST_LOG

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

CORS(app)

# --------------------------------------------------
# Blueprints
# --------------------------------------------------

app.register_blueprint(identity_bp)
app.register_blueprint(relay_bp)
app.register_blueprint(memory_bp)
app.register_blueprint(hud)

# --------------------------------------------------
# Pages
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
# Status
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
            "groq": "missing_api_key"
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
            timeout=10
        )

        return jsonify({
            "groq": "ok",
            "status_code": response.status_code
        })

    except Exception as e:
        return jsonify({
            "groq": "fail",
            "error": str(e)
        }), 500


@app.route("/status/memory")
def status_memory():
    return jsonify({
        "memory": "disabled",
        "rate_limits": "disabled",
        "quotas": "unlimited"
    })


# --------------------------------------------------
# Admin
# --------------------------------------------------

@app.route("/api/logs")
def get_logs():
    return jsonify(REQUEST_LOG)


@app.route("/api/rate")
def rate_status():
    return jsonify({
        "used": "unlimited",
        "remaining": "unlimited",
        "limit": "unlimited"
    })


# --------------------------------------------------
# Errors
# --------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal Server Error"
    }), 500


# --------------------------------------------------
# Local Dev
# --------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )