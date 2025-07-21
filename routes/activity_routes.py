from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from models.types import doc_to_dict
from auth_decorators import role_required
from db.mongo import mongo_db
from bson.objectid import ObjectId
import json
from datetime import datetime

activity_bp = Blueprint("activity", __name__)

@activity_bp.route("/activities", methods=["GET"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["admin", "teacher", "student"])
def get_activities(current_user):
    activities = []
    if current_user['role'] == "admin":
        for activity_doc in mongo_db.activities.find():
            activities.append(doc_to_dict(activity_doc))
    elif current_user['role'] == "teacher":
        # Teachers see activities in their sections
        teacher_sections = mongo_db.sections.find({"teacher_id": current_user['id']})
        section_obj_ids = [ObjectId(s['_id']) for s in teacher_sections]
        for activity_doc in mongo_db.activities.find({"section_id": {"$in": section_obj_ids}}):
            activities.append(doc_to_dict(activity_doc))
    elif current_user['role'] == "student":
        # Students only see published activities
        for activity_doc in mongo_db.activities.find({"is_published": True}):
            activities.append(doc_to_dict(activity_doc))
    
    return jsonify(activities)

@activity_bp.route("/activities", methods=["POST"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["admin", "teacher"])
def create_activity(current_user):
    data = request.get_json()
    title = data.get("title")
    section_id = data.get("section_id")
    activity_type = data.get("activity_type", "assignment")
    content = data.get("content", "")
    due_date = data.get("due_date")

    if not title or not section_id:
        return jsonify({"error": "Bad Request", "message": "Title and section_id are required"}), 400

    try:
        section_obj_id = ObjectId(section_id)
    except Exception:
        return jsonify({"error": "Bad Request", "message": "Invalid Section ID format"}), 400

    new_activity_data = {
        "title": title,
        "description": data.get("description", ""),
        "section_id": section_obj_id,
        "activity_type": activity_type,
        "content": content,
        "due_date": datetime.fromisoformat(due_date) if due_date else None,
        "is_published": False,
        "created_by": ObjectId(current_user['id']),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = mongo_db.activities.insert_one(new_activity_data)
    new_activity_data['id'] = str(result.inserted_id)
    
    return jsonify(new_activity_data), 201

@activity_bp.route("/activities/<activity_id>/publish", methods=["POST"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["admin", "teacher"])
def publish_activity(current_user, activity_id):
    try:
        activity_obj_id = ObjectId(activity_id)
    except Exception:
        return jsonify({"error": "Bad Request", "message": "Invalid Activity ID format"}), 400

    activity_doc = mongo_db.activities.find_one({"_id": activity_obj_id})
    if not activity_doc:
        return jsonify({"error": "Not Found", "message": "Activity not found"}), 404

    mongo_db.activities.update_one({"_id": activity_obj_id}, {"$set": {"is_published": True, "updated_at": datetime.utcnow()}})
    updated_activity_doc = mongo_db.activities.find_one({"_id": activity_obj_id})
    
    return jsonify(doc_to_dict(updated_activity_doc))

@activity_bp.route("/activities/<activity_id>/unpublish", methods=["POST"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["admin", "teacher"])
def unpublish_activity(current_user, activity_id):
    try:
        activity_obj_id = ObjectId(activity_id)
    except Exception:
        return jsonify({"error": "Bad Request", "message": "Invalid Activity ID format"}), 400

    activity_doc = mongo_db.activities.find_one({"_id": activity_obj_id})
    if not activity_doc:
        return jsonify({"error": "Not Found", "message": "Activity not found"}), 404

    mongo_db.activities.update_one({"_id": activity_obj_id}, {"$set": {"is_published": False, "updated_at": datetime.utcnow()}})
    updated_activity_doc = mongo_db.activities.find_one({"_id": activity_obj_id})
    
    return jsonify(doc_to_dict(updated_activity_doc))

@activity_bp.route("/activity_submissions", methods=["GET"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["admin", "teacher", "student"])
def get_activity_submissions(current_user):
    submissions = []
    if current_user['role'] == "admin":
        for submission_doc in mongo_db.activity_submissions.find():
            submissions.append(doc_to_dict(submission_doc))
    elif current_user['role'] == "teacher":
        # Teachers see submissions for activities in their sections
        teacher_sections = mongo_db.sections.find({"teacher_id": current_user['id']})
        section_obj_ids = [ObjectId(s['_id']) for s in teacher_sections]
        activities_in_sections = mongo_db.activities.find({"section_id": {"$in": section_obj_ids}})
        activity_obj_ids = [ObjectId(a['_id']) for a in activities_in_sections]
        for submission_doc in mongo_db.activity_submissions.find({"activity_id": {"$in": activity_obj_ids}}):
            submissions.append(doc_to_dict(submission_doc))
    elif current_user['role'] == "student":
        # Students only see their own submissions
        for submission_doc in mongo_db.activity_submissions.find({"student_id": ObjectId(current_user['id'])}):
            submissions.append(doc_to_dict(submission_doc))
    
    return jsonify(submissions)

@activity_bp.route("/publish-schedule", methods=["POST"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["admin", "teacher"])
def schedule_publish(current_user):
    data = request.get_json()
    
    schedule_data = {
        "quiz_id": ObjectId(data["quiz_id"]) if data.get("quiz_id") else None,
        "activity_id": ObjectId(data["activity_id"]) if data.get("activity_id") else None,
        "publish_date": datetime.fromisoformat(data["publish_date"]),
        "unpublish_date": datetime.fromisoformat(data["unpublish_date"]) if data.get("unpublish_date") else None,
        "target_sections": [ObjectId(section_id) for section_id in data.get("target_sections", [])],
        "created_by": ObjectId(current_user['id']),
        "created_at": datetime.utcnow(),
        "status": "scheduled"
    }
    
    result = mongo_db.publish_schedules.insert_one(schedule_data)
    schedule_data['id'] = str(result.inserted_id)
    
    return jsonify(schedule_data), 201
