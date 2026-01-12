# Cấu hình Google Gemini cho Medical Chatbot

## ✅ Đã cấu hình

### 1. Trả lời ngắn gọn
- **max_output_tokens**: 300 (đủ cho 2-4 câu)
- **System prompt**: Yêu cầu trả lời ngắn gọn, tối đa 2-4 câu
- Response format: Ngắn gọn, súc tích, đi thẳng vào vấn đề

### 2. Focus vào Y tế & Sức khỏe
- **System prompt**: Chuyên biệt cho medical/health topics
- Chỉ trả lời các câu hỏi về y tế và sức khỏe
- Từ chối/redirect các câu hỏi không liên quan đến y tế
- Ngôn ngữ y tế đơn giản, dễ hiểu

## System Prompt

```
You are a specialized medical and health assistant chatbot. 
Your expertise is focused exclusively on health, medical conditions, symptoms, and wellness.

- Keep responses SHORT and CONCISE - maximum 2-4 sentences
- Focus ONLY on medical and health topics
- Use simple, clear medical language
- Always emphasize this is NOT a medical diagnosis
- Recommend consulting a doctor for proper diagnosis
```

## Generation Config

```python
temperature=0.7        # Balanced for medical responses
top_p=0.9             # Focus on most likely tokens
top_k=40              # Limit candidate tokens
max_output_tokens=300 # Short responses (2-4 sentences)
```

## Model

- **Model**: `models/gemini-2.5-flash`
- **API Key**: Đã lưu trong `.env`
- **Focus**: Medical & Health topics only

## Test Examples

### Example 1: Symptoms
```json
{
  "message": "I have a headache and fever, what should I do?"
}
```

**Response**: Ngắn gọn, đưa ra lời khuyên cụ thể, có disclaimer

### Example 2: Medical Question
```json
{
  "message": "What causes high blood pressure?"
}
```

**Response**: Giải thích ngắn gọn về nguyên nhân, focus vào y tế

## Lưu ý

1. **Response length**: Tự động giới hạn ở 2-4 câu
2. **Medical focus**: Chỉ trả lời về y tế/sức khỏe
3. **Disclaimer**: Luôn có disclaimer về không phải chẩn đoán y tế
4. **Non-medical questions**: Sẽ redirect về health topics

## Cấu hình hiện tại

- ✅ Trả lời ngắn gọn (2-4 câu)
- ✅ Focus vào y tế và sức khỏe
- ✅ System prompt chuyên biệt
- ✅ Generation config tối ưu
- ✅ Model: gemini-2.5-flash

Server đang chạy và sẵn sàng test! 🚀

