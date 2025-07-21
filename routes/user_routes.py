from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from models.types import doc_to_dict
from auth_decorators import role_required
from db.mongo import mongo_db
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash
from datetime import datetime

user_bp = Blueprint("user", __name__)

@user_bp.route("/users", methods=["GET"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["admin"])
def get_users(current_user):
    users = []
    for user_doc in mongo_db.users.find():
        user_dict = doc_to_dict(user_doc)
        # Remove password from response
        user_dict.pop('password', None)
        users.append(user_dict)
    return jsonify(users)

@user_bp.route("/users", methods=["POST"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["admin"])
def create_user(current_user):
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not all([name, email, password, role]):
        return jsonify({"error": "Bad Request", "message": "All fields are required"}), 400

    if role not in ["admin", "teacher", "student"]:
        return jsonify({"error": "Bad Request", "message": "Invalid role"}), 400

    # Check if user already exists
    existing_user = mongo_db.users.find_one({"email": email})
    if existing_user:
        return jsonify({"error": "Conflict", "message": "User with this email already exists"}), 409

    new_user_data = {
        "name": name,
        "email": email,
        "password": generate_password_hash(password),
        "role": role,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = mongo_db.users.insert_one(new_user_data)
    new_user_data['id'] = str(result.inserted_id)
    new_user_data.pop('password', None)  # Remove password from response
    
    return jsonify(new_user_data), 201

@user_bp.route("/users/<user_id>", methods=["PUT"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["admin"])
def update_user(current_user, user_id):
    try:
        user_obj_id = ObjectId(user_id)
    except Exception:
        return jsonify({"error": "Bad Request", "message": "Invalid User ID format"}), 400

    user_doc = mongo_db.users.find_one({"_id": user_obj_id})
    if not user_doc:
        return jsonify({"error": "Not Found", "message": "User not found"}), 404

    data = request.get_json()
    update_data = {
        "name": data.get("name", user_doc["name"]),
        "email": data.get("email", user_doc["email"]),
        "role": data.get("role", user_doc["role"]),
        "updated_at": datetime.utcnow()
    }

    # Update password if provided
    if data.get("password"):
        update_data["password"] = generate_password_hash(data["password"])

    mongo_db.users.update_one({"_id": user_obj_id}, {"$set": update_data})
    updated_user_doc = mongo_db.users.find_one({"_id": user_obj_id})
    updated_user_dict = doc_to_dict(updated_user_doc)
    updated_user_dict.pop('password', None)  # Remove password from response
    
    return jsonify(updated_user_dict)

@user_bp.route("/users/<user_id>", methods=["DELETE"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["admin"])
def delete_user(current_user, user_id):
    try:
        user_obj_id = ObjectId(user_id)
    except Exception:
        return jsonify({"error": "Bad Request", "message": "Invalid User ID format"}), 400

    user_doc = mongo_db.users.find_one({"_id": user_obj_id})
    if not user_doc:
        return jsonify({"error": "Not Found", "message": "User not found"}), 404

    mongo_db.users.delete_one({"_id": user_obj_id})
    return jsonify({"message": "User deleted successfully"}), 200
