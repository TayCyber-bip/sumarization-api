from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel
import torch
import re

app = FastAPI()

BASE_MODEL_PATH = "./models/long-t5-tglobal-base-16384-book-summary"
PEFT_MODEL_PATH = "./models/peft/peft-pubmed-summary"

device = "cuda" if torch.cuda.is_available() else "cpu"

# Load tokenizer (BASE MODEL)
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH)

# Load base LongT5 model
base_model = AutoModelForSeq2SeqLM.from_pretrained(
    BASE_MODEL_PATH,
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    device_map="auto"
)

# Attach PEFT adapter
model = PeftModel.from_pretrained(
    base_model,
    PEFT_MODEL_PATH
)

model.eval()
model.config.use_cache = False

class SummarizeRequest(BaseModel):
    article: str

def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # combine newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Combine space
    text = re.sub(r"[ \t]+", " ", text)

    # Strip
    return text.strip()

@app.post("/summarize")
def summarize(req: SummarizeRequest):
    text = normalize_text(req.article)

    if not text:
        raise HTTPException(400, "Empty text")

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=4096
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            num_beams=4,
            length_penalty=1.0,
            early_stopping=True,
            repetition_penalty=1.1,
            no_repeat_ngram_size=3
        )

    summary = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    )

    return {"summary": summary}
@app.post("/summarize-plain-text")
async def summarize(request: Request):
    # Nhận raw body
    raw_text = await request.body()
    text = raw_text.decode("utf-8")

    text = normalize_text(text)

    if not text:
        raise HTTPException(400, "Empty text")

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=4096
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            num_beams=4,
            length_penalty=1.0,
            early_stopping=True,
            repetition_penalty=1.1,
            no_repeat_ngram_size=3
        )

    summary = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    )

    return {"summary": summary}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
