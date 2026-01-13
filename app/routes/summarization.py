"""Summarization API routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

router = APIRouter(prefix="/summarize", tags=["summarization"])

# Summarization model
MODEL_NAME = "google/bigbird-pegasus-large-pubmed"

# Load model and tokenizer
model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME, cache_dir="./models/bigbird_pubmed"
)

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME, cache_dir="./models/bigbird_pubmed"
)


class SummarizeRequest(BaseModel):
    text: str


@router.post("")
def summarize(req: SummarizeRequest):
    """Summarize text using BigBird-Pegasus model"""
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

