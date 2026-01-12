@echo off
REM API Test Script for Windows CMD
REM Chạy: test_api.bat

set BASE_URL=http://localhost:8000

echo === API Test Script ===
echo Base URL: %BASE_URL%
echo.

REM 1. Health Check
echo 1. Health Check...
curl -s %BASE_URL%/health
echo.
echo.

REM 2. Tạo session mới
echo 2. Creating new chat session...
curl -X POST "%BASE_URL%/chat" ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"I have a headache and fever\"}"
echo.
echo.

REM Note: Để test các bước tiếp theo, bạn cần copy session_id từ response trên
echo Note: Copy session_id từ response trên và thay YOUR_SESSION_ID trong script để test tiếp
echo.
pause

