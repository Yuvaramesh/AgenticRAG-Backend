from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from rag.extract_text import extract_text
from rag.embedding import embed_and_store

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
@cross_origin(origin="http://localhost:3000")
def upload():
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "No files provided"}), 400

    total_chunks = 0
    for file in files:
        try:
            content = extract_text(file.stream, file.filename)
            chunk_count = embed_and_store(file.filename, content)
            total_chunks += chunk_count
        except Exception as e:
            return jsonify({"error": f"{file.filename} failed: {str(e)}"}), 500

    return jsonify({"message": f"{total_chunks} chunks embedded from {len(files)} file(s)"}), 200
