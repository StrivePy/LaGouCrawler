# -*- coding: utf-8 -*-
import scrapy
import time
from ..items import CompanyItem, CompanyItemLoader
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from scrapy.http import HtmlResponse


class LagoucrawlerSpider(scrapy.Spider):
    def parse(self, response):
        pass

    name = 'lagoucrawler'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.brower = None
        self.wait = None

    def start_requests(self):
        base_url = 'https://www.lagou.com'
        index_flag = {'index_flag': 'fetch index page', 'brower': None, 'wait': None}
        # 调试完毕，回调函数切换回parse_index
        yield scrapy.Request(url=base_url, callback=self.parse, meta=index_flag)

    def parse_index(self, response):
        # 解析索引页各项招聘详情页url
        for url in self.parse_url(response):
            yield scrapy.Request(url=url, callback=self.parse_detail)
        # 翻页并解析
        self.brower = response.meta['brower']
        self.wait = response.meta['wait']
        # for pagenumber in range(2, 6):
        #     response = self.next_page()
        #     for url in self.parse_url(response):
        #         yield scrapy.Request(url=url, callback=self.parse_detail)

    def next_page(self):
        try:
            next_page_button = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="s_position_list"]//span[@class="pager_next"]')))
            time.sleep(1)
            next_page_button.click()
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="s_position_list"]//span[@class="pager_next"]')))
            body = self.brower.page_source
            response = HtmlResponse(url=self.brower.current_url, body=body, encoding='utf-8')
            return response
        except TimeoutException:
            self.next_page()

    @staticmethod
    def parse_url(response):
        url_selector = response.xpath('//*[@id="s_position_list"]/ul/li')
        url_list = []
        for selector in url_selector:
            url = selector.xpath('.//div[@class="p_top"]/a/@href').extract_first()
            url_list.append(url)
        return url_list

    @staticmethod
    def parse_detail(response):
        """
        解析每一页各个招聘信息的详情
        :param response: 每个列表页的HtmlResponse实例
        :return: 各个公司招聘详情生成器
        """
        item_loader = CompanyItemLoader(item=CompanyItem(), selector=response)
        item_loader.add_xpath('company_name', '//*[@id="job_company"]/dt/a/div/h2/text()')
        item = item_loader.load_item()
        yield item




