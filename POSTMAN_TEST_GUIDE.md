# Hướng dẫn test API với Postman

## Server đang chạy tại:
- **URL**: `http://localhost:8000`
- **Port**: 8000

## Các endpoint có sẵn:

### 1. Health Check (GET)
**Endpoint**: `GET http://localhost:8000/health`

**Request trong Postman:**
- Method: `GET`
- URL: `http://localhost:8000/health`
- Headers: Không cần

**Response mẫu:**
```json
{
  "status": "healthy",
  "services": ["summarization", "chatbot"]
}
```

---

### 2. Summarization (POST)
**Endpoint**: `POST http://localhost:8000/summarize`

**Request trong Postman:**
- Method: `POST`
- URL: `http://localhost:8000/summarize`
- Headers:
  - `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "text": "Your long medical text here that you want to summarize. This can be a research paper abstract, medical report, or any lengthy text that needs summarization."
}
```

**Response mẫu:**
```json
{
  "summary": "Summarized text here..."
}
```

**Ví dụ Body:**
```json
{
  "text": "Influenza, commonly known as the flu, is an infectious disease caused by influenza viruses. Symptoms range from mild to severe and often include fever, runny nose, sore throat, muscle pain, headache, coughing, and fatigue. The flu spreads around the world in yearly outbreaks, resulting in about three to five million cases of severe illness and about 290,000 to 650,000 deaths."
}
```

---

### 3. Medical Chatbot (POST)
**Endpoint**: `POST http://localhost:8000/chat`

⚠️ **Lưu ý**: Endpoint này sẽ trả về lỗi 503 nếu chưa cấu hình `CHATBOT_MODEL_NAME` trong code.

**Request trong Postman:**
- Method: `POST`
- URL: `http://localhost:8000/chat`
- Headers:
  - `Content-Type: application/json`
- Body (raw JSON) - Option 1: Chỉ message:
```json
{
  "message": "What are the symptoms of flu?"
}
```

- Body (raw JSON) - Option 2: Với conversation history:
```json
{
  "message": "What should I do?",
  "conversation_history": [
    {
      "user": "I have a headache",
      "assistant": "How long have you had it?"
    },
    {
      "user": "2 days",
      "assistant": "Any other symptoms?"
    }
  ]
}
```

**Response mẫu (khi đã cấu hình model):**
```json
{
  "response": "Based on your symptoms...",
  "message": "What are the symptoms of flu?"
}
```

**Response khi chưa cấu hình:**
```json
{
  "detail": "Chatbot model not configured. Please set CHATBOT_MODEL_NAME in the code."
}
```

---

## Cách test trong Postman:

### Bước 1: Test Health Check
1. Tạo request mới
2. Chọn method `GET`
3. Nhập URL: `http://localhost:8000/health`
4. Click **Send**
5. Kiểm tra response có `"status": "healthy"`

### Bước 2: Test Summarization
1. Tạo request mới
2. Chọn method `POST`
3. Nhập URL: `http://localhost:8000/summarize`
4. Vào tab **Headers**, thêm:
   - Key: `Content-Type`
   - Value: `application/json`
5. Vào tab **Body**, chọn **raw** và **JSON**
6. Paste JSON body mẫu ở trên
7. Click **Send**
8. Đợi response (có thể mất vài giây để model xử lý)

### Bước 3: Test Chatbot
1. Tạo request mới
2. Chọn method `POST`
3. Nhập URL: `http://localhost:8000/chat`
4. Vào tab **Headers**, thêm:
   - Key: `Content-Type`
   - Value: `application/json`
5. Vào tab **Body**, chọn **raw** và **JSON**
6. Paste JSON body mẫu ở trên
7. Click **Send**

---

## Lưu ý:

1. **Model loading**: Lần đầu chạy, model BigBird-Pegasus sẽ được load vào memory, có thể mất 1-2 phút tùy vào máy của bạn.

2. **Memory**: Model này khá lớn, đảm bảo máy có đủ RAM (khuyến nghị ít nhất 8GB).

3. **Response time**: 
   - Health check: < 1 giây
   - Summarization: 5-15 giây (tùy độ dài text)
   - Chatbot: Sẽ báo lỗi nếu chưa cấu hình model

4. **Error handling**: Nếu gặp lỗi, kiểm tra:
   - Server có đang chạy không
   - Port 8000 có bị chiếm không
   - Model có được load thành công không

---

## Troubleshooting:

### Lỗi: "Connection refused"
→ Server chưa khởi động xong, đợi thêm vài giây rồi thử lại

### Lỗi: "Model loading..."
→ Đây là bình thường lần đầu, đợi model load xong

### Lỗi: "Out of memory"
→ Model quá lớn, cần máy có nhiều RAM hơn hoặc sử dụng model nhỏ hơn

### Response chậm
→ Bình thường với model lớn, có thể mất 10-30 giây cho mỗi request

---

## Collection Postman (Import vào Postman):

Bạn có thể tạo Postman Collection với các request trên để test dễ dàng hơn!

