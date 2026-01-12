# API Test Script for Windows PowerShell
# Chạy script này để test tất cả endpoints

$baseURL = "http://localhost:8000"

Write-Host "=== API Test Script ===" -ForegroundColor Green
Write-Host "Base URL: $baseURL`n" -ForegroundColor Cyan

# 1. Health Check
Write-Host "1. Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseURL/health" -Method GET
    Write-Host "Status: $($health.status)" -ForegroundColor Green
    Write-Host "Services: $($health.services -join ', ')" -ForegroundColor Green
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit
}

Write-Host ""

# 2. Tạo session mới - Chat lần đầu
Write-Host "2. Creating new chat session..." -ForegroundColor Yellow
$chatBody1 = @{
    message = "I have a headache and fever"
} | ConvertTo-Json

try {
    $chatResponse1 = Invoke-RestMethod -Uri "$baseURL/chat" -Method POST -Body $chatBody1 -ContentType "application/json"
    $sessionId = $chatResponse1.session_id
    Write-Host "Session ID: $sessionId" -ForegroundColor Cyan
    Write-Host "User: $($chatResponse1.message)" -ForegroundColor White
    Write-Host "Assistant: $($chatResponse1.response)" -ForegroundColor Green
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit
}

Write-Host ""

# 3. Chat tiếp với session_id
Write-Host "3. Continuing chat with session ID..." -ForegroundColor Yellow
$chatBody2 = @{
    message = "What should I do?"
    session_id = $sessionId
} | ConvertTo-Json

try {
    $chatResponse2 = Invoke-RestMethod -Uri "$baseURL/chat" -Method POST -Body $chatBody2 -ContentType "application/json"
    Write-Host "User: $($chatResponse2.message)" -ForegroundColor White
    Write-Host "Assistant: $($chatResponse2.response)" -ForegroundColor Green
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host ""

# 4. Lấy chat history
Write-Host "4. Getting chat history..." -ForegroundColor Yellow
try {
    $history = Invoke-RestMethod -Uri "$baseURL/chat/history/$sessionId?limit=50" -Method GET
    Write-Host "Session ID: $($history.session_id)" -ForegroundColor Cyan
    Write-Host "Message count: $($history.count)" -ForegroundColor Green
    Write-Host "Messages:" -ForegroundColor Yellow
    for ($i = 0; $i -lt $history.messages.Count; $i++) {
        $msg = $history.messages[$i]
        Write-Host "  [$($i+1)] User: $($msg.user)" -ForegroundColor White
        Write-Host "      Assistant: $($msg.assistant)" -ForegroundColor Green
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host ""

# 5. List sessions
Write-Host "5. Listing all sessions..." -ForegroundColor Yellow
try {
    $sessions = Invoke-RestMethod -Uri "$baseURL/chat/sessions?limit=10" -Method GET
    Write-Host "Total sessions: $($sessions.count)" -ForegroundColor Green
    foreach ($session in $sessions.sessions) {
        Write-Host "  Session: $($session.session_id)" -ForegroundColor Cyan
        Write-Host "    Last message: $($session.last_message_at)" -ForegroundColor White
        Write-Host "    Message count: $($session.message_count)" -ForegroundColor White
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Green
Write-Host "Session ID để test tiếp: $sessionId" -ForegroundColor Cyan

