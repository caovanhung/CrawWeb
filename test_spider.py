#!/usr/bin/env python3
"""
Script test để kiểm tra spider mà không crawl thực tế
"""

import sys
import os
from datetime import datetime

def test_spider_import():
    """Test import spider"""
    try:
        from baotintuc.spiders.phap_luat import PhapLuatSpider
        print("✅ Import spider thành công")
        return True
    except ImportError as e:
        print(f"❌ Lỗi import spider: {e}")
        return False

def test_items_import():
    """Test import items"""
    try:
        from baotintuc.items import BaotintucItem
        print("✅ Import items thành công")
        return True
    except ImportError as e:
        print(f"❌ Lỗi import items: {e}")
        return False

def test_pipeline_import():
    """Test import pipeline"""
    try:
        from baotintuc.pipelines import BaotintucPipeline
        print("✅ Import pipeline thành công")
        return True
    except ImportError as e:
        print(f"❌ Lỗi import pipeline: {e}")
        return False

def test_spider_creation():
    """Test tạo spider instance"""
    try:
        from baotintuc.spiders.phap_luat import PhapLuatSpider
        spider = PhapLuatSpider()
        print("✅ Tạo spider instance thành công")
        print(f"   - Name: {spider.name}")
        print(f"   - Start URLs: {spider.start_urls}")
        print(f"   - Allowed domains: {spider.allowed_domains}")
        return True
    except Exception as e:
        print(f"❌ Lỗi tạo spider: {e}")
        return False

def test_item_creation():
    """Test tạo item"""
    try:
        from baotintuc.items import BaotintucItem
        item = BaotintucItem()
        item['topic'] = 'Pháp luật'
        item['title'] = 'Test title'
        item['summary'] = 'Test summary'
        item['content'] = 'Test content'
        item['url'] = 'https://test.com'
        item['source'] = 'baotintuc.vn'
        item['date'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+07:00')
        
        print("✅ Tạo item thành công")
        print(f"   - Topic: {item['topic']}")
        print(f"   - Title: {item['title']}")
        print(f"   - Source: {item['source']}")
        return True
    except Exception as e:
        print(f"❌ Lỗi tạo item: {e}")
        return False

def main():
    print("=" * 60)
    print("TEST SPIDER - BÁO TIN TỨC PHÁP LUẬT")
    print("=" * 60)
    print(f"Thời gian test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Import Spider", test_spider_import),
        ("Import Items", test_items_import),
        ("Import Pipeline", test_pipeline_import),
        ("Create Spider Instance", test_spider_creation),
        ("Create Item", test_item_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"🧪 Testing: {test_name}")
        if test_func():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Kết quả: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ Tất cả tests đều thành công!")
        print("🚀 Bạn có thể chạy spider bằng lệnh: python run_spider.py")
    else:
        print("❌ Có lỗi trong quá trình test")
        print("🔧 Vui lòng kiểm tra lại cấu hình")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 