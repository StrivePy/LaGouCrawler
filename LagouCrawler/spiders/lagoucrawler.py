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
        self.pagenumber = None

    def start_requests(self):
        base_url = 'https://www.lagou.com'
        index_flag = {'index_flag': 'fetch index page', 'brower': None, 'wait': None, 'pagenumber': None}
        yield scrapy.Request(url=base_url, callback=self.parse_index, meta=index_flag, dont_filter=True)

    def parse_index(self, response):
        """
        解析第一页列表页，拿到各个招聘详情页url，并发起请求；然后进行翻页做操，拿到每页
        列表页各个窄频详情页的url，并发起请求。注意：详情页请求发起大概55个后（抓取的时
        候，一共有4页，每页15个招聘，供60个招聘详情），最后5个总是被重定向到最初始输入
        搜索关键字的页面，即使设置了DOWNLOAD_DELAY也是没用。应该是被服务器识别出了是机
        器人了，初步思路是在middlewares的process_response()函数中，通过判断response的
        status_code,对重定向的request加上代理后，再次发起request。
        :param response: 经middleware筛选并处理后的第一页详情页response
        :return:
        """
        self.pagenumber = response.meta['pagenumber']
        # 初始化spider中的brower和wait
        self.brower = response.meta['brower']
        self.wait = response.meta['wait']
        # 发起请求的request必须携带cookies，不然请求几个(5个)后，会被重定向
        # 可以从brower中或者本地文件中拿到cookies
        cookies = self.load_cookies()
        # 解析索引页各项招聘详情页url
        for url in self.parse_url(response):
            yield scrapy.Request(url=url, callback=self.parse_detail, cookies=cookies, dont_filter=True)
        # 翻页并解析
        for pagenumber in range(2, int(self.pagenumber) + 1):
            response = self.next_page()
            for url in self.parse_url(response):
                yield scrapy.Request(url=url, callback=self.parse_detail, cookies=cookies, dont_filter=True)

    def load_cookies(self):
        """
        从response的meta字典的brower属性中获得cookies，brower中的cookies是登陆获取的或者是从本地文件
        加载的
        :return: 返回包含cookies的字典
        """
        cookies = self.brower.get_cookies()
        cooke_dict = {}
        for cookie in cookies:
            cooke_dict[cookie['name']] = cookie['value']
        return cooke_dict

    def next_page(self):
        """
        用selenium模拟翻页动作。用xpath获取next_page_button控件时，花了很久时间，原因是
        span标签的class="pager_next "后引号前面有一个空格！！！
        :return:
        """
        try:
            # 用xpath找这个下一页按钮居然花了半天的时间居然是这个程序员大哥在span标签的class="pager_next "加了个空格，空格！！！
            next_page_button = self.wait.until(EC.presence_of_element_located((
                By.XPATH, '//*[@id="s_position_list"]/div[@class="item_con_pager"]/div/span[@class="pager_next "]'
            )))
            next_page_button.click()
            self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="s_position_list"]')))
            # 控制翻页速度
            time.sleep(2)
            body = self.brower.page_source
            response = HtmlResponse(url=self.brower.current_url, body=body, encoding='utf-8')
            return response
        except TimeoutException:
            pass

    @staticmethod
    def parse_url(response):
        """
        解析出每页列表页各项招聘信息的url
        :param response: 列表页response
        :return: 该列表页各项招聘详情页的url列表
        """
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
        item_loader = CompanyItemLoader(item=CompanyItem(), response=response)
        item_loader.add_xpath('company_name', '//*[@id="job_company"]/dt/a/div/h2/text()')
        item_loader.add_xpath('company_location', 'string(//*[@id="job_detail"]/dd[@class="job-address clearfix"]/div[@class="work_addr"])')
        item_loader.add_xpath('company_website', '//*[@id="job_company"]/dd/ul/li[5]/a/@href')
        item_loader.add_xpath('company_figure', '//*[@id="job_company"]/dd/ul//i[@class="icon-glyph-figure"]/parent::*/text()')
        item_loader.add_xpath('company_square', '//*[@id="job_company"]/dd/ul//i[@class="icon-glyph-fourSquare"]/parent::*/text()')
        item_loader.add_xpath('company_trend', '//*[@id="job_company"]/dd/ul//i[@class="icon-glyph-trend"]/parent::*/text()')
        item_loader.add_xpath('invest_organization', '//*[@id="job_company"]/dd/ul//p[@class="financeOrg"]/text()')
        item_loader.add_xpath('job_position', '//*[@class="position-content-l"]/div[@class="job-name"]/span/text()')
        item_loader.add_xpath('job_salary', '//*[@class="position-content-l"]/dd[@class="job_request"]/p/span[@class="salary"]/text()')
        item_loader.add_xpath('work_experience', '//*[@class="position-content-l"]/dd[@class="job_request"]/p/span[3]/text()')
        item_loader.add_xpath('degree', '//*[@class="position-content-l"]/dd[@class="job_request"]/p/span[4]/text()')
        item_loader.add_xpath('job_category', '//*[@class="position-content-l"]/dd[@class="job_request"]/p/span[5]/text()')
        item_loader.add_xpath('job_lightspot', '//*[@id="job_detail"]/dd[@class="job-advantage"]/p/text()')
        item_loader.add_xpath('job_description', 'string(//*[@id="job_detail"]/dd[@class="job_bt"]/div)')
        item_loader.add_xpath('job_publisher', '//*[@id="job_detail"]//div[@class="publisher_name"]/a/span/text()')
        item_loader.add_xpath('resume_processing', 'string(//*[@id="job_detail"]//div[@class="publisher_data"]/div[2]/span[@class="tip"])')
        item_loader.add_xpath('active_time', 'string(//*[@id="job_detail"]//div[@class="publisher_data"]/div[3]/span[@class="tip"])')
        item_loader.add_xpath('publish_date', '//*[@class="position-content-l"]/dd[@class="job_request"]/p[@class="publish_time"]/text()')
        item = item_loader.load_item()
        yield item




