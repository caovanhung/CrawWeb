#!/usr/bin/env python3
"""
Script để chạy spider crawl dữ liệu pháp luật từ baotintuc.vn
"""

import subprocess
import sys
import os
from datetime import datetime

def main():
    print("=" * 60)
    print("SCRAPY CRAWLER - BÁO TIN TỨC PHÁP LUẬT")
    print("=" * 60)
    print(f"Thời gian bắt đầu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Kiểm tra xem có cài đặt scrapy chưa
        result = subprocess.run([sys.executable, '-m', 'scrapy', 'version'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Scrapy chưa được cài đặt!")
            print("Vui lòng chạy: pip install -r requirements.txt")
            return
        
        print("✅ Scrapy đã được cài đặt")
        print("🚀 Bắt đầu crawl dữ liệu...")
        print()
        
        # Chạy spider
        cmd = [sys.executable, '-m', 'scrapy', 'crawl', 'phap_luat']
        result = subprocess.run(cmd, cwd=os.getcwd())
        
        if result.returncode == 0:
            print()
            print("✅ Crawl thành công!")
            print("📁 Kiểm tra thư mục 'output/' để xem kết quả")
        else:
            print()
            print("❌ Có lỗi xảy ra trong quá trình crawl")
            
    except KeyboardInterrupt:
        print()
        print("⚠️  Đã dừng crawl theo yêu cầu của người dùng")
    except Exception as e:
        print()
        print(f"❌ Lỗi: {e}")
    
    print()
    print(f"Thời gian kết thúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main() 