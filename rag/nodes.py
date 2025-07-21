from config import GEMINI_API_KEY, COLLECTION_NAME
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import google.generativeai as genai
from rag.utils import clean_markdown
from db.mongo import chat_collection

genai.configure(api_key=GEMINI_API_KEY)

client = QdrantClient(url="https://2ed85abb-e606-4167-8d2e-ce4185f33997.us-east4-0.gcp.cloud.qdrant.io", 
                      api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.UYr-iYmbfZzhyr-lGQBlMlMuYQIAxriQhZd6af7vLq4")

EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

def extract_context_node(state: dict) -> dict:
    query_vector = EMBED_MODEL.encode(state["query"]).tolist()

    filter_condition = None
    if state.get("selected_file"):
        filter_condition = {
            "must": [
                {
                    "key": "source",
                    "match": {"value": state["selected_file"]}
                }
            ]
        }

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=3,
        with_payload=True,
        query_filter=filter_condition
    )

    return {
        "context_chunks": [res.payload["text"] for res in results]
    }


def classify_agent_node(state: dict) -> dict:
    context = "\n".join(state.get("context_chunks", []))
    prompt = f"""
You are a routing agent responsible for determining the appropriate agent to handle the user query and how the selected agent should respond.

Agent types: technical, customer, common

Rules:
- technical: engineering-related queries
- customer: support/product/service queries
- common: general queries

Return only one: technical, customer, or common.

Query: {state['query']}

Context:
{context}
"""

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return {"agent_type": response.text.strip().lower()}


def build_response_node(role: str):
    def node(state: dict) -> dict:
        context = "\n".join(state.get("context_chunks", []))
        prompt = f"""
You are a helpful {role} agent. Respond only using the context.

Ensure formatting:
- No **bold**, *italic*, or bullet points
- Use paragraphs only

Query:
{state['query']}

Context:
{context}
"""
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        cleaned_response = clean_markdown(response.text.strip())
        return {"answer": cleaned_response}
    return node


def update_history_node(state: dict) -> dict:
    history = state.get("chat_history", [])
    chat_entry = {
        "question": state["query"],
        "answer": state.get("answer", ""),
        "selected_file": state.get("selected_file", ""),
        "agent": state.get("agent_type", "common"),
        "user_email": state.get("user_email", "anonymous"),
    }

    try:
        inserted = chat_collection.insert_one(chat_entry)
        chat_entry["id"] = str(inserted.inserted_id)
    except Exception as e:
        print(f"[MongoDB Error] Failed to insert chat: {e}")

    history.append(chat_entry)
    return {"chat_history": history}


def route_agent(state: dict) -> str:
    return {
        "technical": "technical_agent",
        "customer": "customer_agent",
    }.get(state.get("agent_type", ""), "common_agent")
