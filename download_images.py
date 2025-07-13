#!/usr/bin/env python3
"""
Script để tải ảnh từ kết quả JSON đã crawl
"""

import json
import requests
import os
from urllib.parse import urlparse
import time
from datetime import datetime

def download_images_from_json(json_file):
    """Tải ảnh từ file JSON đã crawl"""
    
    print("=" * 60)
    print("TẢI ẢNH TỪ KẾT QUẢ CRAWL")
    print("=" * 60)
    
    # Đọc file JSON
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Lỗi đọc file JSON: {e}")
        return
    
    print(f"📄 Đọc được {len(data)} bài viết từ {json_file}")
    
    # Tạo thư mục images nếu chưa có
    images_dir = 'output/images'
    os.makedirs(images_dir, exist_ok=True)
    
    # Headers để tải ảnh
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Language': 'vi,en;q=0.8',
    }
    
    total_images = 0
    downloaded_images = 0
    
    for i, article in enumerate(data):
        print(f"\n📰 Bài viết {i+1}: {article.get('title', 'N/A')[:50]}...")
        
        # Lấy danh sách ảnh từ bài viết
        images = article.get('images', [])
        if not images:
            print("   ⚠️  Không có ảnh trong bài viết này")
            continue
        
        print(f"   🖼️  Tìm thấy {len(images)} ảnh")
        total_images += len(images)
        
        for j, img_info in enumerate(images):
            img_url = img_info.get('url')
            img_filename = img_info.get('filename')
            img_path = img_info.get('local_path')
            
            if not img_url or not img_filename:
                continue
            
            # Kiểm tra xem ảnh đã tồn tại chưa
            if os.path.exists(img_path):
                print(f"      ✅ Ảnh {j+1}: {img_filename} (đã tồn tại)")
                downloaded_images += 1
                continue
            
            # Tải ảnh
            try:
                print(f"      📥 Đang tải ảnh {j+1}: {img_filename}")
                response = requests.get(img_url, headers=headers, timeout=10, verify=False)
                response.raise_for_status()
                
                # Lưu ảnh
                with open(img_path, 'wb') as f:
                    f.write(response.body)
                
                print(f"      ✅ Đã tải thành công: {img_filename}")
                downloaded_images += 1
                
                # Delay nhỏ để tránh gây tải cho server
                time.sleep(0.5)
                
            except Exception as e:
                print(f"      ❌ Lỗi tải ảnh {img_filename}: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 KẾT QUẢ TẢI ẢNH:")
    print(f"   Tổng số ảnh: {total_images}")
    print(f"   Đã tải thành công: {downloaded_images}")
    print(f"   Thất bại: {total_images - downloaded_images}")
    print(f"   Thư mục lưu: {images_dir}")
    print("=" * 60)

def main():
    # Tìm file JSON mới nhất
    output_dir = 'output'
    json_files = [f for f in os.listdir(output_dir) if f.endswith('.json') and 'baotintuc_phap_luat' in f]
    
    if not json_files:
        print("❌ Không tìm thấy file JSON kết quả crawl")
        return
    
    # Lấy file mới nhất
    latest_file = max(json_files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
    json_file = os.path.join(output_dir, latest_file)
    
    print(f"🎯 Sử dụng file: {json_file}")
    
    # Tải ảnh
    download_images_from_json(json_file)

if __name__ == "__main__":
    main() 