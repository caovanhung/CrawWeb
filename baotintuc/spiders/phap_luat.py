import scrapy
from baotintuc.items import BaotintucItem
from datetime import datetime, timedelta
import re
from urllib.parse import urljoin
import os
import hashlib


class PhapLuatSpider(scrapy.Spider):
    name = 'phap_luat'
    allowed_domains = ['baotintuc.vn']
    start_urls = ['http://baotintuc.vn/phap-luat-475ct0.htm']
    
    def __init__(self, *args, **kwargs):
        super(PhapLuatSpider, self).__init__(*args, **kwargs)
        # Lấy ngày hôm nay
        self.today = datetime.now().date()
        
        # Tạo thư mục để lưu ảnh và bài viết
        self.images_dir = 'output/images'
        self.articles_dir = 'output/articles'
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.articles_dir, exist_ok=True)
        
    def parse(self, response):
        """Parse trang chính pháp luật để lấy danh sách bài viết"""
        
        # Debug: In ra URL hiện tại
        self.logger.info(f"Đang parse URL: {response.url}")
        
        # Debug: Lưu toàn bộ HTML để phân tích
        with open('debug_full_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        self.logger.info("Đã lưu toàn bộ HTML vào debug_full_page.html")
        
        # Debug: In ra một phần HTML để xem cấu trúc
        html_sample = response.text[:2000]
        self.logger.info(f"HTML sample: {html_sample}")
        
        # Tìm tất cả các bài viết trong trang - thử nhiều selector khác nhau
        selectors_to_try = [
            'div.list-news article',
            'div.list-news .item-news', 
            '.list-news .item',
            '.news-list .item',
            'article',
            '.item-news',
            '.news-item',
            '.article-item',
            '.list-news',
            '.news-list',
            '.content-list',
            '.main-content article',
            '.main-content .item',
            '.container article',
            '.container .item',
            '.content .item',
            '.content article',
            '.main .item',
            '.main article',
            '.news-content .item',
            '.news-content article',
            '.list .item',
            '.list article',
            '.item',
            'div[class*="news"]',
            'div[class*="item"]',
            'div[class*="article"]',
            'div[class*="list"]'
        ]
        
        articles = []
        for selector in selectors_to_try:
            found = response.css(selector)
            self.logger.info(f"Selector '{selector}': {len(found)} elements")
            if found:
                articles = found
                self.logger.info(f"Sử dụng selector: {selector}")
                break
        
        self.logger.info(f"Tìm thấy {len(articles)} bài viết")
        
        for i, article in enumerate(articles):
            # Lấy link bài viết - thử nhiều selector
            article_link = article.css('a::attr(href)').get()
            if not article_link:
                article_link = article.css('h3 a::attr(href), h2 a::attr(href), .title a::attr(href)').get()
            
            if article_link:
                article_url = urljoin(response.url, article_link)
                
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
        
        # Lấy thông tin từ meta
        title = response.meta.get('title', '')
        summary = response.meta.get('summary', '')
        date_str = response.meta.get('date_str', '')
        
        # Nếu chưa có title từ trang danh sách, lấy từ trang chi tiết
        if not title:
            title_selectors = [
                'h1.title::text',
                'h1::text', 
                '.title::text',
                '.article-title::text',
                '.post-title::text',
                '.entry-title::text',
                '.content h1::text',
                '.article h1::text',
                '.main h1::text',
                '.detail-title::text',
                '.news-title::text'
            ]
            for selector in title_selectors:
                title = response.css(selector).get()
                if title and title.strip():
                    self.logger.info(f"Tìm thấy title với selector: {selector}")
                    break
        
        # Nếu chưa có summary từ trang danh sách, lấy từ trang chi tiết
        if not summary:
            summary = response.css('.summary::text, .desc::text, .sapo::text, .lead::text').get()
        
        # Lấy nội dung đầy đủ - thử nhiều selector
        content_selectors = [
            '.content-detail p',
            '.article-content p',
            '.content p',
            '.detail-content p',
            '.article-body p',
            '.post-content p',
            '.entry-content p'
        ]
        
        content_parts = []
        for selector in content_selectors:
            content_parts = response.css(selector + '::text').getall()
            if content_parts:
                self.logger.info(f"Tìm thấy nội dung với selector: {selector}")
                break
        
        # Nếu không tìm thấy với selector p, thử lấy toàn bộ content
        if not content_parts:
            content_selectors_div = [
                '.content-detail',
                '.article-content',
                '.content',
                '.detail-content',
                '.article-body',
                '.post-content'
            ]
            for selector in content_selectors_div:
                content_text = response.css(selector + '::text').get()
                if content_text:
                    content_parts = [content_text]
                    self.logger.info(f"Tìm thấy nội dung với selector div: {selector}")
                    break
        
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
        # Lọc bỏ các ảnh quảng cáo, banner, icon
        exclude_keywords = [
            'banner', 'quang-cao', 'advertisement', 'ads',
            'icon', 'logo', 'button', 'play', 'video-play',
            'partner', 'sponsor', 'sidebar', 'widget',
            'social', 'share', 'facebook', 'twitter',
            'web_images', 'static', 'assets'
        ]
        
        img_url_lower = img_url.lower()
        img_alt_lower = img_alt.lower()
        
        # Kiểm tra URL
        for keyword in exclude_keywords:
            if keyword in img_url_lower:
                return False
        
        # Kiểm tra alt text
        for keyword in exclude_keywords:
            if keyword in img_alt_lower:
                return False
        
        # Lọc bỏ ảnh có kích thước quá nhỏ (thường là icon)
        if any(size in img_url_lower for size in ['16x16', '32x32', '48x48', '64x64']):
            return False
        
        # Lọc bỏ ảnh từ các domain quảng cáo
        ad_domains = ['doubleclick', 'googleadservices', 'googlesyndication']
        for domain in ad_domains:
            if domain in img_url_lower:
                return False
        
        return True
    
    def save_image(self, response):
        """Lưu ảnh xuống máy"""
        img_path = response.meta['img_path']
        img_url = response.meta['img_url']
        
        try:
            with open(img_path, 'wb') as f:
                f.write(response.body)
            self.logger.info(f"Đã lưu ảnh: {img_path}")
        except Exception as e:
            self.logger.error(f"Lỗi lưu ảnh {img_path}: {e}")
    
    def save_article_html(self, response, title):
        """Lưu bài viết dưới dạng HTML"""
        try:
            # Tạo tên file HTML
            safe_title = re.sub(r'[^\w\s-]', '', title).strip()
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            safe_title = safe_title[:50]  # Giới hạn độ dài tên file
            
            # Tạo hash từ URL để tránh trùng tên
            url_hash = hashlib.md5(response.url.encode()).hexdigest()[:8]
            
            filename = f"{safe_title}_{url_hash}.html"
            filepath = os.path.join(self.articles_dir, filename)
            
            # Lưu HTML
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            self.logger.info(f"Đã lưu bài viết HTML: {filepath}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Lỗi lưu bài viết HTML: {e}")
            return None
    
    def generate_image_filename(self, img_url, img_alt):
        """Tạo tên file ảnh"""
        # Lấy extension từ URL
        ext = os.path.splitext(img_url)[1]
        if not ext:
            ext = '.jpg'  # Mặc định
        
        # Tạo tên file an toàn
        safe_alt = re.sub(r'[^\w\s-]', '', img_alt).strip()
        safe_alt = re.sub(r'[-\s]+', '-', safe_alt)
        safe_alt = safe_alt[:30]  # Giới hạn độ dài
        
        # Tạo hash từ URL
        url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
        
        return f"{safe_alt}_{url_hash}{ext}" 