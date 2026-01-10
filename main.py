from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

app = FastAPI()

BASE_MODEL_PATH = "./models/llama2-7b"
PEFT_MODEL_PATH = "./models/peft/peft-dialogue-summary"

# Load tokenizer (BASE MODEL, không phải PEFT)
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH)
tokenizer.pad_token = tokenizer.eos_token

# Load base model
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_PATH,
    torch_dtype=torch.float16,
    device_map="auto"
)

# Attach PEFT
model = PeftModel.from_pretrained(
    base_model,
    PEFT_MODEL_PATH
)

model.eval()

def build_prompt(text: str) -> str:
    return f"""Summarize the following conversation.

### Input:
{text}

### Summary:
"""

class SummarizeRequest(BaseModel):
    text: str

@app.post("/summarize")
def summarize(req: SummarizeRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is empty")

    prompt = build_prompt(req.text)

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1024
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.6,
            top_p=0.9,
            repetition_penalty=1.15,
            do_sample=False,
        )

    decoded = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    )

    # Cắt bỏ prompt
    summary = decoded[len(prompt):].strip()

    return {"summary": summary}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
