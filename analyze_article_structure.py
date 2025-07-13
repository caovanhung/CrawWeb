import json
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import time
import urllib3
import ssl

# Tắt cảnh báo SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Tạo SSL context cho legacy renegotiation
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
# Thêm option legacy renegotiation nếu có
try:
    ssl_context.options |= ssl.OP_LEGACY_SERVER_CONNECT
except AttributeError:
    # Fallback cho Python cũ hơn
    pass

def analyze_article_structure():
    """Phân tích cấu trúc HTML của các trang chi tiết bài viết"""
    
    # Đọc file JSON để lấy URLs của các bài viết
    try:
        with open('output/articles.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
    except FileNotFoundError:
        print("Không tìm thấy file output/articles.json")
        return
    
    if not articles:
        print("Không có bài viết nào trong file JSON")
        return
    
    print(f"Tìm thấy {len(articles)} bài viết để phân tích")
    
    # Phân tích 3 bài viết đầu tiên
    for i, article in enumerate(articles[:3]):
        print(f"\n{'='*60}")
        print(f"PHÂN TÍCH BÀI VIẾT {i+1}: {article['title'][:50]}...")
        print(f"URL: {article['url']}")
        print(f"{'='*60}")
        
        try:
            # Gửi request với headers giống spider
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(article['url'], headers=headers, timeout=30, verify=False, ssl_context=ssl_context)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Phân tích các selector quan trọng
            print("\n1. PHÂN TÍCH TITLE:")
            title_selectors = [
                'h1',
                '.title',
                '.article-title',
                '.post-title',
                '.entry-title',
                'h1.title',
                '.content h1',
                '.article h1'
            ]
            
            for selector in title_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"  {selector}: {len(elements)} elements found")
                    for j, elem in enumerate(elements[:2]):  # Chỉ hiển thị 2 phần tử đầu
                        text = elem.get_text(strip=True)
                        if text:
                            print(f"    [{j+1}] {text[:100]}...")
                else:
                    print(f"  {selector}: Không tìm thấy")
            
            print("\n2. PHÂN TÍCH SUMMARY/DESCRIPTION:")
            summary_selectors = [
                '.summary',
                '.description',
                '.excerpt',
                '.sapo',
                '.lead',
                '.intro',
                '.article-summary',
                '.post-excerpt',
                '.entry-summary'
            ]
            
            for selector in summary_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"  {selector}: {len(elements)} elements found")
                    for j, elem in enumerate(elements[:2]):
                        text = elem.get_text(strip=True)
                        if text:
                            print(f"    [{j+1}] {text[:100]}...")
                else:
                    print(f"  {selector}: Không tìm thấy")
            
            print("\n3. PHÂN TÍCH CONTENT:")
            content_selectors = [
                '.content',
                '.article-content',
                '.post-content',
                '.entry-content',
                '.article-body',
                '.post-body',
                '.main-content',
                '.content-area',
                '.article-text'
            ]
            
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"  {selector}: {len(elements)} elements found")
                    for j, elem in enumerate(elements[:2]):
                        text = elem.get_text(strip=True)
                        if text:
                            print(f"    [{j+1}] {text[:100]}...")
                else:
                    print(f"  {selector}: Không tìm thấy")
            
            print("\n4. PHÂN TÍCH IMAGES:")
            # Tìm tất cả hình ảnh
            all_images = soup.find_all('img')
            print(f"  Tổng số hình ảnh: {len(all_images)}")
            
            # Phân tích hình ảnh theo vùng
            image_analysis = {
                'content_images': [],
                'sidebar_images': [],
                'header_images': [],
                'footer_images': [],
                'other_images': []
            }
            
            for img in all_images:
                src = img.get('src', '')
                alt = img.get('alt', '').lower()
                
                # Phân loại hình ảnh
                if any(keyword in alt for keyword in ['quảng cáo', 'ad', 'banner', 'logo', 'icon']):
                    image_analysis['other_images'].append((src, alt))
                elif img.find_parent('aside') or img.find_parent('.sidebar'):
                    image_analysis['sidebar_images'].append((src, alt))
                elif img.find_parent('header'):
                    image_analysis['header_images'].append((src, alt))
                elif img.find_parent('footer'):
                    image_analysis['footer_images'].append((src, alt))
                elif img.find_parent('.content') or img.find_parent('.article-content'):
                    image_analysis['content_images'].append((src, alt))
                else:
                    image_analysis['other_images'].append((src, alt))
            
            for category, images in image_analysis.items():
                print(f"  {category}: {len(images)} images")
                for j, (src, alt) in enumerate(images[:3]):  # Chỉ hiển thị 3 hình đầu
                    print(f"    [{j+1}] src: {src[:80]}...")
                    print(f"        alt: {alt[:50]}...")
            
            print("\n5. PHÂN TÍCH DATE:")
            date_selectors = [
                '.date',
                '.time',
                '.published',
                '.post-date',
                '.article-date',
                '.entry-date',
                '.meta-date',
                'time',
                '.datetime'
            ]
            
            for selector in date_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"  {selector}: {len(elements)} elements found")
                    for j, elem in enumerate(elements[:2]):
                        text = elem.get_text(strip=True)
                        if text:
                            print(f"    [{j+1}] {text}")
                else:
                    print(f"  {selector}: Không tìm thấy")
            
            # Lưu HTML để phân tích thêm
            html_filename = f"output/debug_article_{i+1}.html"
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            print(f"\nĐã lưu HTML vào: {html_filename}")
            
            # Nghỉ giữa các request
            if i < 2:  # Không nghỉ sau request cuối
                print("\nNghỉ 2 giây trước khi phân tích bài viết tiếp theo...")
                time.sleep(2)
                
        except Exception as e:
            print(f"Lỗi khi phân tích bài viết {i+1}: {e}")
            continue

if __name__ == "__main__":
    analyze_article_structure() 