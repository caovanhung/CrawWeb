#!/usr/bin/env python3
"""
Script để test cấu trúc HTML của trang baotintuc.vn
"""

import requests
from bs4 import BeautifulSoup
import json
import urllib3
import ssl

# Tắt cảnh báo SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Tạo SSL context tùy chỉnh
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def test_page_structure():
    """Test cấu trúc HTML của trang pháp luật"""
    
    # Thử cả HTTP và HTTPS
    urls_to_try = [
        "http://baotintuc.vn/phap-luat-475ct0.htm",
        "https://baotintuc.vn/phap-luat-475ct0.htm"
    ]
    
    for url in urls_to_try:
        print(f"🔄 Thử URL: {url}")
        if test_single_url(url):
            break
    else:
        print("❌ Không thể kết nối với bất kỳ URL nào")

def test_single_url(url):
    """Test một URL cụ thể"""
    
    print("=" * 60)
    print("TEST CẤU TRÚC HTML - BAOTINTUC.VN")
    print("=" * 60)
    print(f"URL: {url}")
    print()
    
    try:
        # Headers để giả lập browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'vi,en;q=0.8',
        }
        
        # Gửi request
        print("📡 Đang gửi request...")
        session = requests.Session()
        session.verify = False
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"✅ Status code: {response.status_code}")
        print(f"📄 Content length: {len(response.text)} bytes")
        print()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm các selector có thể chứa bài viết
        selectors_to_test = [
            'div.list-news article',
            'div.list-news .item-news',
            '.list-news .item',
            '.news-list .item',
            'article',
            '.item-news',
            '.news-item',
            '.article-item'
        ]
        
        print("🔍 Tìm kiếm bài viết với các selector:")
        for selector in selectors_to_test:
            elements = soup.select(selector)
            print(f"   {selector}: {len(elements)} elements")
        
        print()
        
        # Test lấy link bài viết
        print("🔗 Test lấy link bài viết:")
        link_selectors = [
            'a[href*="/phap-luat/"]',
            'article a',
            '.item-news a',
            '.news-item a'
        ]
        
        for selector in link_selectors:
            links = soup.select(selector)
            print(f"   {selector}: {len(links)} links")
            if links:
                for i, link in enumerate(links[:3]):  # Chỉ hiển thị 3 link đầu
                    href = link.get('href')
                    text = link.get_text(strip=True)[:50]
                    print(f"     {i+1}. {href} - {text}...")
        
        print()
        
        # Test lấy title
        print("📝 Test lấy title:")
        title_selectors = [
            'h3 a',
            'h2 a',
            '.title a',
            'a'
        ]
        
        for selector in title_selectors:
            titles = soup.select(selector)
            print(f"   {selector}: {len(titles)} titles")
            if titles:
                for i, title in enumerate(titles[:3]):
                    text = title.get_text(strip=True)[:50]
                    print(f"     {i+1}. {text}...")
        
        print()
        
        # Test lấy ngày tháng
        print("📅 Test lấy ngày tháng:")
        date_selectors = [
            '.time',
            '.date',
            '.datetime',
            'time',
            '.news-time'
        ]
        
        for selector in date_selectors:
            dates = soup.select(selector)
            print(f"   {selector}: {len(dates)} dates")
            if dates:
                for i, date in enumerate(dates[:3]):
                    text = date.get_text(strip=True)
                    print(f"     {i+1}. {text}")
        
        print()
        
        # Lưu HTML để debug
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("💾 Đã lưu HTML vào file debug_page.html")
        
        return True
        
    except requests.RequestException as e:
        print(f"❌ Lỗi request: {e}")
        return False
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False
    
    print("=" * 60)
    return True

if __name__ == "__main__":
    test_page_structure() 