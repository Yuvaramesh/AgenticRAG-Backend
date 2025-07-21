from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from models.types import doc_to_dict
from auth_decorators import role_required
from db.mongo import mongo_db
from bson.objectid import ObjectId
from datetime import datetime

quiz_attempt_bp = Blueprint("quiz_attempt", __name__)

@quiz_attempt_bp.route("/quiz_attempts", methods=["GET"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["admin", "teacher", "student"])
def get_quiz_attempts(current_user):
    attempts = []
    if current_user['role'] == "admin":
        for attempt_doc in mongo_db.quiz_attempts.find():
            attempts.append(doc_to_dict(attempt_doc))
    elif current_user['role'] == "teacher":
        # Teachers see attempts for quizzes in their sections
        teacher_sections = mongo_db.sections.find({"teacher_id": current_user['id']})
        section_obj_ids = [ObjectId(s['_id']) for s in teacher_sections]
        quizzes_in_sections = mongo_db.quizzes.find({"section_id": {"$in": section_obj_ids}})
        quiz_obj_ids = [ObjectId(q['_id']) for q in quizzes_in_sections]
        for attempt_doc in mongo_db.quiz_attempts.find({"quiz_id": {"$in": quiz_obj_ids}}):
            attempts.append(doc_to_dict(attempt_doc))
    elif current_user['role'] == "student":
        # Students only see their own attempts
        for attempt_doc in mongo_db.quiz_attempts.find({"student_id": ObjectId(current_user['id'])}):
            attempts.append(doc_to_dict(attempt_doc))
    
    return jsonify(attempts)

@quiz_attempt_bp.route("/quiz_attempts", methods=["POST"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["student"])
def submit_quiz_attempt(current_user):
    data = request.get_json()
    quiz_id = data.get("quiz_id")
    answers = data.get("answers", {})

    if not quiz_id:
        return jsonify({"error": "Bad Request", "message": "Quiz ID is required"}), 400

    try:
        quiz_obj_id = ObjectId(quiz_id)
    except Exception:
        return jsonify({"error": "Bad Request", "message": "Invalid Quiz ID format"}), 400

    # Get the quiz with correct answers
    quiz_doc = mongo_db.quizzes.find_one({"_id": quiz_obj_id})
    if not quiz_doc:
        return jsonify({"error": "Not Found", "message": "Quiz not found"}), 404

    if not quiz_doc.get("is_enabled", False):
        return jsonify({"error": "Forbidden", "message": "Quiz is not available"}), 403

    # Calculate score
    score = 0
    total_questions = len(quiz_doc.get("questions", []))
    
    for i, question in enumerate(quiz_doc.get("questions", [])):
        student_answer = answers.get(str(i))
        correct_answer = question.get("correct_answer")
        if student_answer == correct_answer:
            score += 1

    # Save the attempt
    attempt_data = {
        "student_id": ObjectId(current_user['id']),
        "quiz_id": quiz_obj_id,
        "score": score,
        "total_questions": total_questions,
        "answers": answers,
        "attempt_date": datetime.utcnow(),
        "time_taken": data.get("time_taken", 0)
    }
    
    result = mongo_db.quiz_attempts.insert_one(attempt_data)
    attempt_data['id'] = str(result.inserted_id)
    
    return jsonify({
        "id": attempt_data['id'],
        "score": score,
        "total_questions": total_questions,
        "percentage": round((score / total_questions) * 100, 1) if total_questions > 0 else 0
    }), 201

@quiz_attempt_bp.route("/quiz_attempts/<attempt_id>", methods=["GET"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["admin", "teacher", "student"])
def get_quiz_attempt(current_user, attempt_id):
    try:
        attempt_obj_id = ObjectId(attempt_id)
    except Exception:
        return jsonify({"error": "Bad Request", "message": "Invalid Attempt ID format"}), 400

    attempt_doc = mongo_db.quiz_attempts.find_one({"_id": attempt_obj_id})
    if not attempt_doc:
        return jsonify({"error": "Not Found", "message": "Quiz attempt not found"}), 404

    # Check permissions
    if current_user['role'] == "student" and str(attempt_doc['student_id']) != current_user['id']:
        return jsonify({"error": "Forbidden", "message": "Access denied"}), 403
    elif current_user['role'] == "teacher":
        # Check if the quiz belongs to teacher's section
        quiz_doc = mongo_db.quizzes.find_one({"_id": attempt_doc['quiz_id']})
        if quiz_doc:
            section_doc = mongo_db.sections.find_one({"_id": quiz_doc['section_id']})
            if not section_doc or str(section_doc['teacher_id']) != current_user['id']:
                return jsonify({"error": "Forbidden", "message": "Access denied"}), 403

    return jsonify(doc_to_dict(attempt_doc))
