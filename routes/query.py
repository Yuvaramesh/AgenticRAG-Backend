from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from rag.graph import run_graph # Assuming run_graph is the function in graph.py
from models.types import ChatState, ChatMessage # Import ChatState and ChatMessage
from datetime import datetime

query_bp = Blueprint("query", __name__)

@query_bp.route("/query", methods=["POST"])
@cross_origin(origins=["http://localhost:3000"])
def handle_query():
    data = request.get_json()
    user_query = data.get("query")
    # Ensure chat_history is a list of ChatMessage objects
    raw_chat_history = data.get("chat_history", [])
    chat_history = [ChatMessage(**msg) for msg in raw_chat_history] # Convert raw dicts to ChatMessage objects
    
    selected_file = data.get("selected_file")
    agent_type = data.get("agent_type")
    user_email = request.headers.get('X-User-Email')
    image_path = data.get("image_path")

    if not user_query:
        return jsonify({"error": "Bad Request", "message": "Query is required"}), 400

    chat_state: ChatState = {
        "query": user_query,
        "selected_file": selected_file,
        "context_chunks": [], # This will be populated by the RAG graph
        "agent_type": agent_type,
        "answer": None, # This will be populated by the RAG graph
        "user_email": user_email,
        "chat_history": chat_history,
        "image_path": image_path
    }

    try:
        # Assuming run_graph takes ChatState as an argument and returns a dict
        result = run_graph(chat_state)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
