from flask import Blueprint, request, jsonify

memory_bp = Blueprint("memory", __name__)

@memory_bp.route("/api/memory", methods=["POST"])
def memory():
    data = request.json or {}
    return jsonify({
        "status": "ok",
        "received": data
    })
