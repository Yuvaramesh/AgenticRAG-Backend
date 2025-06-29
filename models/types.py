from typing import TypedDict, List, Optional

class ChatState(TypedDict):
    query: str
    selected_file: Optional[str]
    context_chunks: List[str]
    agent_type: Optional[str]
    answer: Optional[str]
    user_email: str
    chat_history: List[dict]
