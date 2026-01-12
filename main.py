from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForCausalLM
import torch
import os
from typing import Optional, List, Dict
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

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
    conversation_history: Optional[List[Dict[str, str]]] = []  # Optional: for maintaining context




@app.post("/chat")
def chat(req: ChatRequest):
    """
    Medical chatbot endpoint using Google Gemini.
    
    This endpoint uses Google's Gemini models to provide medical information and guidance.
    Configured specifically for health-related conversations with appropriate disclaimers.
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
        # Build prompt with system instructions and conversation history
        # Format optimized for Gemini to ensure complete responses
        prompt_parts = [MEDICAL_SYSTEM_PROMPT]
        
        # Add conversation history if available
        if req.conversation_history:
            prompt_parts.append("\n\nPrevious conversation:")
            for exchange in req.conversation_history[-5:]:  # Last 5 exchanges for context
                user_msg = exchange.get("user", "")
                assistant_msg = exchange.get("assistant", "")
                if user_msg:
                    prompt_parts.append(f"User: {user_msg}")
                if assistant_msg:
                    prompt_parts.append(f"Assistant: {assistant_msg}")
        
        # Add current user message with clear instruction
        prompt_parts.append(f"\n\nUser question: {message}")
        prompt_parts.append("\nProvide a brief, concise medical answer (2-4 sentences):")
        
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
        
        return {
            "response": assistant_response,
            "message": message,
            "model": GEMINI_MODEL
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response from Gemini: {str(e)}"
        )


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "services": ["summarization", "chatbot"]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
