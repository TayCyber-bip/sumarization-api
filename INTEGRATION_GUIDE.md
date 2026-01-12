# Hướng dẫn tích hợp Medical Chatbot từ Kaggle

## Tổng quan

Backend của bạn đã được chuẩn bị để tích hợp model chatbot y tế từ Kaggle notebook. Code hiện tại hỗ trợ cả hai loại model phổ biến:
- **Causal models** (GPT-2, DialoGPT, GPT-Neo): Cho chatbot hội thoại
- **Seq2Seq models** (T5, BART): Cho question-answering

## Các bước tích hợp

### Bước 1: Xác định loại model từ Kaggle notebook

Mở Kaggle notebook và kiểm tra:
1. **Model name/path**: Tên model được sử dụng (ví dụ: `microsoft/DialoGPT-medium`, `google/flan-t5-base`)
2. **Model type**: 
   - Nếu dùng `AutoModelForCausalLM` → `CHATBOT_MODEL_TYPE = "causal"`
   - Nếu dùng `AutoModelForSeq2SeqLM` → `CHATBOT_MODEL_TYPE = "seq2seq"`
3. **Prompt format**: Cách model được format input (có thể cần điều chỉnh)

### Bước 2: Cập nhật cấu hình trong `main.py`

Mở file `main.py` và cập nhật các biến sau:

```python
# Dòng 20-21
CHATBOT_MODEL_NAME = "your-model-name-here"  # Ví dụ: "microsoft/DialoGPT-medium"
CHATBOT_MODEL_TYPE = "causal"  # hoặc "seq2seq"
```

### Bước 3: Tùy chỉnh prompt format (nếu cần)

Nếu Kaggle notebook sử dụng format prompt khác, bạn có thể chỉnh sửa trong hàm `chat()`:

**Ví dụ cho medical chatbot với format đặc biệt:**
```python
# Thay vì format mặc định, có thể dùng:
prompt = f"Medical Question: {message}\nAnswer:"
# hoặc
prompt = f"Patient: {message}\nDoctor:"
```

### Bước 4: Tải model và test

1. **Chạy server:**
```bash
python main.py
```

2. **Test endpoint:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the symptoms of flu?"}'
```

3. **Test với conversation history:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What should I do?",
    "conversation_history": [
      {"user": "I have a headache", "assistant": "How long have you had it?"},
      {"user": "2 days", "assistant": "Any other symptoms?"}
    ]
  }'
```

## Các trường hợp đặc biệt

### Nếu model sử dụng RAG (Retrieval-Augmented Generation)

Nếu Kaggle notebook sử dụng RAG với vector database, bạn cần:
1. Thêm thư viện: `pip install faiss-cpu sentence-transformers` (hoặc tương tự)
2. Tạo module riêng cho RAG trong `rag_module.py`
3. Tích hợp vào hàm `chat()`

### Nếu model cần fine-tuning weights

Nếu bạn có file weights đã fine-tune:
1. Tải weights về và đặt trong `./models/chatbot/`
2. Load model với `from_pretrained()` trỏ đến thư mục local

### Nếu model sử dụng pipeline

Nếu Kaggle notebook dùng `pipeline()`:
```python
from transformers import pipeline

chatbot_pipeline = pipeline(
    "text-generation",
    model=CHATBOT_MODEL_NAME,
    tokenizer=CHATBOT_MODEL_NAME
)
```

## Ví dụ tích hợp cụ thể

### Ví dụ 1: DialoGPT (Causal Model)
```python
CHATBOT_MODEL_NAME = "microsoft/DialoGPT-medium"
CHATBOT_MODEL_TYPE = "causal"
```

### Ví dụ 2: Flan-T5 (Seq2Seq Model)
```python
CHATBOT_MODEL_NAME = "google/flan-t5-base"
CHATBOT_MODEL_TYPE = "seq2seq"
```

### Ví dụ 3: Model từ HuggingFace Hub
```python
CHATBOT_MODEL_NAME = "username/model-name"
CHATBOT_MODEL_TYPE = "causal"  # hoặc "seq2seq"
```

## Lưu ý quan trọng

1. **Memory**: Model lớn có thể tốn nhiều RAM. Cân nhắc sử dụng GPU nếu có.
2. **Performance**: Có thể thêm caching hoặc async processing cho production.
3. **Error handling**: Code đã có error handling cơ bản, có thể mở rộng thêm.
4. **Security**: Thêm rate limiting và input validation cho production.

## Troubleshooting

### Lỗi: "Chatbot model not configured"
→ Kiểm tra đã set `CHATBOT_MODEL_NAME` chưa

### Lỗi: "Failed to load chatbot model"
→ Kiểm tra:
- Model name có đúng không
- Internet connection (nếu tải từ HuggingFace)
- Disk space đủ không

### Response không đúng format
→ Điều chỉnh prompt format trong hàm `chat()`

## API Endpoints

- `POST /summarize` - Summarization (đã có sẵn)
- `POST /chat` - Medical chatbot (mới thêm)
- `GET /health` - Health check

## Cần hỗ trợ thêm?

Nếu bạn gửi cho tôi:
1. Model name từ Kaggle notebook
2. Loại model (causal/seq2seq)
3. Prompt format được sử dụng

Tôi có thể giúp bạn tích hợp chính xác hơn!

