from flask import Blueprint, request, jsonify
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME
from sentence_transformers import SentenceTransformer

suggest_bp = Blueprint("suggest", __name__)
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
model = SentenceTransformer("all-MiniLM-L6-v2")

@suggest_bp.route("/suggest_words", methods=["POST"])
def suggest_words():
    data = request.json
    query_prefix = data.get("prefix", "")
    selected_file = data.get("selected_file", "")

    if not query_prefix or not selected_file:
        return jsonify({"suggestions": []})

    query_vector = model.encode(query_prefix).tolist()

    hits = client.search(
        collection_name=COLLECTION_NAME,  # use from config
        query_vector=query_vector,
        limit=5,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="source",  # ✅ updated from 'doc_name' to 'source'
                    match=MatchValue(value=selected_file)
                )
            ]
        )
    )

    suggestions = []
    for hit in hits:
        chunk_text = hit.payload.get("text", "")
        for word in chunk_text.split():
            if word.lower().startswith(query_prefix.lower()) and word not in suggestions:
                suggestions.append(word)
        if len(suggestions) >= 5:
            break

    return jsonify({"suggestions": suggestions[:5]})
