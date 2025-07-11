# BTEC FPT Web Crawler

Một công cụ crawler mạnh mẽ được thiết kế đặc biệt cho website BTEC FPT (https://btec.fpt.edu.vn/), hỗ trợ thu thập toàn bộ nội dung và xuất thành file PDF.

## 🚀 Tính năng chính

- **Thu thập toàn diện**: Crawl toàn bộ website một cách có hệ thống
- **Xử lý tiếng Việt**: Hỗ trợ đầy đủ nội dung tiếng Việt và Unicode
- **Tạo PDF chất lượng cao**: Chuyển đổi từng trang web thành file PDF riêng biệt
- **Tải PDF có sẵn**: Tự động tải xuống các file PDF đã có trên website
- **Phân loại theo campus**: Tổ chức nội dung theo các campus (Hà Nội, HCM, Đà Nẵng)
- **Xử lý lỗi thông minh**: Retry tự động và ghi log chi tiết
- **Kiểm soát đồng thời**: Crawl nhiều trang cùng lúc với giới hạn có thể cấu hình
- **Loại bỏ trùng lặp**: Phát hiện và bỏ qua nội dung trùng lặp

## 📋 Yêu cầu hệ thống

- Python 3.8 trở lên
- Hệ điều hành: Windows, macOS, hoặc Linux
- RAM: Tối thiểu 4GB
- Dung lượng đĩa: Tùy thuộc vào số lượng trang cần crawl

## 🛠️ Cài đặt

### 1. Clone hoặc tải code

```bash
# Tạo thư mục dự án
mkdir btec_crawler
cd btec_crawler

# Copy file btec_crawler.py vào thư mục này
```

### 2. Tạo môi trường ảo (khuyến nghị)

```bash
conda create -n ten_moi_truong python=3.10
conda activate ten_moi_truong
```

### 3. Cài đặt dependencies

Tạo file `requirements.txt` với nội dung sau:

```txt
aiohttp>=3.8.0
asyncio>=3.4.3
beautifulsoup4>=4.12.0
weasyprint>=60.0
playwright>=1.40.0
tenacity>=8.2.0
requests>=2.31.0
lxml>=4.9.0
Pillow>=10.0.0
pdfkit>=1.0.0
urllib3>=2.0.0
```

Sau đó cài đặt:

```bash
pip install -r requirements.txt
```

### 4. Cài đặt Playwright browsers (nếu sử dụng Playwright engine)

```bash
playwright install chromium
```

### 5. Cài đặt wkhtmltopdf (nếu sử dụng pdfkit engine)

- **Windows**: Tải từ https://wkhtmltopdf.org/downloads.html
- **macOS**: `brew install wkhtmltopdf`
- **Linux**: `sudo apt-get install wkhtmltopdf`

## 🚦 Cách sử dụng

### Sử dụng cơ bản

```python
import asyncio
from btec_crawler import BTECCrawler

async def main():
    # Sử dụng cấu hình mặc định
    async with BTECCrawler() as crawler:
        report = await crawler.crawl_website()
        print(f"Đã crawl {report['summary']['total_pages_crawled']} trang")

if __name__ == "__main__":
    asyncio.run(main())
```

### Sử dụng với cấu hình tùy chỉnh

```python
import asyncio
from btec_crawler import BTECCrawler

async def main():
    config = {
        'max_concurrent_requests': 5,  # Số request đồng thời
        'delay_between_requests': 2.0,  # Delay giữa các request (giây)
        'output_dir': './my_output',    # Thư mục lưu kết quả
        'pdf_engine': 'weasyprint',     # Engine tạo PDF
        'max_depth': 10,                # Độ sâu crawl tối đa
        'download_existing_pdfs': True  # Tải PDF có sẵn
    }
    
    async with BTECCrawler(config) as crawler:
        report = await crawler.crawl_website()

if __name__ == "__main__":
    asyncio.run(main())
```

### Crawl các URL cụ thể

```python
async def main():
    seed_urls = [
        'https://btec.fpt.edu.vn/courses',
        'https://btec.fpt.edu.vn/btec-hanoi',
        'https://btec.fpt.edu.vn/admissions'
    ]
    
    async with BTECCrawler() as crawler:
        report = await crawler.crawl_website(seed_urls)
```

## ⚙️ Cấu hình chi tiết

### Các tùy chọn cấu hình

| Tùy chọn | Mô tả | Giá trị mặc định |
|----------|-------|------------------|
| `base_url` | URL gốc của website | `https://btec.fpt.edu.vn/` |
| `max_concurrent_requests` | Số request đồng thời tối đa | `5` |
| `delay_between_requests` | Thời gian chờ giữa các request (giây) | `1.0` |
| `max_retries` | Số lần thử lại khi gặp lỗi | `3` |
| `timeout` | Timeout cho mỗi request (giây) | `30` |
| `max_depth` | Độ sâu crawl tối đa | `10` |
| `output_dir` | Thư mục lưu kết quả | `./btec_crawl_output` |
| `pdf_engine` | Engine tạo PDF (`weasyprint`, `playwright`) | `weasyprint` |
| `include_images` | Bao gồm hình ảnh trong PDF | `True` |
| `download_existing_pdfs` | Tải xuống file PDF có sẵn | `True` |
| `respect_robots_txt` | Tuân thủ robots.txt | `True` |

### Ví dụ file cấu hình JSON

Tạo file `config.json`:

```json
{
  "base_url": "https://btec.fpt.edu.vn/",
  "max_concurrent_requests": 3,
  "delay_between_requests": 2.0,
  "max_retries": 3,
  "timeout": 30,
  "max_depth": 8,
  "output_dir": "./btec_output",
  "pdf_engine": "weasyprint",
  "download_existing_pdfs": true,
  "pdf_options": {
    "page_size": "A4",
    "margin": "1in",
    "orientation": "Portrait"
  }
}
```

Sử dụng với file config:

```python
import json

with open('config.json', 'r') as f:
    config = json.load(f)

async with BTECCrawler(config) as crawler:
    report = await crawler.crawl_website()
```

## 📁 Cấu trúc thư mục output

```
btec_crawl_output/
├── pages_pdf/              # PDF được tạo từ các trang web
├── downloaded_pdfs/        # PDF được tải xuống
├── campus_hanoi/          # Nội dung campus Hà Nội
├── campus_hcm/            # Nội dung campus HCM
├── campus_danang/         # Nội dung campus Đà Nẵng
├── reports/               # Báo cáo crawl
│   └── crawl_report_*.json
└── logs/                  # Log file
    └── btec_crawler.log
```

## 📊 Báo cáo kết quả

Sau khi crawl xong, tool sẽ tạo báo cáo JSON với các thông tin:

- Tổng số trang đã crawl
- Số PDF đã tạo
- Số PDF đã tải xuống
- Số lỗi gặp phải
- Thống kê theo campus
- Danh sách URL lỗi (nếu có)
- Thời gian thực hiện

## 🔧 Xử lý lỗi thường gặp

### 1. Lỗi cài đặt WeasyPrint

```bash
# Ubuntu/Debian
sudo apt-get install python3-pip python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0

# macOS
brew install cairo pango gdk-pixbuf libffi
```

### 2. Lỗi SSL Certificate

Thêm vào config:
```python
config = {
    'verify_ssl': False  # Chỉ dùng khi cần thiết
}
```

### 3. Memory Error với website lớn

Giảm concurrent requests và tăng delay:
```python
config = {
    'max_concurrent_requests': 2,
    'delay_between_requests': 3.0
}
```

## 🚨 Lưu ý quan trọng

1. **Tôn trọng server**: Không đặt `max_concurrent_requests` quá cao
2. **Kiểm tra robots.txt**: Tool mặc định tuân thủ robots.txt
3. **Backup định kỳ**: Với crawl lớn, nên backup kết quả định kỳ
4. **Monitor resources**: Theo dõi CPU và RAM khi crawl
5. **Test nhỏ trước**: Thử với một vài URL trước khi crawl toàn bộ

## 🤝 Đóng góp

Nếu bạn muốn đóng góp hoặc báo lỗi, vui lòng:

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📝 License

Dự án này được phát hành cho mục đích giáo dục. Vui lòng tuân thủ điều khoản sử dụng của website khi sử dụng tool này.

## 📞 Hỗ trợ

Nếu gặp vấn đề khi sử dụng, bạn có thể:

1. Kiểm tra file log trong thư mục `logs/`
2. Xem lại cấu hình
3. Đảm bảo đã cài đặt đủ dependencies
4. Thử với cấu hình mặc định trước

---

Made with ❤️ for BTEC FPT students and staff