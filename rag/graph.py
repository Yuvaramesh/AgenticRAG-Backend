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
