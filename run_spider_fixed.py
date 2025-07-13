#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from baotintuc.spiders.phap_luat_fixed import PhapLuatSpiderFixed

def main():
    # Thiết lập project settings
    settings = get_project_settings()
    
    # Cấu hình output
    settings.set('FEEDS', {
        'output/articles.json': {
            'format': 'json',
            'encoding': 'utf8',
            'indent': 2,
            'overwrite': True
        }
    })
    
    # Cấu hình logging
    settings.set('LOG_LEVEL', 'INFO')
    
    # Tạo thư mục output nếu chưa có
    os.makedirs('output', exist_ok=True)
    
    # Khởi tạo crawler process
    process = CrawlerProcess(settings)
    
    # Thêm spider vào process
    process.crawl(PhapLuatSpiderFixed)
    
    # Chạy spider
    process.start()

if __name__ == '__main__':
    main() 