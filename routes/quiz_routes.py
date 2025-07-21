from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from models.types import doc_to_dict
from auth_decorators import role_required
from db.mongo import mongo_db
from bson.objectid import ObjectId
import json
from datetime import datetime

quiz_bp = Blueprint("quiz", __name__)

@quiz_bp.route("/quizzes", methods=["GET"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["admin", "teacher", "student"])
def get_quizzes(current_user):
    quizzes = []
    if current_user['role'] == "admin":
        for quiz_doc in mongo_db.quizzes.find():
            quizzes.append(doc_to_dict(quiz_doc))
    elif current_user['role'] == "teacher":
        teacher_sections = mongo_db.sections.find({"teacher_id": current_user['id']})
        section_obj_ids = [ObjectId(s['_id']) for s in teacher_sections]
        # Include quizzes with no section_id for teachers
        for quiz_doc in mongo_db.quizzes.find({"$or": [{"section_id": {"$in": section_obj_ids}}, {"section_id": None}]}):
            quizzes.append(doc_to_dict(quiz_doc))
    elif current_user['role'] == "student":
        # Students only see enabled quizzes
        for quiz_doc in mongo_db.quizzes.find({"is_enabled": True}):
            quiz_dict = doc_to_dict(quiz_doc)
            # Remove correct answers for students
            if quiz_dict.get('questions'):
                for question in quiz_dict['questions']:
                    question.pop('correct_answer', None)
            quizzes.append(quiz_dict)
    
    return jsonify(quizzes)

@quiz_bp.route("/quizzes", methods=["POST"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["admin", "teacher"])
def create_quiz(current_user):
    data = request.get_json()
    title = data.get("title")
    section_id = data.get("section_id") # This can now be None or empty string
    questions = data.get("questions", [])

    if not title: # Only title is strictly required now
        return jsonify({"error": "Bad Request", "message": "Title is required"}), 400

    section_obj_id = None
    if section_id: # Only convert to ObjectId if section_id is provided
        try:
            section_obj_id = ObjectId(section_id)
        except Exception:
            return jsonify({"error": "Bad Request", "message": "Invalid Section ID format"}), 400

    new_quiz_data = {
        "title": title,
        "description": data.get("description", ""),
        "section_id": section_obj_id, # Store as ObjectId or None
        "created_by": ObjectId(current_user['id']),
        "questions": questions,
        "is_enabled": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = mongo_db.quizzes.insert_one(new_quiz_data)
    
    # Convert the inserted document to a dictionary with string IDs before jsonify
    created_quiz_doc = mongo_db.quizzes.find_one({"id": result.inserted_id})
    return jsonify(doc_to_dict(created_quiz_doc)), 201

@quiz_bp.route("/quizzes", methods=["GET"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["admin", "teacher", "student"])
def get_quiz():
    
    quiz_doc = mongo_db.quizzes.find_many({"is_enabled": True})
    if not quiz_doc:
        return jsonify({"error": "Not Found", "message": "Quiz not found"}), 404

    quiz_dict = doc_to_dict(quiz_doc)

    return jsonify(quiz_dict)

@quiz_bp.route("/quizzes/<quiz_id>", methods=["PUT"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["admin", "teacher"])
def update_quiz(current_user, quiz_id):
    try:
        quiz_obj_id = ObjectId(quiz_id)
    except Exception:
        return jsonify({"error": "Bad Request", "message": "Invalid Quiz ID format"}), 400

    quiz_doc = mongo_db.quizzes.find_one({"id": quiz_obj_id})
    if not quiz_doc:
        return jsonify({"error": "Not Found", "message": "Quiz not found"}), 404

    data = request.get_json()
    
    # Handle section_id update - allow setting to None
    updated_section_id = data.get("section_id")
    if updated_section_id == "": # If frontend sends empty string for optional field
        updated_section_id = None
    elif updated_section_id is not None:
        try:
            updated_section_id = ObjectId(updated_section_id)
        except Exception:
            return jsonify({"error": "Bad Request", "message": "Invalid Section ID format for update"}), 400

    updated_data = {
        "title": data.get("title", quiz_doc["title"]),
        "description": data.get("description", quiz_doc.get("description", "")),
        "questions": data.get("questions", quiz_doc.get("questions", [])),
        "section_id": updated_section_id if updated_section_id is not None else quiz_doc.get("section_id", None), # Update section_id
        "updated_at": datetime.utcnow()
    }

    mongo_db.quizzes.update_one({"id": quiz_obj_id}, {"$set": updated_data})
    updated_quiz_doc = mongo_db.quizzes.find_one({"id": quiz_obj_id})
    
    return jsonify(doc_to_dict(updated_quiz_doc))

@quiz_bp.route("/quizzes/<quiz_id>/enable", methods=["POST"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["admin", "teacher"])
def enable_quiz(current_user, quiz_id):
    try:
        quiz_obj_id = ObjectId(quiz_id)
    except Exception:
        return jsonify({"error": "Bad Request", "message": "Invalid Quiz ID format"}), 400

    quiz_doc = mongo_db.quizzes.find_one({"_id": quiz_obj_id})
    if not quiz_doc:
        return jsonify({"error": "Not Found", "message": "Quiz not found"}), 404

    mongo_db.quizzes.update_one({"_id": quiz_obj_id}, {"$set": {"is_enabled": True, "updated_at": datetime.utcnow()}})
    updated_quiz_doc = mongo_db.quizzes.find_one({"_id": quiz_obj_id})
    
    return jsonify(doc_to_dict(updated_quiz_doc))

@quiz_bp.route("/quizzes/<quiz_id>/disable", methods=["POST"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["admin", "teacher"])
def disable_quiz(current_user, quiz_id):
    try:
        quiz_obj_id = ObjectId(quiz_id)
    except Exception:
        return jsonify({"error": "Bad Request", "message": "Invalid Quiz ID format"}), 400

    quiz_doc = mongo_db.quizzes.find_one({"id": quiz_obj_id})
    if not quiz_doc:
        return jsonify({"error": "Not Found", "message": "Quiz not found"}), 404

    mongo_db.quizzes.update_one({"id": quiz_obj_id}, {"$set": {"is_enabled": False, "updated_at": datetime.utcnow()}})
    updated_quiz_doc = mongo_db.quizzes.find_one({"id": quiz_obj_id})
    
    return jsonify(doc_to_dict(updated_quiz_doc))
