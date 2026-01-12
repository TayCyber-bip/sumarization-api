# Hướng dẫn Setup Model từ Kaggle Notebook

## Tổng quan

Từ Kaggle notebook của Abbas Syed, có 3 cách tiếp cận:

1. **Milestone 2**: Rule-based với TF-IDF (đơn giản, không cần model lớn)
2. **Milestone 3**: RAG với Llama-2-7B-Chat + SentenceTransformer (cần GPU)
3. **Milestone 4**: Fine-tuned Llama-2/BioMistral với QLoRA (cần GPU, tốt nhất)

## Model được sử dụng trong Notebook

### Milestone 3 (RAG):
- **LLM**: `TheBloke/Llama-2-7B-Chat-GPTQ` (quantized, ~4GB)
- **Embedding**: `all-MiniLM-L6-v2` (SentenceTransformer)
- **Approach**: RAG với semantic search

### Milestone 4 (Fine-tuning):
- **Base Model**: `NousResearch/Llama-2-7b-chat-hf` hoặc `BioMistral/BioMistral-7B`
- **Fine-tuning**: QLoRA với LoRA
- **Approach**: Fine-tuned trên medical dataset

## Cấu hình cho Backend

### Option 1: Llama-2-7B-Chat (Từ Milestone 3) - Khuyến nghị nếu có GPU

```python
# Trong main.py hoặc environment variables
CHATBOT_MODEL_NAME = "TheBloke/Llama-2-7B-Chat-GPTQ"  # Quantized version, nhỏ hơn
CHATBOT_MODEL_TYPE = "causal"
USE_LLAMA_FORMAT = "true"  # Tự động detect nếu model name chứa "llama"
```

**Yêu cầu:**
- GPU với ít nhất 8GB VRAM (cho quantized version)
- Hoặc CPU với 16GB+ RAM (chậm hơn nhiều)

### Option 2: BioMistral-7B (Từ Milestone 4) - Tốt nhất cho Medical

```python
CHATBOT_MODEL_NAME = "BioMistral/BioMistral-7B"
CHATBOT_MODEL_TYPE = "causal"
USE_LLAMA_FORMAT = "true"  # BioMistral cũng dùng format tương tự
```

**Yêu cầu:**
- GPU với ít nhất 14GB VRAM
- Hoặc CPU với 32GB+ RAM

### Option 3: Model nhỏ hơn (Cho testing không có GPU)

```python
CHATBOT_MODEL_NAME = "microsoft/DialoGPT-medium"  # ~350MB
CHATBOT_MODEL_TYPE = "causal"
USE_LLAMA_FORMAT = "false"
```

**Yêu cầu:**
- CPU với 4GB+ RAM

## Cách cấu hình

### Cách 1: Cấu hình trong code (main.py)

Mở `main.py`, tìm dòng ~46 và cập nhật:

```python
# Cho Llama-2 (từ notebook Milestone 3)
CHATBOT_MODEL_NAME = os.getenv("CHATBOT_MODEL_NAME", "TheBloke/Llama-2-7B-Chat-GPTQ")
USE_LLAMA_FORMAT = os.getenv("USE_LLAMA_FORMAT", "true").lower() == "true"

# Hoặc cho BioMistral (từ notebook Milestone 4)
CHATBOT_MODEL_NAME = os.getenv("CHATBOT_MODEL_NAME", "BioMistral/BioMistral-7B")
USE_LLAMA_FORMAT = os.getenv("USE_LLAMA_FORMAT", "true").lower() == "true"
```

### Cách 2: Sử dụng Environment Variables

```bash
export CHATBOT_MODEL_NAME="TheBloke/Llama-2-7B-Chat-GPTQ"
export CHATBOT_MODEL_TYPE="causal"
export USE_LLAMA_FORMAT="true"
python main.py
```

## Prompt Format

Backend đã được cấu hình để tự động sử dụng Llama-2 format khi detect model name chứa "llama" hoặc "mistral":

```
<s>[INST] <<SYS>>
You are a medical assistant. List the top 2 possible diseases for these symptoms. 
Be concise and give the response in points. Make sure to include a disclaimer telling 
users that this is not a medical diagnosis and they should always consult a doctor.
<</SYS>>

Symptoms: {user_input} [/INST]
```

Format này khớp với format trong Kaggle notebook.

## Generation Parameters

Backend sử dụng các parameters từ notebook:
- `max_new_tokens=300` (tăng từ 150 cho Llama-2)
- `temperature=0.2` (thấp hơn cho medical, từ notebook)
- `top_p=0.9`
- `repetition_penalty=1.2`

## RAG (Milestone 3) - Tùy chọn

Nếu muốn tích hợp RAG như trong Milestone 3:

1. **Cài đặt thêm:**
```bash
pip install sentence-transformers
```

2. **Cấu hình:**
```python
ENABLE_RAG = True
```

3. **Cần có dataset:** Tải dataset từ Kaggle và tạo embeddings

RAG sẽ được tích hợp trong phiên bản tiếp theo nếu cần.

## Test

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Test Chatbot
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "fever, cough, sore throat"}'
```

### 3. Test trong Postman
- Method: `POST`
- URL: `http://localhost:8000/chat`
- Body:
```json
{
  "message": "I have a headache and fever"
}
```

## Lưu ý quan trọng

### Về Model Size:
- **Llama-2-7B**: ~14GB (full precision) hoặc ~4GB (quantized GPTQ)
- **BioMistral-7B**: ~14GB
- **DialoGPT-medium**: ~350MB

### Về GPU:
- Llama-2 và BioMistral **cần GPU** để chạy hiệu quả
- Nếu không có GPU, model sẽ chạy trên CPU nhưng rất chậm (có thể mất vài phút mỗi response)
- Khuyến nghị: Dùng quantized version (`TheBloke/Llama-2-7B-Chat-GPTQ`) nếu có GPU nhỏ

### Về Memory:
- GPU: Ít nhất 8GB VRAM cho quantized Llama-2
- RAM: Ít nhất 16GB cho CPU inference

## Troubleshooting

### Lỗi: "Out of memory"
- **Giải pháp**: Dùng model nhỏ hơn hoặc quantized version
- Hoặc giảm `max_new_tokens` trong code

### Lỗi: "Model loading failed"
- Kiểm tra internet connection (model sẽ được tải từ HuggingFace)
- Kiểm tra disk space (model có thể lớn)
- Kiểm tra model name có đúng không

### Response chậm
- **Bình thường** nếu chạy trên CPU với model lớn
- Khuyến nghị: Dùng GPU hoặc model nhỏ hơn

## So sánh các Model

| Model | Size | GPU Required | Quality | Speed (GPU) | Speed (CPU) |
|-------|------|--------------|---------|-------------|-------------|
| DialoGPT-medium | 350MB | No | Good | N/A | Fast |
| Llama-2-7B-Chat-GPTQ | 4GB | Yes (8GB+) | Excellent | Fast | Very Slow |
| BioMistral-7B | 14GB | Yes (14GB+) | Best (Medical) | Fast | Very Slow |

## Khuyến nghị

1. **Cho testing**: Dùng `DialoGPT-medium` (đã cấu hình sẵn)
2. **Cho production với GPU**: Dùng `TheBloke/Llama-2-7B-Chat-GPTQ`
3. **Cho production medical-specific**: Dùng `BioMistral/BioMistral-7B` (nếu có GPU mạnh)

## Next Steps

1. Cấu hình model name trong `main.py`
2. Restart server
3. Test với Postman
4. Nếu cần RAG, có thể tích hợp thêm sau

