from fastapi import FastAPI
from dotenv import load_dotenv

from app.routes import summarization, chatbot

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Include routers
app.include_router(summarization.router)
app.include_router(chatbot.router)

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "services": ["summarization", "chatbot", "chat_history"]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
