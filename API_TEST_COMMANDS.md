# API Test Commands - Chạy từ Windows/Mobile App

## Cấu hình

Trước khi chạy, đảm bảo server đang chạy tại: `http://localhost:8000` (hoặc URL của server)

---

## 1. Health Check

### Windows PowerShell
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET | ConvertTo-Json
```

### Windows CMD (với curl)
```cmd
curl http://localhost:8000/health
```

### Mobile App Test (JavaScript/TypeScript)
```javascript
fetch('http://localhost:8000/health')
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 2. Chat - Tạo Session Mới (Lần đầu)

### Windows PowerShell
```powershell
$body = @{
    message = "I have a headache"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method POST -Body $body -ContentType "application/json"
$response | ConvertTo-Json

# Lưu session_id
$sessionId = $response.session_id
Write-Host "Session ID: $sessionId"
```

### Windows CMD (với curl)
```cmd
curl -X POST "http://localhost:8000/chat" ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"I have a headache\"}"
```

### Mobile App Test (JavaScript/TypeScript)
```javascript
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'I have a headache'
  })
});

const data = await response.json();
console.log('Response:', data);
console.log('Session ID:', data.session_id);

// Lưu session_id để dùng sau
const sessionId = data.session_id;
```

---

## 3. Chat - Tiếp tục với Session ID

### Windows PowerShell
```powershell
# Thay YOUR_SESSION_ID bằng session_id từ bước trước
$sessionId = "YOUR_SESSION_ID"

$body = @{
    message = "What should I do?"
    session_id = $sessionId
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method POST -Body $body -ContentType "application/json" | ConvertTo-Json
```

### Windows CMD (với curl)
```cmd
curl -X POST "http://localhost:8000/chat" ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"What should I do?\", \"session_id\": \"YOUR_SESSION_ID\"}"
```

### Mobile App Test (JavaScript/TypeScript)
```javascript
// Dùng session_id đã lưu từ bước trước
const sessionId = 'YOUR_SESSION_ID';

const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'What should I do?',
    session_id: sessionId
  })
});

const data = await response.json();
console.log('Response:', data);
```

---

## 4. Lấy Chat History

### Windows PowerShell
```powershell
# Thay YOUR_SESSION_ID bằng session_id của bạn
$sessionId = "YOUR_SESSION_ID"

Invoke-RestMethod -Uri "http://localhost:8000/chat/history/$sessionId?limit=50" -Method GET | ConvertTo-Json
```

### Windows CMD (với curl)
```cmd
curl "http://localhost:8000/chat/history/YOUR_SESSION_ID?limit=50"
```

### Mobile App Test (JavaScript/TypeScript)
```javascript
const sessionId = 'YOUR_SESSION_ID';

const response = await fetch(
  `http://localhost:8000/chat/history/${sessionId}?limit=50`
);
const history = await response.json();

console.log('History:', history);
console.log('Message count:', history.count);

// Hiển thị messages
history.messages.forEach((msg, index) => {
  console.log(`${index + 1}. User: ${msg.user}`);
  console.log(`   Assistant: ${msg.assistant}`);
});
```

---

## 5. List Tất cả Sessions

### Windows PowerShell
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/chat/sessions?limit=20" -Method GET | ConvertTo-Json
```

### Windows CMD (với curl)
```cmd
curl "http://localhost:8000/chat/sessions?limit=20"
```

### Mobile App Test (JavaScript/TypeScript)
```javascript
const response = await fetch('http://localhost:8000/chat/sessions?limit=20');
const sessions = await response.json();

console.log('Total sessions:', sessions.count);
sessions.sessions.forEach(session => {
  console.log(`Session: ${session.session_id}`);
  console.log(`  Last message: ${session.last_message_at}`);
  console.log(`  Message count: ${session.message_count}`);
});
```

---

## 6. Xóa Chat History

### Windows PowerShell
```powershell
# Thay YOUR_SESSION_ID bằng session_id cần xóa
$sessionId = "YOUR_SESSION_ID"

Invoke-RestMethod -Uri "http://localhost:8000/chat/history/$sessionId" -Method DELETE | ConvertTo-Json
```

### Windows CMD (với curl)
```cmd
curl -X DELETE "http://localhost:8000/chat/history/YOUR_SESSION_ID"
```

### Mobile App Test (JavaScript/TypeScript)
```javascript
const sessionId = 'YOUR_SESSION_ID';

const response = await fetch(
  `http://localhost:8000/chat/history/${sessionId}`,
  { method: 'DELETE' }
);

const result = await response.json();
console.log('Deleted:', result.deleted_count, 'messages');
```

---

## 7. Summarization Endpoint

### Windows PowerShell
```powershell
$body = @{
    text = "Your long medical text here that needs to be summarized..."
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/summarize" -Method POST -Body $body -ContentType "application/json" | ConvertTo-Json
```

### Windows CMD (với curl)
```cmd
curl -X POST "http://localhost:8000/summarize" ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"Your long medical text here...\"}"
```

### Mobile App Test (JavaScript/TypeScript)
```javascript
const response = await fetch('http://localhost:8000/summarize', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: 'Your long medical text here that needs to be summarized...'
  })
});

const data = await response.json();
console.log('Summary:', data.summary);
```

---

## Complete Test Flow (Từ đầu đến cuối)

### Windows PowerShell Script
```powershell
# 1. Health Check
Write-Host "1. Health Check..."
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET | ConvertTo-Json

# 2. Tạo session mới
Write-Host "`n2. Creating new chat session..."
$chatBody = @{
    message = "I have a headache and fever"
} | ConvertTo-Json

$chatResponse = Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method POST -Body $chatBody -ContentType "application/json"
$sessionId = $chatResponse.session_id
Write-Host "Session ID: $sessionId"
$chatResponse | ConvertTo-Json

# 3. Chat tiếp với session_id
Write-Host "`n3. Continuing chat with session ID..."
$continueBody = @{
    message = "What should I do?"
    session_id = $sessionId
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method POST -Body $continueBody -ContentType "application/json" | ConvertTo-Json

# 4. Lấy history
Write-Host "`n4. Getting chat history..."
Invoke-RestMethod -Uri "http://localhost:8000/chat/history/$sessionId" -Method GET | ConvertTo-Json

# 5. List sessions
Write-Host "`n5. Listing all sessions..."
Invoke-RestMethod -Uri "http://localhost:8000/chat/sessions?limit=10" -Method GET | ConvertTo-Json
```

### Complete JavaScript/TypeScript Test
```javascript
async function testAPI() {
  const baseURL = 'http://localhost:8000';
  
  // 1. Health Check
  console.log('1. Health Check...');
  const health = await fetch(`${baseURL}/health`).then(r => r.json());
  console.log(health);
  
  // 2. Tạo session mới
  console.log('\n2. Creating new chat session...');
  const chat1 = await fetch(`${baseURL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'I have a headache and fever' })
  }).then(r => r.json());
  
  const sessionId = chat1.session_id;
  console.log('Session ID:', sessionId);
  console.log('Response:', chat1.response);
  
  // 3. Chat tiếp với session_id
  console.log('\n3. Continuing chat...');
  const chat2 = await fetch(`${baseURL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: 'What should I do?',
      session_id: sessionId
    })
  }).then(r => r.json());
  console.log('Response:', chat2.response);
  
  // 4. Lấy history
  console.log('\n4. Getting chat history...');
  const history = await fetch(`${baseURL}/chat/history/${sessionId}`).then(r => r.json());
  console.log('History count:', history.count);
  history.messages.forEach((msg, i) => {
    console.log(`${i + 1}. User: ${msg.user}`);
    console.log(`   Assistant: ${msg.assistant}`);
  });
  
  // 5. List sessions
  console.log('\n5. Listing sessions...');
  const sessions = await fetch(`${baseURL}/chat/sessions?limit=10`).then(r => r.json());
  console.log('Total sessions:', sessions.count);
}

// Chạy test
testAPI().catch(console.error);
```

---

## Lưu ý

### Đổi URL cho Production
Nếu server chạy ở server khác (không phải localhost), thay `http://localhost:8000` bằng URL của server:

```javascript
const baseURL = 'https://your-server.com';  // Thay URL này
```

### Cài đặt curl trên Windows (nếu chưa có)
- Windows 10/11: curl đã có sẵn
- Hoặc download từ: https://curl.se/windows/

### Test với Postman
Bạn cũng có thể import các requests này vào Postman để test dễ dàng hơn.

---

## Quick Reference

| Action | Endpoint | Method | Body |
|--------|----------|--------|------|
| Health Check | `/health` | GET | - |
| Chat (new) | `/chat` | POST | `{message: "..."}` |
| Chat (continue) | `/chat` | POST | `{message: "...", session_id: "..."}` |
| Get History | `/chat/history/{session_id}` | GET | - |
| List Sessions | `/chat/sessions` | GET | - |
| Delete History | `/chat/history/{session_id}` | DELETE | - |
| Summarize | `/summarize` | POST | `{text: "..."}` |

---

Copy các lệnh này và chạy từ Windows Cursor hoặc mobile app project để test API! 🚀

