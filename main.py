import os
import json
from typing import Annotated, TypedDict, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy import create_all, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# LangChain/LangGraph/Groq imports
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode

# --- FASTAPI APP INITIALIZATION ---
app = FastAPI()

# --- CORS MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATABASE SETUP ---
DATABASE_URL = os.getenv("DATABASE_URL")
f DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base() 

class HCPInteraction(Base):
    __tablename__ = "hcp_interactions"
    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(100))
    interaction_type = Column(String(50))
    summary = Column(Text)
    sentiment = Column(String(20))
    next_step = Column(String(200))
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# --- TOOLS DEFINITION ---

@tool
def log_interaction(hcp_name: str, summary: str, sentiment: str, next_step: str):
    """Log a new interaction with an HCP. Use this when the user describes a meeting."""
    db = SessionLocal()
    try:
        new_entry = HCPInteraction(
            hcp_name=hcp_name, 
            summary=summary, 
            sentiment=sentiment, 
            next_step=next_step,
            interaction_type="In-Person" 
        )
        db.add(new_entry)
        db.commit()
        return f"Successfully logged interaction for {hcp_name}."
    except Exception as e:
        return f"Error logging interaction: {str(e)}"
    finally:
        db.close()

@tool
def edit_interaction(interaction_id: int, new_summary: str):
    """Update an existing interaction's summary. interaction_id MUST be an integer."""
    db = SessionLocal()
    try:
        target_id = int(interaction_id) 
        record = db.query(HCPInteraction).filter(HCPInteraction.id == target_id).first()
        if record:
            record.summary = new_summary
            db.commit()
            return f"Successfully updated record {target_id}."
        return f"Record with ID {target_id} not found."
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        db.close()

@tool
def hcp_search(name_query: str):
    """Search for existing HCP records."""
    db = SessionLocal()
    results = db.query(HCPInteraction).filter(HCPInteraction.hcp_name.contains(name_query)).all()
    db.close()
    return [r.hcp_name for r in results] if results else "No HCPs found."

@tool
def analyze_sentiment(text: str):
    """Analyze if the doctor's tone was Positive, Neutral, or Concerned."""
    t = text.lower()
    if any(word in t for word in ["interested", "happy", "great", "good"]):
        return "Positive"
    elif any(word in t for word in ["concern", "issue", "bad", "unhappy"]):
        return "Concerned"
    return "Neutral"

@tool
def generate_followup(context: str):
    """Generate a specific follow-up task summary."""
    return f"Follow-up: Schedule meeting regarding {context[:30]}"

# --- LANGGRAPH AGENT SETUP ---

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=GROQ_API_KEY, temperature=0)
tools = [log_interaction, edit_interaction, hcp_search, analyze_sentiment, generate_followup]
llm_with_tools = llm.bind_tools(tools)

def call_model(state: AgentState):
    sys_msg = SystemMessage(content=(
        "You are an expert CRM assistant for Life Sciences. Use tools to log or search HCP interactions. "
        "When logging, always provide hcp_name, summary, sentiment, and next_step. "
        "IMPORTANT: Always call 'log_interaction' when a user describes a new meeting."
    ))
    messages = [sys_msg] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))
workflow.add_edge(START, "agent")

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    return "tools" if last_message.tool_calls else END

workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")
graph = workflow.compile()

# --- FASTAPI ENDPOINT ---

class ChatInput(BaseModel):
    message: str

@app.post("/chat")
async def chat(input_data: ChatInput):
    inputs = {"messages": [HumanMessage(content=input_data.message)]}
    result = graph.invoke(inputs)
    
    structured_data = {}
    
    # Extracting tool arguments to fill the React form
    for msg in result["messages"]:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tool_call in msg.tool_calls:
                if tool_call['name'] == 'log_interaction':
                    args = tool_call['args']
                    structured_data = {
                        "hcp_name": args.get("hcp_name", ""),
                        "interaction_type": "In-Person",
                        "summary": args.get("summary", ""),
                        "sentiment": args.get("sentiment", ""),
                        "next_step": args.get("next_step", "")
                    }
    
    final_response = result["messages"][-1].content
    if not final_response:
        for msg in reversed(result["messages"]):
            if msg.content:
                final_response = msg.content
                break

    return {
        "response": final_response or "Action completed.",
        "data": structured_data
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)