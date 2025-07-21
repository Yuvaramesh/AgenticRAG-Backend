from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from werkzeug.security import check_password_hash
from db.mongo import mongo_db
from models.types import doc_to_dict # Added for consistency, though not directly used in simple_login

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/simple-login", methods=["POST"])
@cross_origin(origins=["http://localhost:3000"])
def simple_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    # Find user in database
    user = mongo_db.users.find_one({"email": email})
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    # Check password
    if not check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid credentials"}), 401

    # Return user data without JWT token
    return jsonify({
        "id": str(user["_id"]),
        "email": user["email"],
        "name": user.get("name", ""),
        "role": user["role"]
    }), 200
