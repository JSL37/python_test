import time
import pymongo
from selenium import webdriver
from selenium.webdriver.common.by import By
from amazoncaptcha import AmazonCaptcha
from scrapy.exceptions import DropItem

class MongoPipeline(object):
    def __init__(self, connection_string, database):
        self.connection_string = connection_string
        self.database = database
        self.browser = webdriver.Chrome()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            connection_string=crawler.settings.get('MONGODB_CONNECTION_STRING'),
            database=crawler.settings.get('MONGODB_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.connection_string)
        self.db = self.client[self.database]

    def process_item(self, item, spider):
        name = item.__class__.__name__
        if self.check_logic(item['asin']):
            self.db[name].insert_one(dict(item))
            return item
        else:
            raise DropItem("Invalid data")

    def close_spider(self, spider):
        self.client.close()
        self.browser.quit()

    def check_logic(self, asin):
        amazon_link = f'https://www.amazon.com/dp/{asin}'
        self.browser.get(amazon_link)
        time.sleep(1)  # 等待页面加载
        html = self.browser.page_source
        if ('we just need to make sure you' in html or
                'Geben Sie die angezeigten Zeichen im Bild ein:' in html or
                'Ingresar los caracteres' in html):
            print('验证码')
            self.handle_captcha(asin)
        else:
            print('无需验证码，直接继续执行爬取流程...')
            self.process_page(html, asin)

    def handle_captcha(self, asin):
        print('处理验证码...')
        img = self.browser.find_element(By.CSS_SELECTOR, 'div > img.captcha-image')
        hrefs = img.get_attribute('src')
        print('验证码图片链接:', hrefs)
        yzm_number = self.get_captcha()
        print('验证码识别结果:', yzm_number)
        if yzm_number:
            yzm_input = self.browser.find_element(By.CSS_SELECTOR, '#captchacharacters')
            yzm_input.send_keys(yzm_number)
            time.sleep(1)  # 等待输入验证码
            yzm_submit = self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"].a-button-input')
            yzm_submit.click()
            time.sleep(1)  # 等待页面加载
            print('验证码处理完成，继续执行爬取流程...')
            html = self.browser.page_source
            self.process_page(html, asin)
        else:
            print('验证码解决失败，等待重新尝试...')
            time.sleep(5)
            self.handle_captcha(asin)

    def process_page(self, html, asin):
        if ('alt="Dogs of Amazon"' in html or
                '您输入的网址不是我们网站上的有效网页' in html or
                'The Web address' in html):
            print('--变狗--' + asin)
            return True
        else:
            print('未检测到变狗，继续执行爬取流程...')
            return False

    def get_captcha(self):
        captcha = AmazonCaptcha.fromdriver(self.browser)
        solution = captcha.solve()
        if solution == 'Not solved':
            return False
        return solution
