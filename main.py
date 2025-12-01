from fastapi import FastAPI
from pydantic import BaseModel
from transformers import T5ForConditionalGeneration, T5Tokenizer

app = FastAPI()

# Load basic T5-small model
model_name = "google-t5/t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

class InputText(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "Local T5 summarization server is running!"}

@app.post("/summarize")
def summarize(input: InputText):
    content = "summarize: " + input.text

    inputs = tokenizer.encode(
        content,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    outputs = model.generate(
        inputs,
        max_length=150,
        min_length=20,
        num_beams=4,
        length_penalty=2.0
    )

    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"summary": summary}