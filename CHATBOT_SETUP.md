# Hướng dẫn cấu hình Chatbot Model

## Vấn đề: Endpoint /chat trả về lỗi 503

Lỗi này xảy ra vì `CHATBOT_MODEL_NAME` chưa được cấu hình. Có 2 cách để khắc phục:

---

## Cách 1: Cấu hình trực tiếp trong code (Đơn giản nhất - Khuyến nghị cho testing)

### Bước 1: Mở file `main.py`

### Bước 2: Tìm dòng này (khoảng dòng 30-35):
```python
# Option 2: Set directly in code (for testing/development)
# Uncomment and set your model name below:
# CHATBOT_MODEL_NAME = "microsoft/DialoGPT-medium"  # Example: Small conversational model
```

### Bước 3: Bỏ comment và đặt tên model của bạn

**Ví dụ với model từ Kaggle notebook:**
```python
CHATBOT_MODEL_NAME = "microsoft/DialoGPT-medium"  # Nếu notebook dùng DialoGPT
CHATBOT_MODEL_TYPE = "causal"  # Đảm bảo đúng loại model
```

**Hoặc nếu notebook dùng model khác:**
```python
CHATBOT_MODEL_NAME = "google/flan-t5-base"  # Nếu dùng T5
CHATBOT_MODEL_TYPE = "seq2seq"  # Đổi thành seq2seq cho T5
```

### Bước 4: Restart server
```bash
# Dừng server (Ctrl+C) và chạy lại:
source venv/bin/activate
python main.py
```

---

## Cách 2: Sử dụng biến môi trường (Khuyến nghị cho production)

### Trên macOS/Linux:
```bash
export CHATBOT_MODEL_NAME="microsoft/DialoGPT-medium"
export CHATBOT_MODEL_TYPE="causal"
python main.py
```

### Hoặc tạo file `.env`:
```bash
# Tạo file .env
echo "CHATBOT_MODEL_NAME=microsoft/DialoGPT-medium" > .env
echo "CHATBOT_MODEL_TYPE=causal" >> .env
```

---

## Các model đề xuất để test

### 1. Model nhỏ, nhanh (Tốt cho testing)

#### DialoGPT-small (Causal - ~117MB)
```python
CHATBOT_MODEL_NAME = "microsoft/DialoGPT-small"
CHATBOT_MODEL_TYPE = "causal"
```
- ✅ Nhỏ, nhanh
- ✅ Tốt cho hội thoại
- ⚠️ Không phải medical-specific

#### GPT-2 (Causal - ~500MB)
```python
CHATBOT_MODEL_NAME = "gpt2"
CHATBOT_MODEL_TYPE = "causal"
```
- ✅ Phổ biến, dễ test
- ⚠️ Không phải medical-specific

### 2. Model cho Medical (Nếu có từ Kaggle)

Nếu Kaggle notebook của bạn sử dụng model cụ thể, hãy dùng model đó:

**Ví dụ:**
```python
# Nếu notebook dùng model từ HuggingFace
CHATBOT_MODEL_NAME = "username/model-name-from-kaggle"
CHATBOT_MODEL_TYPE = "causal"  # hoặc "seq2seq"
```

### 3. Model Seq2Seq (Cho Q&A)

#### Flan-T5 Base (Seq2Seq - ~250MB)
```python
CHATBOT_MODEL_NAME = "google/flan-t5-base"
CHATBOT_MODEL_TYPE = "seq2seq"
```
- ✅ Tốt cho question-answering
- ✅ Có thể fine-tune cho medical

---

## Cách xác định model từ Kaggle notebook

### Bước 1: Mở Kaggle notebook
Truy cập: https://www.kaggle.com/code/abbasyed/abbas-syed-medical-chatbot

### Bước 2: Tìm dòng code load model
Tìm các dòng như:
```python
from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM
model = AutoModelForCausalLM.from_pretrained("MODEL_NAME_HERE")
# hoặc
model = AutoModelForSeq2SeqLM.from_pretrained("MODEL_NAME_HERE")
```

### Bước 3: Copy model name
- Nếu là `AutoModelForCausalLM` → `CHATBOT_MODEL_TYPE = "causal"`
- Nếu là `AutoModelForSeq2SeqLM` → `CHATBOT_MODEL_TYPE = "seq2seq"`

### Bước 4: Cập nhật vào `main.py`
```python
CHATBOT_MODEL_NAME = "MODEL_NAME_HERE"
CHATBOT_MODEL_TYPE = "causal"  # hoặc "seq2seq"
```

---

## Test sau khi cấu hình

### 1. Kiểm tra server đã load model:
```bash
curl http://localhost:8000/health
```

### 2. Test endpoint /chat:
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

### 3. Trong Postman:
- Method: `POST`
- URL: `http://localhost:8000/chat`
- Body:
```json
{
  "message": "What are the symptoms of flu?"
}
```

---

## Troubleshooting

### Lỗi: "Failed to load chatbot model"
**Nguyên nhân:**
- Model name sai
- Không có internet để tải model
- Thiếu disk space

**Giải pháp:**
1. Kiểm tra model name có đúng không
2. Kiểm tra internet connection
3. Kiểm tra disk space: `df -h`

### Lỗi: "Out of memory"
**Nguyên nhân:** Model quá lớn

**Giải pháp:**
- Dùng model nhỏ hơn (DialoGPT-small thay vì large)
- Hoặc tăng RAM/swap space

### Model load chậm
**Bình thường:** Lần đầu tải model từ HuggingFace có thể mất 5-10 phút tùy vào tốc độ internet.

---

## Ví dụ cấu hình hoàn chỉnh

### Ví dụ 1: DialoGPT-small (Khuyến nghị để test)
```python
# Trong main.py, dòng ~35
CHATBOT_MODEL_NAME = "microsoft/DialoGPT-small"
CHATBOT_MODEL_TYPE = "causal"
```

### Ví dụ 2: Flan-T5 Base
```python
CHATBOT_MODEL_NAME = "google/flan-t5-base"
CHATBOT_MODEL_TYPE = "seq2seq"
```

### Ví dụ 3: Model từ Kaggle
```python
# Thay bằng model name từ Kaggle notebook của bạn
CHATBOT_MODEL_NAME = "your-kaggle-model-name"
CHATBOT_MODEL_TYPE = "causal"  # hoặc "seq2seq" tùy vào model
```

---

## Lưu ý quan trọng

1. **Lần đầu chạy:** Model sẽ được tải về từ HuggingFace, có thể mất vài phút
2. **Model size:** Model lớn cần nhiều RAM (khuyến nghị ít nhất 8GB)
3. **Cache:** Model sẽ được cache trong `./models/chatbot/`, lần sau sẽ nhanh hơn
4. **Production:** Nên dùng biến môi trường thay vì hardcode trong code

---

## Cần hỗ trợ?

Nếu bạn gửi cho tôi:
1. Model name từ Kaggle notebook
2. Loại model (causal hay seq2seq)

Tôi có thể giúp bạn cấu hình chính xác!

