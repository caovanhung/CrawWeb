import json
import os
from bs4 import BeautifulSoup

def analyze_existing_data():
    """Phân tích dữ liệu đã có từ spider"""
    
    # Kiểm tra file JSON
    if not os.path.exists('output/articles.json'):
        print("Không tìm thấy file output/articles.json")
        print("Hãy chạy spider trước: scrapy crawl phap_luat -o output/articles.json")
        return
    
    # Đọc file JSON
    with open('output/articles.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    print(f"Tìm thấy {len(articles)} bài viết để phân tích")
    
    if not articles:
        print("Không có bài viết nào trong file JSON")
        return
    
    # Phân tích 3 bài viết đầu tiên
    for i, article in enumerate(articles[:3]):
        print(f"\n{'='*60}")
        print(f"PHÂN TÍCH BÀI VIẾT {i+1}: {article['title'][:50]}...")
        print(f"URL: {article['url']}")
        print(f"{'='*60}")
        
        # Phân tích dữ liệu đã có
        print(f"\n1. DỮ LIỆU ĐÃ TRÍCH XUẤT:")
        print(f"   Title: {article['title']}")
        print(f"   Summary: {article['summary'][:100]}...")
        print(f"   Date: {article['date']}")
        print(f"   Source: {article['source']}")
        print(f"   Số hình ảnh: {len(article['images'])}")
        
        if article['images']:
            print(f"   Hình ảnh đầu tiên: {article['images'][0]}")
        
        # Kiểm tra file HTML nếu có
        html_filename = f"output/debug_article_{i+1}.html"
        if os.path.exists(html_filename):
            print(f"\n2. PHÂN TÍCH FILE HTML: {html_filename}")
            try:
                with open(html_filename, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Phân tích cấu trúc
                print(f"   Tổng số thẻ h1: {len(soup.find_all('h1'))}")
                print(f"   Tổng số thẻ h2: {len(soup.find_all('h2'))}")
                print(f"   Tổng số thẻ h3: {len(soup.find_all('h3'))}")
                print(f"   Tổng số thẻ p: {len(soup.find_all('p'))}")
                print(f"   Tổng số thẻ img: {len(soup.find_all('img'))}")
                
                # Tìm các class phổ biến
                common_classes = ['title', 'content', 'article', 'summary', 'date', 'time', 'author']
                for class_name in common_classes:
                    elements = soup.find_all(class_=lambda x: x and class_name in x)
                    if elements:
                        print(f"   Class chứa '{class_name}': {len(elements)} elements")
                
                # Phân tích hình ảnh
                images = soup.find_all('img')
                if images:
                    print(f"\n3. PHÂN TÍCH HÌNH ẢNH:")
                    content_images = 0
                    other_images = 0
                    
                    for img in images:
                        src = img.get('src', '')
                        alt = img.get('alt', '').lower()
                        
                        # Kiểm tra xem có phải hình ảnh nội dung không
                        if any(keyword in alt for keyword in ['quảng cáo', 'ad', 'banner', 'logo', 'icon', 'button']):
                            other_images += 1
                        elif img.find_parent('aside') or img.find_parent('.sidebar'):
                            other_images += 1
                        else:
                            content_images += 1
                    
                    print(f"   Hình ảnh nội dung: {content_images}")
                    print(f"   Hình ảnh khác (ads, sidebar): {other_images}")
                    
                    # Hiển thị một số hình ảnh nội dung
                    print(f"\n   Một số hình ảnh nội dung:")
                    count = 0
                    for img in images:
                        if count >= 3:  # Chỉ hiển thị 3 hình đầu
                            break
                        src = img.get('src', '')
                        alt = img.get('alt', '')
                        if src and not any(keyword in alt.lower() for keyword in ['quảng cáo', 'ad', 'banner', 'logo', 'icon']):
                            print(f"     - src: {src[:80]}...")
                            print(f"       alt: {alt[:50]}...")
                            count += 1
                
            except Exception as e:
                print(f"   Lỗi khi đọc file HTML: {e}")
        else:
            print(f"\n2. Không tìm thấy file HTML: {html_filename}")
            print("   Spider chưa lưu HTML của bài viết này")
    
    print(f"\n{'='*60}")
    print("KẾT LUẬN VÀ ĐỀ XUẤT:")
    print("1. Spider đang hoạt động tốt và trích xuất được dữ liệu")
    print("2. Để tối ưu hóa hình ảnh, cần:")
    print("   - Lọc hình ảnh theo alt text (loại bỏ ads, banners)")
    print("   - Chỉ lấy hình ảnh trong vùng nội dung chính")
    print("   - Kiểm tra kích thước và chất lượng hình ảnh")
    print("3. Có thể cải thiện selector để lấy nội dung chính xác hơn")

if __name__ == "__main__":
    analyze_existing_data() 