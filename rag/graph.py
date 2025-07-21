from langgraph.graph.state import StateGraph, START, END
from models.types import ChatState
from rag.nodes import (
    extract_context_node, classify_agent_node, 
    build_response_node, update_history_node, route_agent
)

graph_builder = StateGraph(ChatState)
graph_builder.add_node("extract_context", extract_context_node)
graph_builder.add_node("classify_agent", classify_agent_node)
graph_builder.add_node("technical_agent", build_response_node("technical"))
graph_builder.add_node("customer_agent", build_response_node("customer"))
graph_builder.add_node("common_agent", build_response_node("general"))
graph_builder.add_node("update_history", update_history_node)

graph_builder.add_edge(START, "extract_context")
graph_builder.add_edge("extract_context", "classify_agent")
graph_builder.add_conditional_edges("classify_agent", route_agent)
graph_builder.add_edge("technical_agent", "update_history")
graph_builder.add_edge("customer_agent", "update_history")
graph_builder.add_edge("common_agent", "update_history")
graph_builder.add_edge("update_history", END)

graph = graph_builder.compile()

from models.types import ChatState, ChatMessage # Import ChatState and ChatMessage
# Assuming 'graph' is an object or function that needs to be defined here
# For demonstration, let's define a placeholder run_graph function
# You will replace this with your actual RAG graph implementation.

def run_graph(chat_state: ChatState):
    """
    Placeholder for your RAG graph logic.
    Processes the chat_state and returns a result.
    """
    query = chat_state['query']
    chat_history = chat_state['chat_history'] # This will now be List[ChatMessage]
    user_email = chat_state['user_email']
    selected_file = chat_state['selected_file']

    # Example: Simple echo or mock RAG response
    print(f"Processing query: {query} for user: {user_email}")
    print(f"Chat history length: {len(chat_history)}")
    
    # In a real RAG system, you would:
    # 1. Retrieve context based on query and selected_file
    # 2. Use an LLM to generate an answer based on query, context, and chat_history
    # 3. Update chat_state with the answer and context_chunks

    mock_answer = f"Hello {user_email}, I received your query: '{query}'. This is a mock response from the RAG graph."
    mock_context_chunks = ["Context chunk 1 from file.", "Context chunk 2 related to query."]

    # Update the chat_state with the answer and context chunks
    chat_state['answer'] = mock_answer
    chat_state['context_chunks'] = mock_context_chunks

    return {
        "answer": chat_state['answer'],
        "context_chunks": chat_state['context_chunks'],
        "chat_history": [msg.dict() for msg in chat_state['chat_history']] # Convert ChatMessage back to dict for jsonify
    }

# If your graph is an object, you might have something like:
# class RAGGraph:
#     def __init__(self):
#         # Initialize RAG components
#         pass
#     def run(self, chat_state: ChatState):
#         # RAG logic here
#         return {"answer": "...", "context_chunks": [...]}
# graph = RAGGraph() # Instantiate your graph object if needed
