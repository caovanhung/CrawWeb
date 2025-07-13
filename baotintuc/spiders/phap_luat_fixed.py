#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import scrapy
import re
import os
from datetime import datetime, date
from urllib.parse import urljoin
from baotintuc.items import BaotintucItem

class PhapLuatSpiderFixed(scrapy.Spider):
    name = 'phap_luat_fixed'
    allowed_domains = ['baotintuc.vn']
    start_urls = ['http://baotintuc.vn/phap-luat-475ct0.htm']
    
    def __init__(self, *args, **kwargs):
        super(PhapLuatSpiderFixed, self).__init__(*args, **kwargs)
        self.today = date.today()
        
        # Tạo thư mục lưu ảnh
        self.images_dir = 'output/images'
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Tạo thư mục lưu bài viết
        self.articles_dir = 'output/articles'
        os.makedirs(self.articles_dir, exist_ok=True)
    
    def parse(self, response):
        """Parse trang danh sách bài viết"""
        self.logger.info(f"Đang parse trang: {response.url}")
        
        # Tìm các bài viết - thử nhiều selector
        article_selectors = [
            '.list-news .item-news',
            '.list-news li',
            '.news-list .news-item',
            '.article-list .article-item',
            '.content-list .content-item',
            '.list-news .item',
            '.news-item',
            '.article-item'
        ]
        
        articles = []
        for selector in article_selectors:
            articles = response.css(selector)
            if articles:
                self.logger.info(f"Tìm thấy {len(articles)} bài viết với selector: {selector}")
                break
        
        self.logger.info(f"Tìm thấy {len(articles)} bài viết")
        
        for i, article in enumerate(articles):
            # Lấy link bài viết - thử nhiều selector
            article_link = article.css('a::attr(href)').get()
            if not article_link:
                article_link = article.css('h3 a::attr(href), h2 a::attr(href), .title a::attr(href)').get()
            
            if article_link:
                article_url = urljoin(response.url, article_link)
                
                # Chỉ crawl bài viết từ section Pháp luật
                if '/phap-luat/' not in article_url:
                    self.logger.info(f"Bỏ qua bài viết không thuộc section Pháp luật: {article_url}")
                    continue
                
                # Lấy thông tin cơ bản từ trang danh sách
                title = article.css('h3 a::text, h2 a::text, .title a::text, a::text').get()
                summary = article.css('.summary::text, .desc::text, .sapo::text').get()
                
                # Lấy ngày đăng - thử nhiều selector
                date_str = article.css('.time::text, .date::text, .datetime::text, time::text').get()
                
                self.logger.info(f"Bài viết {i+1}: {title[:50]}... - Ngày: {date_str}")
                
                # Tạm thời bỏ qua filter ngày để lấy tất cả bài viết
                yield scrapy.Request(
                    url=article_url,
                    callback=self.parse_article,
                    meta={
                        'title': title,
                        'summary': summary,
                        'date_str': date_str
                    }
                )
    
    def parse_article(self, response):
        """Parse trang chi tiết bài viết"""
        
        # Debug: In ra URL bài viết
        self.logger.info(f"Đang parse bài viết: {response.url}")
        print(f"TEST PRINT: Đang parse bài viết: {response.url}")
        
        # Lấy thông tin từ meta
        title = response.meta.get('title', '')
        summary = response.meta.get('summary', '')
        date_str = response.meta.get('date_str', '')
        
        # Luôn thử lấy title từ trang chi tiết (ưu tiên hơn title từ trang danh sách)
        print("TEST PRINT: Bắt đầu lấy title từ trang chi tiết")
        self.logger.info("Bắt đầu lấy title từ trang chi tiết")
        
        # Thử lấy bằng XPath string() trước - lấy toàn bộ text content
        detail_title = response.css('h1.detail-title').xpath('string()').get()
        print(f"DEBUG: h1.detail-title string(): '{detail_title}'")
        self.logger.info(f"DEBUG: h1.detail-title string(): '{detail_title}'")
        
        # Nếu không có, thử lấy bằng ::text
        if not detail_title or not detail_title.strip():
            detail_title = response.css('h1.detail-title::text').get()
            print(f"DEBUG: h1.detail-title::text: '{detail_title}'")
            self.logger.info(f"DEBUG: h1.detail-title::text: '{detail_title}'")
        
        # Nếu vẫn không có, thử lấy h1 đầu tiên
        if not detail_title or not detail_title.strip():
            all_h1 = response.css('h1')
            print(f"DEBUG: Tìm thấy {len(all_h1)} h1 tags")
            self.logger.info(f"DEBUG: Tìm thấy {len(all_h1)} h1 tags")
            
            for i, h1 in enumerate(all_h1):
                h1_text = h1.xpath('string()').get()
                print(f"DEBUG: h1[{i}] string(): '{h1_text}'")
                self.logger.info(f"DEBUG: h1[{i}] string(): '{h1_text}'")
            
            # Lấy text của h1 đầu tiên
            if all_h1:
                detail_title = all_h1[0].xpath('string()').get()
                print(f"DEBUG: h1[0] string(): '{detail_title}'")
                self.logger.info(f"DEBUG: h1[0] string(): '{detail_title}'")
        
        # Chuẩn hóa whitespace và sử dụng title từ trang chi tiết nếu có
        if detail_title and detail_title.strip():
            title = ' '.join(detail_title.split())
            print(f"DEBUG: Final title from detail page: '{title}'")
            self.logger.info(f"DEBUG: Final title from detail page: '{title}'")
        else:
            print(f"DEBUG: Using title from list page: '{title}'")
            self.logger.info(f"DEBUG: Using title from list page: '{title}'")
        
        # Nếu chưa có summary từ trang danh sách, lấy từ trang chi tiết
        if not summary:
            summary = response.css('.summary::text, .desc::text, .sapo::text, .lead::text').get()
        
        # Lấy nội dung đầy đủ - loại bỏ phần bài viết liên quan
        content_selectors = [
            '.content-detail',
            '.article-content',
            '.content',
            '.detail-content',
            '.article-body',
            '.post-content'
        ]
        
        content_parts = []
        content_element = None
        
        # Tìm phần content chính
        for selector in content_selectors:
            content_elements = response.css(selector)
            if content_elements:
                content_element = content_elements[0]  # Lấy phần tử đầu tiên
                self.logger.info(f"Tìm thấy content element với selector: {selector}")
                break
        
        if content_element:
            # Loại bỏ các phần không phải nội dung chính trước khi lấy text
            # Xóa phần list-concern (bài viết liên quan)
            for concern in content_element.css('.list-concern, #plhMain_NewsDetail1_divRelation'):
                concern.extract()
            
            # Xóa phần widget_info (bài viết liên quan)
            for widget in content_element.css('.widget_info'):
                widget.extract()
            
            # Xóa phần boxdata (video, ảnh liên quan)
            for box in content_element.css('.boxdata'):
                box.extract()
            
            # Xóa phần likeshare (chia sẻ mạng xã hội)
            for share in content_element.css('.likeshare'):
                share.extract()
            
            # Xóa phần keysword (từ khóa)
            for keyword in content_element.css('.keysword'):
                keyword.extract()
            
            # Xóa phần btt-bottom (phần cuối trang)
            for bottom in content_element.css('.btt-bottom'):
                bottom.extract()
            
            # Xóa iframe (video comment)
            for iframe in content_element.css('iframe'):
                iframe.extract()
            
            # Lấy text từ các thẻ p trong content đã được lọc
            content_parts = content_element.css('p::text').getall()
            
            # Nếu không có thẻ p, lấy text trực tiếp
            if not content_parts:
                content_text = content_element.xpath('string()').get()
                if content_text:
                    content_parts = [content_text]
        
        content = ' '.join([part.strip() for part in content_parts if part.strip()])
        
        # Xử lý ngày tháng
        parsed_date = self.parse_date(date_str)
        
        # Debug: In ra thông tin bài viết
        self.logger.info(f"Title: {title[:50]}...")
        self.logger.info(f"Summary: {summary[:50] if summary else 'N/A'}...")
        self.logger.info(f"Content length: {len(content)}")
        
        # Tải ảnh từ bài viết
        images = self.download_images(response)
        
        # Lưu bài viết dưới dạng HTML để debug
        article_filename = self.save_article_html(response, title)
        
        # Debug: Lưu HTML cho phân tích
        # Sử dụng biến instance để đếm số bài viết
        if not hasattr(self, 'article_count'):
            self.article_count = 0
        self.article_count += 1
        
        debug_filename = f"output/debug_article_{self.article_count}.html"
        with open(debug_filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        self.logger.info(f"Đã lưu HTML debug vào: {debug_filename}")
        
        # Tạo item
        item = BaotintucItem()
        item['topic'] = 'Pháp luật'
        item['title'] = title.strip() if title else ''
        item['summary'] = summary.strip() if summary else ''
        item['content'] = content
        item['url'] = response.url
        item['source'] = 'baotintuc.vn'
        item['date'] = parsed_date
        item['images'] = images
        item['article_file'] = article_filename
        
        yield item
    
    def is_today_article(self, date_str):
        """Kiểm tra xem bài viết có phải của hôm nay không"""
        if not date_str:
            return False
            
        # Xử lý các format ngày tháng khác nhau
        date_str = date_str.strip()
        
        # Format: "13/07/2025 12:00"
        if re.match(r'\d{1,2}/\d{1,2}/\d{4}', date_str):
            try:
                article_date = datetime.strptime(date_str.split()[0], '%d/%m/%Y').date()
                return article_date == self.today
            except:
                pass
        
        # Format: "Hôm nay", "Hôm qua", etc.
        if 'hôm nay' in date_str.lower():
            return True
            
        # Format: "X giờ trước", "X phút trước"
        if any(keyword in date_str.lower() for keyword in ['giờ trước', 'phút trước', 'vừa']):
            return True
            
        return False
    
    def parse_date(self, date_str):
        """Parse ngày tháng thành format ISO"""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%dT%H:%M:%S+07:00')
            
        date_str = date_str.strip()
        
        # Format: "13/07/2025 12:00"
        if re.match(r'\d{1,2}/\d{1,2}/\d{4}', date_str):
            try:
                if ' ' in date_str:
                    date_part, time_part = date_str.split(' ', 1)
                    dt = datetime.strptime(f"{date_part} {time_part}", '%d/%m/%Y %H:%M')
                else:
                    dt = datetime.strptime(date_str, '%d/%m/%Y')
                return dt.strftime('%Y-%m-%dT%H:%M:%S+07:00')
            except:
                pass
        
        # Nếu không parse được, trả về thời gian hiện tại
        return datetime.now().strftime('%Y-%m-%dT%H:%M:%S+07:00')
    
    def download_images(self, response):
        """Tải ảnh từ bài viết"""
        images = []
        
        # Chỉ lấy ảnh từ trang chi tiết bài viết, không phải trang danh sách
        if '/phap-luat-' in response.url and response.url.endswith('.htm'):
            # Đây là trang danh sách, không lấy ảnh
            self.logger.info("Đây là trang danh sách, bỏ qua việc lấy ảnh")
            return images
        
        # Chỉ tìm ảnh trong phần nội dung chính của bài viết
        content_selectors = [
            '.content-detail',
            '.article-content',
            '.content',
            '.detail-content',
            '.article-body',
            '.post-content',
            '.entry-content',
            '.main-content',
            '.story-content'
        ]
        
        # Tìm phần nội dung chính
        content_element = None
        for selector in content_selectors:
            elements = response.css(selector)
            if elements:
                content_element = elements[0]  # Lấy phần tử đầu tiên
                self.logger.info(f"Tìm thấy nội dung với selector: {selector}")
                break
        
        if not content_element:
            self.logger.warning("Không tìm thấy phần nội dung chính")
            return images
        
        # Tìm ảnh chỉ trong phần nội dung
        img_elements = content_element.css('img')
        self.logger.info(f"Tìm thấy {len(img_elements)} ảnh trong nội dung bài viết")
        
        for i, img in enumerate(img_elements):
            img_src = img.css('::attr(src)').get()
            img_alt = img.css('::attr(alt)').get() or f'image_{i}'
            
            if img_src:
                # Tạo URL đầy đủ
                img_url = urljoin(response.url, img_src)
                
                # Lọc bỏ các ảnh không phải nội dung bài viết
                if self.is_content_image(img_url, img_alt):
                    # Tạo tên file ảnh
                    img_filename = self.generate_image_filename(img_url, img_alt)
                    img_path = os.path.join(self.images_dir, img_filename)
                    
                    # Thêm thông tin ảnh vào danh sách
                    images.append({
                        'url': img_url,
                        'alt': img_alt,
                        'filename': img_filename,
                        'local_path': img_path
                    })
        
        return images
    
    def is_content_image(self, img_url, img_alt):
        """Kiểm tra xem ảnh có phải là ảnh nội dung bài viết không"""
        img_url_lower = img_url.lower()
        img_alt_lower = img_alt.lower()
        
        # Loại bỏ ảnh quảng cáo/banner
        ad_keywords = [
            'quang-cao', 'advertisement', 'ads', 'banner', 'sponsor',
            'quảng cáo', 'banner', 'sponsor', 'ad', 'ads', 'logo',
            'thời tiết', 'thời sự', 'nổi bật', 'tuần qua', '24h',
            'vnanet', 'vietnamplus', 'vietnamnews', 'bnews', 'lecourrier',
            'nxb thông tấn', 'legal forum'
        ]
        
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
                return False
        
        # Chỉ lấy ảnh từ domain hợp lệ
        valid_domains = [
            'baotintuc.vn',
            'media.baotintuc.vn',
            'cdnthumb.baotintuc.vn'
        ]
        
        return any(domain in img_url_lower for domain in valid_domains)
    
    def save_image(self, response):
        """Lưu ảnh từ response"""
        # Tạo tên file dựa trên URL
        filename = response.url.split('/')[-1]
        if not filename or '.' not in filename:
            filename = f"image_{hash(response.url)}.jpg"
        
        filepath = os.path.join(self.images_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(response.body)
        
        return filepath
    
    def save_article_html(self, response, title):
        """Lưu bài viết dưới dạng HTML"""
        # Tạo tên file an toàn từ title
        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        safe_title = safe_title[:100]  # Giới hạn độ dài
        
        filename = f"{safe_title}_{hash(response.url)}.html"
        filepath = os.path.join(self.articles_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        return filepath
    
    def generate_image_filename(self, img_url, img_alt):
        """Tạo tên file ảnh từ URL và alt text"""
        # Lấy phần cuối của URL
        filename = img_url.split('/')[-1]
        
        # Nếu không có extension, thêm .jpg
        if '.' not in filename:
            filename = f"{filename}.jpg"
        
        # Nếu filename quá dài, rút gọn
        if len(filename) > 100:
            name, ext = os.path.splitext(filename)
            filename = f"{name[:90]}{ext}"
        
        return filename 