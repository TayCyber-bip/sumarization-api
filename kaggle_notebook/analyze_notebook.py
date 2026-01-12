"""
Script để phân tích Kaggle notebook và tìm model name
Paste code từ Kaggle notebook vào file notebook_code.py và chạy script này
"""

import re
import sys

def find_model_name(code):
    """Tìm model name từ code"""
    patterns = [
        r'from_pretrained\(["\']([^"\']+)["\']',
        r'\.from_pretrained\(["\']([^"\']+)["\']',
        r'model_name\s*=\s*["\']([^"\']+)["\']',
        r'MODEL_NAME\s*=\s*["\']([^"\']+)["\']',
        r'pretrained\(["\']([^"\']+)["\']',
    ]
    
    models_found = []
    for pattern in patterns:
        matches = re.findall(pattern, code, re.IGNORECASE)
        models_found.extend(matches)
    
    # Filter out common non-model strings
    filtered = [m for m in models_found if not any(x in m.lower() for x in ['cache', 'local', 'path', 'dir'])]
    
    return list(set(filtered))

def find_model_type(code):
    """Xác định loại model"""
    if 'AutoModelForCausalLM' in code or 'GPT2LMHeadModel' in code or 'GPTNeo' in code or 'DialoGPT' in code:
        return "causal"
    elif 'AutoModelForSeq2SeqLM' in code or 'T5' in code or 'BART' in code:
        return "seq2seq"
    return None

if __name__ == "__main__":
    try:
        # Đọc code từ file
        with open('notebook_code.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        print("=" * 60)
        print("PHÂN TÍCH KAGGLE NOTEBOOK")
        print("=" * 60)
        
        # Tìm model names
        models = find_model_name(code)
        if models:
            print("\n📦 CÁC MODEL ĐƯỢC TÌM THẤY:")
            for i, model in enumerate(models, 1):
                print(f"  {i}. {model}")
        else:
            print("\n⚠️  Không tìm thấy model name trong code")
        
        # Tìm model type
        model_type = find_model_type(code)
        if model_type:
            print(f"\n🔧 LOẠI MODEL: {model_type.upper()}")
        else:
            print("\n⚠️  Không xác định được loại model")
        
        print("\n" + "=" * 60)
        print("CẤU HÌNH CHO main.py:")
        print("=" * 60)
        if models:
            primary_model = models[0]
            print(f'\nCHATBOT_MODEL_NAME = "{primary_model}"')
            if model_type:
                print(f'CHATBOT_MODEL_TYPE = "{model_type}"')
            else:
                print('CHATBOT_MODEL_TYPE = "causal"  # Hoặc "seq2seq" tùy vào model')
        else:
            print("\nKhông thể tự động xác định. Vui lòng kiểm tra lại code.")
        
    except FileNotFoundError:
        print("❌ Không tìm thấy file notebook_code.py")
        print("\nHướng dẫn:")
        print("1. Copy code từ Kaggle notebook")
        print("2. Paste vào file notebook_code.py trong thư mục này")
        print("3. Chạy lại script này")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

