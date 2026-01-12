from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForCausalLM
import torch
import os
from typing import Optional, List, Dict
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
import uuid
import sqlite3
from contextlib import contextmanager

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Database setup for chat history
DB_PATH = "chat_history.db"

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_database():
    """Initialize the database with chat history table"""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                assistant_message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Create indexes for better performance
        try:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON chat_history(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON chat_history(created_at)")
        except:
            pass  # Indexes might already exist

# Summarization model
MODEL_NAME = "google/bigbird-pegasus-large-pubmed"

model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME, cache_dir="./models/bigbird_pubmed"
)

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME, cache_dir="./models/bigbird_pubmed"
)

# Google Gemini Configuration for Medical Chatbot
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", None)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")  # Options: models/gemini-2.5-flash, models/gemini-2.5-pro, models/gemini-flash-latest

# Initialize Gemini client
gemini_model = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel(GEMINI_MODEL)

# Medical Chatbot System Prompt - Focused on Health & Medical
MEDICAL_SYSTEM_PROMPT = """You are a specialized medical and health assistant chatbot. Your expertise is focused exclusively on health, medical conditions, symptoms, and wellness.

Your role:
- Provide brief, concise medical and health information
- Focus specifically on health-related questions and symptoms
- Give short, direct answers (2-4 sentences maximum)
- Suggest possible health conditions based on symptoms
- Provide quick health advice and recommendations

Guidelines:
- Keep responses SHORT and CONCISE - maximum 2-4 sentences
- Focus ONLY on medical and health topics
- Use simple, clear medical language
- Always emphasize this is NOT a medical diagnosis
- Recommend consulting a doctor for proper diagnosis
- For emergencies, advise immediate medical attention

Important: Always end with a brief disclaimer: "This is informational only, not medical advice. Consult a healthcare provider."

If asked about non-medical topics, politely redirect to health/medical questions only."""


class SummarizeRequest(BaseModel):
    text: str


@app.post("/summarize")
def summarize(req: SummarizeRequest):
    text = req.text

    if not text.strip():
        raise HTTPException(status_code=400, detail="Text is empty")

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=4096)

    with torch.no_grad():
        output = model.generate(
            **inputs, max_new_tokens=180, num_beams=4, early_stopping=True
        )
    summary = tokenizer.decode(output[0], skip_special_tokens=True)
    summary = summary.replace("<n>", " ").strip()

    return {"summary": summary}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # Session ID for chat history, auto-generated if not provided
    conversation_history: Optional[List[Dict[str, str]]] = []  # Optional: for maintaining context (deprecated, use session_id instead)


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, str]]
    created_at: str


# Initialize database on startup
init_database()




def get_chat_history(session_id: str, limit: int = 10) -> List[Dict[str, str]]:
    """Get chat history from database for a session"""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT user_message, assistant_message FROM chat_history WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
            (session_id, limit)
        )
        rows = cursor.fetchall()
        # Reverse to get chronological order
        history = []
        for row in reversed(rows):
            history.append({
                "user": row["user_message"],
                "assistant": row["assistant_message"]
            })
        return history

def save_chat_message(session_id: str, user_message: str, assistant_message: str):
    """Save chat message to database"""
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO chat_history (session_id, user_message, assistant_message) VALUES (?, ?, ?)",
            (session_id, user_message, assistant_message)
        )

@app.post("/chat")
def chat(req: ChatRequest):
    """
    Medical chatbot endpoint using Google Gemini with chat history management.
    
    This endpoint:
    - Automatically creates/generates session_id if not provided
    - Retrieves conversation history from database if session_id is provided
    - Saves chat messages to database for future reference
    - Provides clear, contextual responses based on conversation history
    """
    message = req.message
    
    if not message.strip():
        raise HTTPException(status_code=400, detail="Message is empty")
    
    # Check if Gemini API key is configured
    if not GEMINI_API_KEY or not gemini_model:
        raise HTTPException(
            status_code=503,
            detail="Gemini API key not configured. Please set GEMINI_API_KEY environment variable."
        )
    
    try:
        # Generate or use provided session_id
        session_id = req.session_id or str(uuid.uuid4())
        
        # Get chat history from database (prioritize database over manual history)
        chat_history = []
        if session_id:
            chat_history = get_chat_history(session_id, limit=10)
        
        # Fallback to manual conversation_history if no database history
        if not chat_history and req.conversation_history:
            chat_history = req.conversation_history
        
        # Build prompt with system instructions and conversation history
        # Format optimized for Gemini to ensure complete, contextual responses
        prompt_parts = [MEDICAL_SYSTEM_PROMPT]
        
        # Add conversation history for better context (last 10 messages)
        if chat_history:
            prompt_parts.append("\n\nConversation history:")
            for exchange in chat_history[-10:]:  # Last 10 exchanges for context
                user_msg = exchange.get("user", "")
                assistant_msg = exchange.get("assistant", "")
                if user_msg and assistant_msg:
                    prompt_parts.append(f"User: {user_msg}")
                    prompt_parts.append(f"Assistant: {assistant_msg}")
        
        # Add current user message with clear instruction
        prompt_parts.append(f"\n\nCurrent user question: {message}")
        prompt_parts.append("\nProvide a brief, concise medical answer (2-4 sentences) based on the conversation context:")
        
        # Combine all parts into full prompt
        full_prompt = "\n".join(prompt_parts)
        
        # Call Gemini API with short response configuration
        response = gemini_model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,  # Balanced temperature for medical responses
                top_p=0.9,
                top_k=40,
                max_output_tokens=300,  # Short responses - 2-4 sentences max (enough for complete answer)
            )
        )
        
        # Extract the assistant's response
        assistant_response = response.text.strip()
        
        # Check if response was cut off (finish_reason == 'MAX_TOKENS')
        if hasattr(response, 'candidates') and len(response.candidates) > 0:
            finish_reason = response.candidates[0].finish_reason
            # If response was cut off, try to complete it or add note
            if finish_reason == 'MAX_TOKENS' and not assistant_response.endswith('.'):
                # Response was truncated, but we'll use what we have
                pass
        
        # Ensure response is not empty
        if not assistant_response:
            assistant_response = "I apologize, but I couldn't generate a response. Please try again or consult a healthcare provider."
        
        # Save to database
        save_chat_message(session_id, message, assistant_response)
        
        return {
            "response": assistant_response,
            "message": message,
            "session_id": session_id,
            "model": GEMINI_MODEL
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response from Gemini: {str(e)}"
        )


@app.get("/chat/history/{session_id}")
def get_chat_history_endpoint(session_id: str, limit: Optional[int] = 50):
    """
    Get chat history for a specific session.
    
    Useful for mobile apps to retrieve and display chat history.
    """
    try:
        history = get_chat_history(session_id, limit=limit or 50)
        return {
            "session_id": session_id,
            "messages": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat history: {str(e)}"
        )

@app.delete("/chat/history/{session_id}")
def delete_chat_history(session_id: str):
    """
    Delete all chat history for a specific session.
    
    Useful for mobile apps to clear chat history.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM chat_history WHERE session_id = ?",
                (session_id,)
            )
            deleted_count = cursor.rowcount
        
        return {
            "session_id": session_id,
            "deleted_count": deleted_count,
            "message": f"Deleted {deleted_count} messages"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting chat history: {str(e)}"
        )

@app.get("/chat/sessions")
def list_sessions(limit: Optional[int] = 20):
    """
    List recent chat sessions.
    
    Returns session IDs with their latest message timestamps.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                """
                SELECT session_id, MAX(created_at) as last_message_at, COUNT(*) as message_count
                FROM chat_history
                GROUP BY session_id
                ORDER BY last_message_at DESC
                LIMIT ?
                """,
                (limit or 20,)
            )
            sessions = [
                {
                    "session_id": row["session_id"],
                    "last_message_at": row["last_message_at"],
                    "message_count": row["message_count"]
                }
                for row in cursor.fetchall()
            ]
        
        return {
            "sessions": sessions,
            "count": len(sessions)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing sessions: {str(e)}"
        )

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "services": ["summarization", "chatbot", "chat_history"]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
