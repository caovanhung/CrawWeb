#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import ssl
from urllib3.util.ssl_ import create_urllib3_context
import json
from datetime import datetime, timedelta

# Tắt SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

def analyze_pagination():
    """Phân tích cấu trúc pagination của baotintuc.vn"""
    
    base_url = "https://baotintuc.vn/phap-luat-475ct0.htm"
    
    # Headers để giả lập browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print(f"Đang phân tích trang: {base_url}")
        response = requests.get(base_url, headers=headers, verify=False, timeout=30)
        response.raise_for_status()
        
        html_content = response.text
        
        # Tìm các link pagination
        pagination_patterns = [
            'page=',
            'trang=',
            'p=',
            'pg=',
            'pagination',
            'next',
            'previous',
            'sau',
            'truoc'
        ]
        
        print("\n=== PHÂN TÍCH PAGINATION ===")
        
        # Tìm các link có thể là pagination
        lines = html_content.split('\n')
        pagination_links = []
        
        for i, line in enumerate(lines):
            for pattern in pagination_patterns:
                if pattern in line.lower():
                    # Tìm URL trong line
                    if 'href=' in line:
                        start = line.find('href="') + 6
                        end = line.find('"', start)
                        if start > 5 and end > start:
                            url = line[start:end]
                            if url.startswith('/') or 'baotintuc.vn' in url:
                                pagination_links.append({
                                    'line': i + 1,
                                    'pattern': pattern,
                                    'url': url,
                                    'context': line.strip()[:100]
                                })
        
        print(f"Tìm thấy {len(pagination_links)} link có thể là pagination:")
        for link in pagination_links[:10]:  # Chỉ hiển thị 10 link đầu
            print(f"  Line {link['line']}: {link['pattern']} -> {link['url']}")
            print(f"    Context: {link['context']}")
        
        # Tìm các link có số trang
        import re
        page_numbers = re.findall(r'[?&](page|trang|p|pg)=(\d+)', html_content)
        if page_numbers:
            print(f"\nTìm thấy {len(page_numbers)} tham số số trang:")
            for param, num in page_numbers[:10]:
                print(f"  {param}={num}")
        
        # Tìm các link "Trang sau", "Trang trước"
        next_prev_patterns = [
            r'<a[^>]*href="([^"]*)"[^>]*>(Trang sau|Trang trước|Sau|Trước|Next|Previous)[^<]*</a>',
            r'<a[^>]*>(Trang sau|Trang trước|Sau|Trước|Next|Previous)[^<]*</a>[^>]*href="([^"]*)"',
        ]
        
        for pattern in next_prev_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                print(f"\nTìm thấy {len(matches)} link điều hướng:")
                for match in matches[:5]:
                    print(f"  {match}")
        
        # Lưu HTML để phân tích thêm
        with open('output/pagination_analysis.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\nĐã lưu HTML vào: output/pagination_analysis.html")
        
        return pagination_links
        
    except Exception as e:
        print(f"Lỗi khi phân tích pagination: {e}")
        return []

if __name__ == "__main__":
    analyze_pagination() 