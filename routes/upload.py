from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from rag.extract_text import extract_text
from rag.embedding import embed_and_store, embed_image_and_store
import os

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
            filename = file.filename
            extension = os.path.splitext(filename)[-1].lower()

            # Use in-memory file object (no need to save locally)
            file_stream = file.stream

            # Extract text directly from file stream
            content = extract_text(file_stream, filename)

            # Route image vs non-image embeddings
            if extension in [".png", ".jpg", ".jpeg"]:
                chunk_count = embed_image_and_store(filename, content)
            else:
                chunk_count = embed_and_store(filename, content)

            total_chunks += chunk_count

        except Exception as e:
            print(f"Error processing {file.filename}: {str(e)}")
            return jsonify({"error": f"{file.filename} failed: {str(e)}"}), 500

    return jsonify({"message": f"{total_chunks} chunks embedded from {len(files)} file(s)"}), 200
