from flask import Blueprint, request, jsonify
from groq_client import groq_chat
from hud_rate_limit import consume, get_remaining

hud = Blueprint("hud", __name__)

@hud.route("/api/hud", methods=["POST"])
def hud_chat():
    data = request.json or {}
    avatar_id = data.get("avatar_id")
    message = data.get("message")

    if not avatar_id or not message:
        return jsonify({"error": "avatar_id and message required"}), 400

    allowed, remaining = consume(avatar_id)
    if not allowed:
        return jsonify({
            "error": "Daily limit reached",
            "remaining": 0,
            "limit": 30
        }), 429

    try:
        reply = groq_chat(message)
    except Exception as e:
        return jsonify({"error": "Groq error", "details": str(e)}), 500

    return jsonify({
        "avatar_id": avatar_id,
        "reply": reply,
        "remaining": remaining,
        "limit": 30
    })

@hud.route("/api/hud/remaining", methods=["GET"])
def hud_remaining():
    avatar_id = request.args.get("avatar_id")
    if not avatar_id:
        return jsonify({"error": "avatar_id required"}), 400

    remaining = get_remaining(avatar_id)
    return jsonify({
        "avatar_id": avatar_id,
        "remaining": remaining,
        "limit": 30
    })
