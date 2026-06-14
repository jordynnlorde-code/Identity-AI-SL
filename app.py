import os
from flask import Flask, jsonify, render_template
from flask_cors import CORS

from identity_routes import identity_bp
from relay_routes import relay_bp
from memory_routes import memory_bp
from hud_routes import hud

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Register API blueprints
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
# JSON STATUS
# -----------------------------

@app.route("/status")
def status():
    return jsonify({"status": "running"})

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
