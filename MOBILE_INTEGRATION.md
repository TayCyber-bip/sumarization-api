# Hướng dẫn tích hợp Chat History cho Mobile App

## Tổng quan

API đã được cải thiện với chat history management để tích hợp vào mobile app:
- **Tự động tạo session ID** cho mỗi conversation
- **Lưu chat history** vào database (SQLite)
- **API endpoints** để lấy/xóa chat history
- **Context-aware responses** dựa trên conversation history

## Database

Chat history được lưu trong SQLite database (`chat_history.db`):
- **Table**: `chat_history`
- **Fields**: `session_id`, `user_message`, `assistant_message`, `created_at`
- Database tự động được tạo khi server khởi động

## API Endpoints

### 1. Chat với History (POST `/chat`)

**Endpoint**: `POST http://localhost:8000/chat`

**Request Body**:
```json
{
  "message": "I have a headache",
  "session_id": "optional-session-id"  // Tự động tạo nếu không có
}
```

**Response**:
```json
{
  "response": "A headache is a common symptom...",
  "message": "I have a headache",
  "session_id": "a418a752-2e6c-479b-8123-e0ce5cb85d6c",
  "model": "models/gemini-2.5-flash"
}
```

**Lưu ý**:
- Nếu không có `session_id`, API sẽ tự động tạo một session ID mới
- API tự động lấy chat history từ database dựa trên `session_id`
- Mỗi message sẽ được lưu vào database tự động

**Mobile Integration Flow**:
1. Lần đầu chat: Gửi message không có `session_id` → Nhận `session_id` mới
2. Lần sau: Dùng `session_id` đã lưu để tiếp tục conversation
3. API tự động sử dụng history để trả lời context-aware

---

### 2. Lấy Chat History (GET `/chat/history/{session_id}`)

**Endpoint**: `GET http://localhost:8000/chat/history/{session_id}?limit=50`

**Query Parameters**:
- `limit` (optional): Số lượng messages tối đa (default: 50)

**Response**:
```json
{
  "session_id": "a418a752-2e6c-479b-8123-e0ce5cb85d6c",
  "messages": [
    {
      "user": "I have a headache",
      "assistant": "A headache is a common symptom..."
    },
    {
      "user": "I have a fever too",
      "assistant": "Fever combined with headache..."
    }
  ],
  "count": 2
}
```

**Use Case cho Mobile**:
- Load chat history khi mở conversation
- Hiển thị previous messages trong chat UI

---

### 3. Xóa Chat History (DELETE `/chat/history/{session_id}`)

**Endpoint**: `DELETE http://localhost:8000/chat/history/{session_id}`

**Response**:
```json
{
  "session_id": "a418a752-2e6c-479b-8123-e0ce5cb85d6c",
  "deleted_count": 5,
  "message": "Deleted 5 messages"
}
```

**Use Case cho Mobile**:
- Clear chat history khi user muốn bắt đầu conversation mới
- Delete old conversations để free up space

---

### 4. List Sessions (GET `/chat/sessions`)

**Endpoint**: `GET http://localhost:8000/chat/sessions?limit=20`

**Query Parameters**:
- `limit` (optional): Số lượng sessions tối đa (default: 20)

**Response**:
```json
{
  "sessions": [
    {
      "session_id": "a418a752-2e6c-479b-8123-e0ce5cb85d6c",
      "last_message_at": "2024-01-12 10:30:00",
      "message_count": 5
    },
    {
      "session_id": "b529b863-3f7d-580c-9234-f1df6dc96e7d",
      "last_message_at": "2024-01-12 09:15:00",
      "message_count": 3
    }
  ],
  "count": 2
}
```

**Use Case cho Mobile**:
- Hiển thị danh sách conversations trong app
- Hiển thị preview của last message
- Sort conversations by `last_message_at`

---

## Mobile Integration Example

### Flow 1: Tạo conversation mới

```javascript
// 1. Gửi message đầu tiên (không có session_id)
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'I have a headache'
  })
});

const data = await response.json();
const sessionId = data.session_id; // Lưu session_id này

// 2. Lần sau, dùng session_id này để tiếp tục
const nextResponse = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'I have a fever too',
    session_id: sessionId
  })
});
```

### Flow 2: Load chat history

```javascript
// Load history khi mở conversation
const historyResponse = await fetch(
  `http://localhost:8000/chat/history/${sessionId}?limit=50`
);
const history = await historyResponse.json();

// Display messages
history.messages.forEach(msg => {
  displayUserMessage(msg.user);
  displayAssistantMessage(msg.assistant);
});
```

### Flow 3: List conversations

```javascript
// Load danh sách conversations
const sessionsResponse = await fetch(
  'http://localhost:8000/chat/sessions?limit=20'
);
const sessions = await sessionsResponse.json();

// Display conversation list
sessions.sessions.forEach(session => {
  displayConversationItem({
    id: session.session_id,
    lastMessage: session.last_message_at,
    messageCount: session.message_count
  });
});
```

### Flow 4: Clear history

```javascript
// Clear chat history
await fetch(
  `http://localhost:8000/chat/history/${sessionId}`,
  { method: 'DELETE' }
);
```

---

## Cải thiện Response Quality

### 1. Context-aware Responses

API tự động sử dụng chat history (last 10 messages) để:
- Hiểu context của conversation
- Trả lời dựa trên previous questions
- Cung cấp thông tin liên quan và rõ ràng hơn

### 2. Better Prompt Format

Prompt được format tốt hơn với:
- System prompt cho medical chatbot
- Conversation history được include
- Clear instructions cho model

**Example**:
```
System: [Medical assistant instructions]
Conversation history:
User: I have a headache
Assistant: [Previous response]
Current user question: I have a fever too
Provide a brief, concise medical answer based on conversation context:
```

---

## Test trong Postman

### Test 1: Chat với session_id mới
```json
POST /chat
{
  "message": "I have a headache"
}
```

### Test 2: Chat tiếp với session_id
```json
POST /chat
{
  "message": "What should I do?",
  "session_id": "session-id-from-previous-response"
}
```

### Test 3: Lấy history
```
GET /chat/history/{session_id}
```

### Test 4: List sessions
```
GET /chat/sessions?limit=20
```

### Test 5: Xóa history
```
DELETE /chat/history/{session_id}
```

---

## Lưu ý cho Mobile Development

### 1. Session Management
- **Lưu session_id**: Lưu `session_id` khi nhận response đầu tiên
- **Reuse session_id**: Dùng `session_id` này cho tất cả messages trong conversation
- **Local storage**: Có thể lưu `session_id` trong local storage hoặc user preferences

### 2. History Loading
- **Lazy loading**: Load history khi user mở conversation, không load tất cả
- **Pagination**: Có thể implement pagination nếu cần (API hỗ trợ `limit`)

### 3. Error Handling
- **Invalid session_id**: API sẽ tạo session mới nếu không tìm thấy history
- **Network errors**: Implement retry logic cho mobile app

### 4. Performance
- **Caching**: Cache chat history trong mobile app để giảm API calls
- **Background sync**: Sync history trong background nếu cần

---

## Database Schema

```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    assistant_message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_session_id ON chat_history(session_id);
CREATE INDEX idx_created_at ON chat_history(created_at);
```

---

## Response Examples

### Example 1: First Message
```json
{
  "message": "I have a headache",
  "session_id": null  // Không có
}
```

**Response**:
```json
{
  "response": "A headache is a common symptom...",
  "message": "I have a headache",
  "session_id": "a418a752-2e6c-479b-8123-e0ce5cb85d6c",
  "model": "models/gemini-2.5-flash"
}
```

### Example 2: Follow-up Message (với context)
```json
{
  "message": "What should I do?",
  "session_id": "a418a752-2e6c-479b-8123-e0ce5cb85d6c"
}
```

**Response**: Sẽ dựa trên previous conversation về "headache"

---

## Benefits cho Mobile

✅ **Persistent History**: Chat history được lưu trên server
✅ **Multi-device**: Có thể access từ nhiều devices (nếu lưu session_id)
✅ **Context-aware**: Responses rõ ràng, cụ thể hơn nhờ history
✅ **Easy Integration**: Simple API endpoints, dễ tích hợp
✅ **Scalable**: SQLite database, có thể scale lên PostgreSQL sau

Server đang chạy và sẵn sàng cho mobile integration! 🚀

