# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
from datetime import datetime
import os


class BaotintucPipeline:
    def __init__(self):
        self.file = None
        self.articles = []
        
    def open_spider(self, spider):
        # Tạo thư mục output nếu chưa tồn tại
        os.makedirs('output', exist_ok=True)
        
        # Tạo tên file với timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'output/baotintuc_phap_luat_{timestamp}.json'
        
        self.file = open(filename, 'w', encoding='utf-8')
        self.file.write('[\n')
        self.first_item = True
        
    def close_spider(self, spider):
        if self.file:
            self.file.write('\n]')
            self.file.close()
            
    def process_item(self, item, spider):
        # Chuyển đổi item thành dict
        item_dict = dict(item)
        
        # Thêm dấu phẩy nếu không phải item đầu tiên
        if not self.first_item:
            self.file.write(',\n')
        else:
            self.first_item = False
            
        # Ghi item vào file JSON
        json.dump(item_dict, self.file, ensure_ascii=False, indent=2)
        
        return item 