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

### Bước 3: Mở sever
```bash
# Khởi dộng server với Flask
python main.py
```