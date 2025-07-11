# Hệ thống Backend cho chatbot
## Hướng dẫn cài đặt
### Bước 1: Clone repository
```bash
git https://github.com/PhamVanHung412004/Build-a-website-with-integrated-AI-Chatbot-technology-to-ask-and-answer-questions-about-the-school.git
cd Build-a-website-with-integrated-AI-Chatbot-technology-to-ask-and-answer-questions-about-the-school
```

### Bước 2: Cài đặt các package cần thiết
```bash
# Tạo môi trường với conda (yêu cầu Miniconda or Anaconda)
conda create -n tên_môi_trường python=3.10
```
```bash
# Tạo môi trường với conda (yêu cầu Miniconda or Anaconda)
conda activate tên_môi_trường
```
```bash
# Cài đặt các thư viện từ requirements.txt
pip install -r requirements.txt
```

### Bước 3: Setup API Key của model gen text Gemini

Bạn hãy tạo tài khoản gemini rồi tạo API KEY rồi dán vào câu lệnh dưới trên Command Prompt vào trang web sau để tạo tài khoản: https://aistudio.google.com/
```bash
set GEMINI_API_KEY="Thay bằng API KEY của bạn"
```

### Bước 4: Mở sever
```bash
# Khởi dộng server với Flask
python main.py
```

### Bước 5: Test API
```bash
python test_api.py
sau khi chạy xong màn hình Command Prompt sẽ hiện ra để bạn nhập câu hỏi.
```
