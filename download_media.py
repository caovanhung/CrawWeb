#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import requests
import ssl
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime
import time

# Tắt SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

class MediaDownloader:
    def __init__(self, json_file='output/articles.json'):
        self.json_file = json_file
        self.base_dir = 'output/media_articles'
        self.session = requests.Session()
        self.session.verify = False
        
        # Headers để giả lập browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        # Tạo thư mục gốc
        os.makedirs(self.base_dir, exist_ok=True)
    
    def sanitize_filename(self, filename):
        """Làm sạch tên file để tránh lỗi"""
        # Loại bỏ các ký tự không hợp lệ
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Giới hạn độ dài
        if len(filename) > 200:
            filename = filename[:200]
        return filename
    
    def download_file(self, url, filepath):
        """Tải file từ URL"""
        try:
            response = self.session.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True
        except Exception as e:
            print(f"  Lỗi tải {url}: {e}")
            return False
    
    def extract_images_from_html(self, html_content, article_url):
        """Trích xuất ảnh từ HTML của bài viết (chỉ ảnh trong nội dung)"""
        images = []
        
        # Tìm ảnh trong các thẻ img
        img_patterns = [
            r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*>',
            r'<img[^>]*alt="([^"]*)"[^>]*src="([^"]*)"[^>]*>',
            r'<img[^>]*src="([^"]*)"[^>]*>',
        ]
        
        for pattern in img_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    img_url, img_alt = match
                else:
                    img_url = match[0]
                    img_alt = f"image_{len(images)}"
                
                if img_url and self.is_content_image(img_url, img_alt):
                    # Chuyển URL tương đối thành tuyệt đối
                    if img_url.startswith('/'):
                        img_url = urljoin(article_url, img_url)
                    elif not img_url.startswith('http'):
                        img_url = urljoin(article_url, img_url)
                    
                    images.append({
                        'url': img_url,
                        'alt': img_alt,
                        'type': 'content_image'
                    })
        
        return list({img['url']: img for img in images}.values())  # Loại bỏ trùng lặp
    
    def is_content_image(self, img_url, img_alt):
        """Kiểm tra xem ảnh có phải là ảnh nội dung bài viết không"""
        # Loại bỏ ảnh quảng cáo
        ad_keywords = [
            'quang-cao', 'advertisement', 'ads', 'banner', 'sponsor',
            'quảng cáo', 'banner', 'sponsor', 'ad', 'ads'
        ]
        
        img_url_lower = img_url.lower()
        img_alt_lower = img_alt.lower()
        
        # Kiểm tra URL và alt text có chứa từ khóa quảng cáo
        for keyword in ad_keywords:
            if keyword in img_url_lower or keyword in img_alt_lower:
                return False
        
        # Loại bỏ ảnh có kích thước nhỏ (thường là icon, avatar)
        size_patterns = [
            r'(\d+)x(\d+)',  # 100x100, 200x200
            r'thumb', 'thumbnail', 'icon', 'avatar'
        ]
        
        for pattern in size_patterns:
            if re.search(pattern, img_url_lower):
                # Kiểm tra nếu là ảnh nhỏ thì bỏ qua
                if 'thumb' in img_url_lower or 'icon' in img_url_lower or 'avatar' in img_url_lower:
                    return False
        
        # Chỉ lấy ảnh từ domain chính của baotintuc.vn
        valid_domains = [
            'baotintuc.vn',
            'cdnmedia.baotintuc.vn',
            'cdnthumb.baotintuc.vn',
            'media.baotintuc.vn'
        ]
        
        is_valid_domain = any(domain in img_url_lower for domain in valid_domains)
        
        return is_valid_domain
    
    def extract_videos_from_html(self, html_content):
        """Trích xuất video URLs từ HTML (chỉ video trong nội dung)"""
        videos = []
        
        # Tìm các thẻ video trong nội dung bài viết
        video_patterns = [
            r'<video[^>]*src="([^"]*)"[^>]*>',
            r'<video[^>]*><source[^>]*src="([^"]*)"[^>]*>',
            r'<iframe[^>]*src="([^"]*)"[^>]*>',
            r'data-video-url="([^"]*)"',
            r'video-url="([^"]*)"',
        ]
        
        for pattern in video_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if match and self.is_content_video(match):
                    videos.append(match)
        
        return list(set(videos))  # Loại bỏ trùng lặp
    
    def is_content_video(self, video_url):
        """Kiểm tra xem video có phải là video nội dung bài viết không"""
        video_url_lower = video_url.lower()
        
        # Loại bỏ video quảng cáo
        ad_keywords = [
            'quang-cao', 'advertisement', 'ads', 'banner', 'sponsor',
            'quảng cáo', 'banner', 'sponsor', 'ad', 'ads'
        ]
        
        for keyword in ad_keywords:
            if keyword in video_url_lower:
                return False
        
        # Chỉ lấy video từ các nguồn hợp lệ
        valid_sources = [
            'baotintuc.vn',
            'youtube.com',
            'youtu.be',
            'vimeo.com',
            'dailymotion.com'
        ]
        
        return any(source in video_url_lower for source in valid_sources)
    
    def process_article(self, article, index):
        """Xử lý một bài viết"""
        title = article.get('title', f'Bài viết {index}')
        url = article.get('url', '')
        
        print(f"\n[{index}] Đang xử lý: {title[:50]}...")
        
        # Tạo tên thư mục từ title
        safe_title = self.sanitize_filename(title)
        article_dir = os.path.join(self.base_dir, f"{index:02d}_{safe_title}")
        os.makedirs(article_dir, exist_ok=True)
        
        # Lưu thông tin bài viết
        article_info = {
            'title': title,
            'url': url,
            'summary': article.get('summary', ''),
            'date': article.get('date', ''),
            'topic': article.get('topic', ''),
            'content': article.get('content', '')[:500] + '...' if len(article.get('content', '')) > 500 else article.get('content', '')
        }
        
        with open(os.path.join(article_dir, 'article_info.json'), 'w', encoding='utf-8') as f:
            json.dump(article_info, f, ensure_ascii=False, indent=2)
        
        # Tải HTML và trích xuất ảnh/video từ nội dung bài viết
        images = []
        videos = []
        
        if url:
            try:
                print(f"  Tải HTML để trích xuất ảnh và video...")
                response = self.session.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                
                html_content = response.text
                
                # Lưu HTML
                with open(os.path.join(article_dir, 'article.html'), 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # Trích xuất ảnh từ nội dung bài viết
                images = self.extract_images_from_html(html_content, url)
                
                # Trích xuất video từ nội dung bài viết
                videos = self.extract_videos_from_html(html_content)
                
            except Exception as e:
                print(f"  Lỗi tải HTML: {e}")
        
        # Tải ảnh từ nội dung bài viết
        downloaded_images = []
        
        if images:
            print(f"  Tìm thấy {len(images)} ảnh trong nội dung bài viết")
            images_dir = os.path.join(article_dir, 'images')
            os.makedirs(images_dir, exist_ok=True)
            
            for i, img in enumerate(images):
                img_url = img.get('url', '')
                img_alt = img.get('alt', f'image_{i}')
                
                if img_url:
                    # Tạo tên file
                    filename = self.sanitize_filename(img_alt)
                    if not filename:
                        filename = f'image_{i:03d}'
                    
                    # Lấy extension từ URL
                    parsed_url = urlparse(img_url)
                    path = parsed_url.path
                    if '.' in path:
                        ext = path.split('.')[-1].split('?')[0]
                        if ext.lower() in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                            filename += f'.{ext}'
                        else:
                            filename += '.jpg'
                    else:
                        filename += '.jpg'
                    
                    filepath = os.path.join(images_dir, filename)
                    
                    print(f"    Tải ảnh {i+1}/{len(images)}: {filename}")
                    if self.download_file(img_url, filepath):
                        downloaded_images.append({
                            'original_url': img_url,
                            'alt': img_alt,
                            'local_path': filepath,
                            'filename': filename
                        })
                    time.sleep(0.5)  # Delay để tránh spam
        
        # Xử lý video từ nội dung bài viết
        if videos:
            print(f"  Tìm thấy {len(videos)} video trong nội dung bài viết")
            videos_dir = os.path.join(article_dir, 'videos')
            os.makedirs(videos_dir, exist_ok=True)
            
            for i, video_url in enumerate(videos):
                print(f"    Video {i+1}: {video_url}")
                
                # Lưu thông tin video
                video_info = {
                    'url': video_url,
                    'index': i,
                    'type': 'video'
                }
                
                with open(os.path.join(videos_dir, f'video_{i:03d}_info.json'), 'w', encoding='utf-8') as f:
                    json.dump(video_info, f, ensure_ascii=False, indent=2)
        
        # Tạo báo cáo
        report = {
            'article_title': title,
            'processed_at': datetime.now().isoformat(),
            'images_found': len(images),
            'images_downloaded': len(downloaded_images),
            'videos_found': len(videos),
            'article_dir': article_dir
        }
        
        with open(os.path.join(article_dir, 'download_report.json'), 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ Hoàn thành: {len(downloaded_images)} ảnh, {len(videos)} video")
        return report
    
    def process_all_articles(self):
        """Xử lý tất cả bài viết"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            
            print(f"Tìm thấy {len(articles)} bài viết trong {self.json_file}")
            
            total_reports = []
            for i, article in enumerate(articles, 1):
                report = self.process_article(article, i)
                total_reports.append(report)
                time.sleep(1)  # Delay giữa các bài viết
            
            # Tạo báo cáo tổng hợp
            summary = {
                'total_articles': len(articles),
                'processed_at': datetime.now().isoformat(),
                'total_images_found': sum(r['images_found'] for r in total_reports),
                'total_images_downloaded': sum(r['images_downloaded'] for r in total_reports),
                'total_videos_found': sum(r['videos_found'] for r in total_reports),
                'base_directory': self.base_dir,
                'reports': total_reports
            }
            
            with open(os.path.join(self.base_dir, 'summary_report.json'), 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            print(f"\n🎉 HOÀN THÀNH!")
            print(f"📁 Thư mục: {self.base_dir}")
            print(f"📊 Tổng cộng: {len(articles)} bài viết")
            print(f"🖼️  Ảnh: {summary['total_images_downloaded']}/{summary['total_images_found']}")
            print(f"🎥 Video: {summary['total_videos_found']}")
            
        except Exception as e:
            print(f"Lỗi: {e}")

if __name__ == "__main__":
    downloader = MediaDownloader()
    downloader.process_all_articles() 