from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from rag.graph import graph

query_bp = Blueprint("query", __name__)

@query_bp.route('/query', methods=['POST'])
@cross_origin(origins=["http://localhost:3000"])
def query():
    data = request.get_json()
    query = data.get("query")
    selected_file = data.get("selectedFile")
    history = data.get("chat_history", [])
    user_email = data.get("user_email", "anonymous")

    if not query:
        return jsonify({"error": "Missing query"}), 400

    initial_state = {
        "query": query,
        "chat_history": history,
        "selected_file": selected_file,
        "user_email": user_email,
    }

    try:
        result = graph.invoke(initial_state)
        return jsonify({
            "answer": result.get("answer", ""),
            "agent_type": result.get("agent_type", ""),
            "chat_history": result.get("chat_history", [])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
