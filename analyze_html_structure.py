#!/usr/bin/env python3
"""
Script để phân tích cấu trúc HTML và tìm selector chính xác cho nội dung bài viết
"""

import os
from bs4 import BeautifulSoup
import re

def analyze_html_structure(html_file):
    """Phân tích cấu trúc HTML để tìm selector chính xác"""
    
    print(f"🔍 Phân tích file: {html_file}")
    print("=" * 60)
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Tìm các selector có thể chứa nội dung bài viết
    content_selectors = [
        '.content-detail',
        '.article-content', 
        '.content',
        '.detail-content',
        '.article-body',
        '.post-content',
        '.entry-content',
        '.main-content',
        '.story-content',
        '.article-detail',
        '.news-content',
        '.story-body',
        '.article-text',
        '.news-text'
    ]
    
    print("📋 Kết quả phân tích các selector:")
    print("-" * 40)
    
    for selector in content_selectors:
        elements = soup.select(selector)
        if elements:
            element = elements[0]
            # Đếm số ảnh trong element này
            images = element.find_all('img')
            # Đếm số đoạn văn
            paragraphs = element.find_all('p')
            # Lấy text mẫu
            text_sample = element.get_text()[:100].strip()
            
            print(f"✅ {selector}:")
            print(f"   - Số ảnh: {len(images)}")
            print(f"   - Số đoạn văn: {len(paragraphs)}")
            print(f"   - Text mẫu: {text_sample}...")
            
            # Hiển thị một số ảnh đầu tiên
            if images:
                print(f"   - Ảnh đầu tiên:")
                for i, img in enumerate(images[:3]):
                    src = img.get('src', '')
                    alt = img.get('alt', '')
                    print(f"     {i+1}. src: {src[:80]}...")
                    print(f"        alt: {alt[:50]}...")
            print()
    
    # Tìm tất cả ảnh trong trang và phân loại
    print("🖼️  Phân tích tất cả ảnh trong trang:")
    print("-" * 40)
    
    all_images = soup.find_all('img')
    print(f"Tổng số ảnh: {len(all_images)}")
    
    # Phân loại ảnh theo URL
    content_images = []
    sidebar_images = []
    ad_images = []
    
    for img in all_images:
        src = img.get('src', '')
        alt = img.get('alt', '')
        
        # Kiểm tra xem ảnh có phải là ảnh nội dung không
        if any(keyword in src.lower() for keyword in ['cdnmedia', 'cdnthumb']):
            if any(keyword in alt.lower() for keyword in ['chú thích', 'ảnh', 'hình']):
                content_images.append((src, alt))
            else:
                content_images.append((src, alt))
        elif any(keyword in src.lower() for keyword in ['banner', 'quang-cao', 'advertisement']):
            ad_images.append((src, alt))
        else:
            sidebar_images.append((src, alt))
    
    print(f"Ảnh nội dung: {len(content_images)}")
    print(f"Ảnh quảng cáo: {len(ad_images)}")
    print(f"Ảnh sidebar: {len(sidebar_images)}")
    
    # Hiển thị một số ảnh nội dung
    if content_images:
        print("\n📸 Ảnh nội dung (10 ảnh đầu):")
        for i, (src, alt) in enumerate(content_images[:10]):
            print(f"{i+1}. {src[:80]}...")
            print(f"   Alt: {alt[:50]}...")
    
    # Tìm các div có class chứa từ khóa liên quan đến nội dung
    print("\n🔍 Tìm các div có class liên quan đến nội dung:")
    print("-" * 40)
    
    content_divs = soup.find_all('div', class_=re.compile(r'content|article|story|news|detail|body|text', re.I))
    
    for div in content_divs[:5]:  # Chỉ xem 5 div đầu
        class_name = ' '.join(div.get('class', []))
        images_count = len(div.find_all('img'))
        text_length = len(div.get_text())
        
        print(f"Div class: {class_name}")
        print(f"  - Số ảnh: {images_count}")
        print(f"  - Độ dài text: {text_length}")
        print()

def main():
    # Sử dụng file debug_full_page.html có sẵn
    html_file = 'debug_full_page.html'
    
    if not os.path.exists(html_file):
        print("❌ Không tìm thấy file debug_full_page.html")
        return
    
    analyze_html_structure(html_file)

if __name__ == "__main__":
    main() 