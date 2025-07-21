from flask import Blueprint, jsonify, request
from db.mongo import sections_collection
from models.types import Section
from auth_decorators import role_required
from bson.objectid import ObjectId
from datetime import datetime

section_bp = Blueprint('sections', __name__)

@section_bp.route('/sections', methods=['GET'])
@role_required(['admin', 'teacher','student'])
def get_sections(*args, **kwargs):
    """Retrieve all sections (Admin/Teacher only)."""
    try:
        sections = list(sections_collection.find({}))
        for section in sections:
            section['_id'] = str(section['_id'])
        return jsonify(sections), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@section_bp.route('/sections/<string:section_id>', methods=['GET'])
@role_required(['admin', 'teacher'])
def get_section(section_id):
    """Retrieve a single section by ID (Admin/Teacher only)."""
    try:
        section = sections_collection.find_one({"_id": ObjectId(section_id)})
        if section:
            section['_id'] = str(section['_id'])
            return jsonify(section), 200
        return jsonify({"message": "Section not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@section_bp.route('/sections', methods=['POST'])
@role_required(['admin', 'teacher'])
def create_section():
    """Create a new section (Admin/Teacher only)."""
    data = request.get_json()
    try:
        new_section_data = Section(
            name=data['name'],
            description=data.get('description'),
            teacher_id=data['teacher_id'] # Ensure this teacher_id exists in users collection
        )
        result = sections_collection.insert_one(new_section_data.model_dump(by_alias=True, exclude_none=True))
        new_section_data._id = str(result.inserted_id)
        return jsonify(new_section_data.model_dump(by_alias=True)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@section_bp.route('/sections/<string:section_id>', methods=['PUT'])
@role_required(['admin', 'teacher'])
def update_section(section_id):
    """Update an existing section (Admin/Teacher only)."""
    data = request.get_json()
    try:
        update_data = {k: v for k, v in data.items() if k not in ['_id', 'id', 'created_at']}
        update_data['updated_at'] = datetime.utcnow()

        result = sections_collection.update_one(
            {"_id": ObjectId(section_id)},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            return jsonify({"message": "Section not found"}), 404
        
        updated_section = sections_collection.find_one({"_id": ObjectId(section_id)})
        updated_section['_id'] = str(updated_section['_id'])
        return jsonify(updated_section), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@section_bp.route('/sections/<string:section_id>', methods=['DELETE'])
@role_required(['admin', 'teacher'])
def delete_section(section_id):
    """Delete a section (Admin/Teacher only)."""
    try:
        result = sections_collection.delete_one({"_id": ObjectId(section_id)})
        if result.deleted_count == 1:
            return jsonify({"message": "Section deleted successfully"}), 200
        return jsonify({"message": "Section not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

