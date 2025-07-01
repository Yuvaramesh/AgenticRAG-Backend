from flask import Blueprint, jsonify
from flask_cors import cross_origin
from qdrant_client import QdrantClient
from config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME
from rag.utils import get_unique_filenames

documents_bp = Blueprint("documents", __name__)

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
@documents_bp.route('/uploaded_docx', methods=['GET'])
@cross_origin(origins=["http://localhost:3000"])
def uploaded_docx():
    try:
        results, _ = client.scroll(
            collection_name=COLLECTION_NAME,
            with_payload=True,
            limit=1000
        )

        documents = [
            point.payload["source"]
            for point in results
            if "source" in point.payload
        ]

        # Filter allowed file types
        allowed_ext = (".pdf", ".docx", ".txt", ".csv", ".png", ".jpg", ".jpeg")
        filtered_files = [
            doc for doc in documents if doc.lower().endswith(allowed_ext)
        ]

        # Remove duplicates
        unique_filenames = sorted(set(filtered_files))

        return jsonify({"uploaded_files": unique_filenames})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

