# Hướng dẫn lấy code từ Kaggle Notebook

## Cách 1: Copy code trực tiếp từ Kaggle

1. Truy cập: https://www.kaggle.com/code/abbasyed/abbas-syed-medical-chatbot
2. Click vào nút **"Copy & Edit"** hoặc **"..."** → **"Copy"**
3. Copy toàn bộ code từ notebook
4. Paste vào file `notebook_code.py` trong thư mục này
5. Chạy: `python analyze_notebook.py`

## Cách 2: Download notebook file

1. Trên trang Kaggle notebook, click **"..."** → **"Download"**
2. Giải nén file `.ipynb`
3. Convert `.ipynb` sang `.py` hoặc copy code cells vào `notebook_code.py`

## Cách 3: Sử dụng Kaggle API (Cần credentials)

```bash
# Cài đặt Kaggle API credentials trước
kaggle kernels pull abbasyed/abbas-syed-medical-chatbot -p .
```

Sau khi có code, chạy script phân tích để tìm model name!

