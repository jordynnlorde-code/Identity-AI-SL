from flask import Blueprint, request, jsonify

relay_bp = Blueprint("relay", __name__)

@relay_bp.route("/api/relay", methods=["POST"])
def relay():
    return jsonify({"received": request.json})
