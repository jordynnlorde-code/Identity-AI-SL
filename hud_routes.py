from flask import Blueprint, request, jsonify

from groq_client import groq_chat
from logger import log_request

hud = Blueprint("hud", __name__)


@hud.route("/api/hud", methods=["POST"])
def hud_chat():
    data = request.get_json(silent=True) or {}

    avatar_id = str(data.get("avatar_id", "")).strip()
    message = str(data.get("message", "")).strip()

    if not avatar_id:
        return jsonify({"error": "avatar_id required"}), 400

    if not message:
        return jsonify({"error": "message required"}), 400

    log_request({
        "avatar_id": avatar_id,
        "message": message[:200]
    })

    reply = groq_chat(message)

    return jsonify({
        "avatar_id": avatar_id,
        "reply": reply
    })