import os
from flask import Flask, jsonify
from flask_cors import CORS

from identity_routes import identity_bp
from relay_routes import relay_bp
from memory_routes import memory_bp
from hud_routes import hud  # NEW

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(identity_bp)
app.register_blueprint(relay_bp)
app.register_blueprint(memory_bp)
app.register_blueprint(hud)  # HUD now active

@app.route("/")
def root():
    return jsonify({
        "status": "ok",
        "service": "Identity-AI Backend",
        "hud": "/api/hud",
        "identity": "/api/identity",
        "relay": "/api/relay",
        "memory": "/api/memory"
    })

@app.route("/status")
def status():
    return jsonify({"status": "running"})

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
