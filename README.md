# Scrapy Crawler cho Báo Tin Tức - Pháp Luật

Dự án này sử dụng Scrapy để crawl dữ liệu bài viết pháp luật mới nhất trong ngày từ trang web [baotintuc.vn](https://baotintuc.vn/phap-luat-475ct0.htm).

## Cấu trúc dự án

```
CrawWeb/
├── requirements.txt          # Dependencies
├── scrapy.cfg               # Cấu hình Scrapy
├── README.md               # Hướng dẫn sử dụng
├── baotintuc/              # Package chính
│   ├── __init__.py
│   ├── items.py            # Định nghĩa cấu trúc dữ liệu
│   ├── settings.py         # Cấu hình Scrapy
│   ├── pipelines.py        # Xử lý và lưu dữ liệu
│   └── spiders/            # Thư mục chứa spiders
│       ├── __init__.py
│       └── phap_luat.py    # Spider chính
├── output/                 # Thư mục chứa kết quả (tự động tạo)
│   ├── images/             # Thư mục chứa ảnh đã tải
│   └── articles/           # Thư mục chứa bài viết HTML
├── run_spider.py           # Script chạy spider
├── test_spider.py          # Script test spider
├── test_page_structure.py  # Script test cấu trúc HTML
└── download_images.py      # Script tải ảnh
```

## Cài đặt

1. Cài đặt Python 3.7+ nếu chưa có
2. Cài đặt các dependencies:

```bash
pip install -r requirements.txt
```

## Sử dụng

### Chạy spider

```bash
python run_spider.py
```

### Tải ảnh (tùy chọn)

Sau khi crawl xong, có thể tải ảnh từ các bài viết:

```bash
python download_images.py
```

### Kết quả

Dữ liệu sẽ được lưu vào file JSON trong thư mục `output/` với format:

```json
[
  {
    "topic": "Pháp luật",
    "title": "Tiêu đề bài viết pháp luật",
    "summary": "Tóm tắt bài viết...",
    "content": "Nội dung đầy đủ...",
    "url": "https://baotintuc.vn/phap-luat/...",
    "source": "baotintuc.vn",
    "date": "2025-07-13T12:00:00+07:00",
    "images": [
      {
        "url": "https://baotintuc.vn/images/...",
        "alt": "Mô tả ảnh",
        "filename": "mo-ta-anh_abc123.jpg",
        "local_path": "output/images/mo-ta-anh_abc123.jpg"
      }
    ],
    "article_file": "tieu-de-bai-viet_abc123.html"
  }
]
```

## Tính năng

- **Lọc theo ngày**: Chỉ lấy bài viết được đăng trong ngày hôm nay
- **Xử lý đa dạng format ngày**: Hỗ trợ nhiều format ngày tháng khác nhau
- **Lưu tự động**: Tự động tạo file JSON với timestamp
- **Encoding UTF-8**: Hỗ trợ tiếng Việt đầy đủ
- **Rate limiting**: Tránh gây tải cho server
- **Tải ảnh**: Tự động phát hiện và lưu thông tin ảnh trong bài viết
- **Lưu bài viết HTML**: Lưu toàn bộ bài viết dưới dạng file HTML
- **Tải ảnh offline**: Script riêng để tải ảnh về máy

## Cấu hình

Có thể điều chỉnh các thông số trong `baotintuc/settings.py`:

- `DOWNLOAD_DELAY`: Thời gian delay giữa các request
- `CONCURRENT_REQUESTS_PER_DOMAIN`: Số request đồng thời
- `DEFAULT_REQUEST_HEADERS`: Headers cho request

## Lưu ý

- Spider tuân thủ robots.txt
- Có delay giữa các request để tránh gây tải cho server
- Chỉ crawl bài viết pháp luật trong ngày hôm nay
- Dữ liệu được lưu với encoding UTF-8 để hỗ trợ tiếng Việt 