from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

app = FastAPI()


MODEL_NAME = "google/bigbird-pegasus-large-pubmed"

model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    cache_dir="./models/bigbird_pubmed"
)

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    cache_dir="./models/bigbird_pubmed"
)

class SummarizeRequest(BaseModel):
    text: str

@app.post("/summarize")
def summarize(req: SummarizeRequest):
    text = req.text

    if not text.strip():
        raise HTTPException(status_code=400, detail="Text is empty")

    content = "summarize: " + text

    inputs = tokenizer.encode(
        content,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    output = model.generate(
        inputs,
        max_new_tokens=120,
        num_beams=2
    )

    return {
        "summary": tokenizer.decode(output[0], skip_special_tokens=True)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
