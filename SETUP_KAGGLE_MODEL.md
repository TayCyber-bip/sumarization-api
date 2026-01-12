# Hướng dẫn Setup Model từ Kaggle Notebook

## Bước 1: Lấy Model Name từ Kaggle Notebook

### Cách 1: Copy code từ Kaggle (Khuyến nghị)

1. Truy cập: https://www.kaggle.com/code/abbasyed/abbas-syed-medical-chatbot
2. Tìm các dòng code load model, thường sẽ có dạng:
   ```python
   from transformers import AutoModelForCausalLM, AutoTokenizer
   model = AutoModelForCausalLM.from_pretrained("MODEL_NAME_HERE")
   ```
3. Copy `MODEL_NAME_HERE` (ví dụ: `microsoft/DialoGPT-medium`, `gpt2`, etc.)

### Cách 2: Sử dụng script phân tích

1. Copy toàn bộ code từ Kaggle notebook
2. Paste vào file `kaggle_notebook/notebook_code.py`
3. Chạy:
   ```bash
   cd kaggle_notebook
   python analyze_notebook.py
   ```
4. Script sẽ tự động tìm model name và loại model

## Bước 2: Cập nhật Model trong main.py

Mở file `main.py` và tìm dòng khoảng **dòng 39**, cập nhật:

```python
CHATBOT_MODEL_NAME = os.getenv("CHATBOT_MODEL_NAME", "YOUR_MODEL_NAME_HERE")
CHATBOT_MODEL_TYPE = os.getenv("CHATBOT_MODEL_TYPE", "causal")  # hoặc "seq2seq"
```

**Ví dụ:**
- Nếu notebook dùng `AutoModelForCausalLM` với model `microsoft/DialoGPT-medium`:
  ```python
  CHATBOT_MODEL_NAME = os.getenv("CHATBOT_MODEL_NAME", "microsoft/DialoGPT-medium")
  CHATBOT_MODEL_TYPE = os.getenv("CHATBOT_MODEL_TYPE", "causal")
  ```

- Nếu notebook dùng `AutoModelForSeq2SeqLM` với model `google/flan-t5-base`:
  ```python
  CHATBOT_MODEL_NAME = os.getenv("CHATBOT_MODEL_NAME", "google/flan-t5-base")
  CHATBOT_MODEL_TYPE = os.getenv("CHATBOT_MODEL_TYPE", "seq2seq")
  ```

## Bước 3: Restart Server

```bash
# Dừng server hiện tại (Ctrl+C)
# Sau đó chạy lại:
source venv/bin/activate
python main.py
```

## Bước 4: Test trong Postman

1. **Health Check:**
   - GET `http://localhost:8000/health`

2. **Test Chatbot:**
   - POST `http://localhost:8000/chat`
   - Body:
   ```json
   {
     "message": "What are the symptoms of flu?"
   }
   ```

## Model hiện tại đang được cấu hình

Hiện tại đang dùng **DialoGPT-medium** để test. Đây là model phổ biến cho chatbot conversation.

Sau khi bạn có model name từ Kaggle notebook, chỉ cần thay đổi `CHATBOT_MODEL_NAME` trong `main.py` là được!

## Troubleshooting

### Model không tải được
- Kiểm tra internet connection
- Kiểm tra model name có đúng không
- Kiểm tra disk space: `df -h`

### Response không đúng format
- Có thể cần điều chỉnh prompt format trong hàm `chat()` trong `main.py`
- Xem cách notebook format input và áp dụng tương tự

### Cần hỗ trợ?
Gửi cho tôi:
1. Model name từ Kaggle notebook
2. Loại model (causal hay seq2seq)
3. Prompt format được sử dụng (nếu có)

Tôi sẽ giúp bạn cấu hình chính xác!

