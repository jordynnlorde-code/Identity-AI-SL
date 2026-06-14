from flask import Blueprint, request, jsonify
from groq_client import groq_chat

identity_bp = Blueprint("identity", __name__)

@identity_bp.route("/api/identity", methods=["POST"])
def identity_chat():
    data = request.json or {}
    message = data.get("message")

    if not message:
        return jsonify({"error": "message required"}), 400

    reply = groq_chat(message)
    return jsonify({"reply": reply})
