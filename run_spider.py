#!/usr/bin/env python3
"""
Script để chạy spider crawl dữ liệu pháp luật từ baotintuc.vn
"""

import subprocess
import sys
import os
from datetime import datetime

def run_spider():
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'articles.json')
    cmd = [
        sys.executable, '-m', 'scrapy', 'crawl', 'phap_luat',
        '-o', output_file, '-t', 'json'
    ]
    print(f"Chạy lệnh: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

if __name__ == '__main__':
    run_spider() 