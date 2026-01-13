# Hướng dẫn Setup Server

Hướng dẫn chi tiết từng bước để setup và chạy server API.

## 📋 Mục lục

1. [Cài đặt Python và Virtual Environment](#1-cài-đặt-python-và-virtual-environment)
2. [Cài đặt Dependencies](#2-cài-đặt-dependencies)
3. [Cấu hình Environment Variables](#3-cấu-hình-environment-variables)
4. [Thay đổi API Key trong .env](#4-thay-đổi-api-key-trong-env)
5. [Chạy Server](#5-chạy-server)
6. [Kiểm tra Server](#6-kiểm-tra-server)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Cài đặt Python và Virtual Environment

### Bước 1.1: Kiểm tra Python version
```bash
python3 --version
# Hoặc
python --version
```
**Yêu cầu:** Python 3.8 trở lên

### Bước 1.2: Tạo Virtual Environment
```bash
# Di chuyển vào thư mục dự án
cd /path/to/sumarization-api

# Tạo virtual environment
python3 -m venv venv
# Hoặc
python -m venv venv
```

### Bước 1.3: Kích hoạt Virtual Environment

**Trên macOS/Linux:**
```bash
source venv/bin/activate
```

**Trên Windows:**
```bash
venv\Scripts\activate
```

Sau khi kích hoạt, bạn sẽ thấy `(venv)` ở đầu dòng lệnh.

---

## 2. Cài đặt Dependencies

### Bước 2.1: Cài đặt packages từ requirements.txt
```bash
pip install -r requirements.txt
```

### Bước 2.2: Kiểm tra cài đặt
```bash
pip list
```

**Các package quan trọng cần có:**
- fastapi
- uvicorn
- transformers
- torch
- google-generativeai
- python-dotenv

---

## 3. Cấu hình Environment Variables

### Bước 3.1: Tạo file .env

Tạo file `.env` trong thư mục gốc của dự án (cùng cấp với `main.py`):

```bash
touch .env
```

### Bước 3.2: Thêm các biến môi trường vào .env

Mở file `.env` và thêm các dòng sau:

```env
# Google Gemini API Key (Bắt buộc cho chatbot)
GEMINI_API_KEY=your_gemini_api_key_here

# Gemini Model (Tùy chọn, mặc định: models/gemini-2.5-flash)
# Các options: models/gemini-2.5-flash, models/gemini-2.5-pro, models/gemini-flash-latest
GEMINI_MODEL=models/gemini-2.5-flash
```

**Lưu ý:** 
- Thay `your_gemini_api_key_here` bằng API key thực tế của bạn
- Không có khoảng trắng xung quanh dấu `=`
- Không cần dấu ngoặc kép cho giá trị

---

## 4. Thay đổi API Key trong .env

### Bước 4.1: Mở file .env

**Cách 1: Sử dụng text editor**
```bash
# macOS/Linux
nano .env
# hoặc
vim .env
# hoặc
code .env  # Nếu có VS Code

# Windows
notepad .env
```

**Cách 2: Sử dụng IDE**
- Mở file `.env` trong VS Code, PyCharm, hoặc IDE yêu thích của bạn

### Bước 4.2: Cập nhật API Key

Tìm dòng:
```env
GEMINI_API_KEY=old_api_key_here
```

Thay bằng:
```env
GEMINI_API_KEY=new_api_key_here
```

### Bước 4.3: Lưu file

- **Nano:** Nhấn `Ctrl + X`, sau đó `Y`, rồi `Enter`
- **Vim:** Nhấn `Esc`, gõ `:wq`, rồi `Enter`
- **VS Code/IDE:** Nhấn `Ctrl + S` (hoặc `Cmd + S` trên Mac)

### Bước 4.4: Restart Server

**Quan trọng:** Sau khi thay đổi `.env`, bạn **PHẢI** restart server để áp dụng thay đổi:

1. Dừng server hiện tại (nhấn `Ctrl + C` trong terminal đang chạy server)
2. Chạy lại server (xem phần 5)

---

## 5. Chạy Server

### Bước 5.1: Đảm bảo Virtual Environment đã được kích hoạt

Kiểm tra xem có `(venv)` ở đầu dòng lệnh:
```bash
(venv) user@computer:~/sumarization-api$
```

Nếu chưa có, kích hoạt lại:
```bash
source venv/bin/activate  # macOS/Linux
# hoặc
venv\Scripts\activate  # Windows
```

### Bước 5.2: Chạy Server

**Cách 1: Sử dụng uvicorn trực tiếp**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Cách 2: Sử dụng Python**
```bash
python main.py
```

**Cách 3: Sử dụng gunicorn (Production)**
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Bước 5.3: Kiểm tra Server đã chạy

Bạn sẽ thấy output tương tự:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 6. Kiểm tra Server

### Bước 6.1: Kiểm tra Health Endpoint

Mở trình duyệt hoặc dùng curl:

```bash
# Trong terminal mới
curl http://localhost:8000/health
```

Hoặc mở trình duyệt: `http://localhost:8000/health`

**Kết quả mong đợi:**
```json
{
  "status": "healthy",
  "services": ["summarization", "chatbot", "chat_history"]
}
```

### Bước 6.2: Kiểm tra API Documentation

Mở trình duyệt:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Bước 6.3: Test Summarization API

```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your long text here to summarize..."}'
```

### Bước 6.4: Test Chatbot API

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the symptoms of flu?"}'
```

---

## 7. Troubleshooting

### Lỗi: ModuleNotFoundError

**Nguyên nhân:** Chưa cài đặt dependencies hoặc chưa kích hoạt virtual environment

**Giải pháp:**
```bash
# Kích hoạt venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows

# Cài đặt lại dependencies
pip install -r requirements.txt
```

### Lỗi: GEMINI_API_KEY not configured

**Nguyên nhân:** 
- Chưa tạo file `.env`
- API key chưa được set trong `.env`
- Server chưa được restart sau khi thay đổi `.env`

**Giải pháp:**
1. Kiểm tra file `.env` có tồn tại không
2. Kiểm tra `GEMINI_API_KEY` có trong `.env` không
3. Restart server

### Lỗi: Port 8000 already in use

**Nguyên nhân:** Port 8000 đang được sử dụng bởi process khác

**Giải pháp 1: Tìm và kill process**
```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Giải pháp 2: Dùng port khác**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Lỗi: Model not found

**Nguyên nhân:** Model chưa được download

**Giải pháp:**
- Model sẽ tự động download khi chạy lần đầu
- Đảm bảo có kết nối internet
- Kiểm tra dung lượng ổ cứng (model khá lớn)

### Server không reload sau khi sửa code

**Nguyên nhân:** Chưa dùng flag `--reload`

**Giải pháp:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📝 Quick Reference

### Các lệnh thường dùng

```bash
# Kích hoạt venv
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy server (development)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Chạy server (production)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Kiểm tra health
curl http://localhost:8000/health

# Xem API docs
# Mở trình duyệt: http://localhost:8000/docs
```

### Cấu trúc file .env

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=models/gemini-2.5-flash
```

---

## 🔄 Quy trình thay đổi API Key

1. **Dừng server** (Ctrl + C)
2. **Mở file .env** và cập nhật `GEMINI_API_KEY`
3. **Lưu file .env**
4. **Chạy lại server**
5. **Test lại API** để đảm bảo hoạt động

---

## 📞 Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
- File `.env` có đúng format không
- Virtual environment đã được kích hoạt chưa
- Dependencies đã được cài đặt đầy đủ chưa
- Server logs để xem lỗi chi tiết

