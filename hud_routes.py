from flask import Blueprint, request, jsonify
from groq_client import groq_chat

hud = Blueprint("hud", __name__)

@hud.route("/api/hud", methods=["POST"])
def hud_chat():
    data = request.json or {}
    avatar_id = data.get("avatar_id")
    message = data.get("message")

    if not avatar_id or not message:
        return jsonify({"error": "avatar_id and message required"}), 400

    reply = groq_chat(message)

    return jsonify({
        "avatar_id": avatar_id,
        "reply": reply
    })
