# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import time
from scrapy.http import HtmlResponse
from selenium.webdriver import Chrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


class LagoucrawlerDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self, username, password, city, job_keywords):
        # 用户名
        self.username = username
        # 用户密码
        self.password = password
        # 选择城市
        self.city = city
        # 搜索关键字
        self.job_keywords = job_keywords
        # Chrome浏览器初始化
        self.brower = Chrome()
        # Chrome浏览器窗口最大化
        self.brower.maximize_window()
        # Chrome浏览器等待加载超时时间
        self.wait = WebDriverWait(self.brower, 5)

    @classmethod
    def from_crawler(cls, crawler):
        # 从setting文件提取出用户名、用户密码、搜索城市和搜索职位
        return cls(
            username=crawler.settings.get('USERNAME'),
            password=crawler.settings.get('PASSWORD'),
            city=crawler.settings.get('CITY'),
            job_keywords=crawler.settings.get('JOB_KEYWORDS')
        )

    def is_logined(self, request, spider):
        """
        通过判断右上角是否显示用户名判断是否为登陆状态,并初始化整个程序的brower实例
        :param request: 初始请求request，其meta包含index_page属性
        :param spider:
        :return: 已经登陆返回True， 否则返回False
        """
        self.brower.get(request.url)
        try:
            # 关掉城市选择窗口
            box_close = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cboxClose"]')))
            box_close.click()
            time.sleep(1)
            login_status = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="lg_tbar"]/div/ul/li[1]/a')))
            # 若右上角显示为登陆，则说明用户还没有登陆
            if login_status.text is '登陆':
                return False
            else:
                return True
        except TimeoutException as e:
            spider.logger.info('Locate Username Element Failed：%s' % e.msg)
            return False

    def login_lagou(self, spider):
        try:
            # 点击进入登陆页面
            login_status = self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, '登陆')))
            login_status.click()
            # 输入用户名
            username = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@data-propertyname="username"]/input')))
            username.send_keys(self.username)
            # 输入用户密码
            password = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@data-propertyname="password"]/input')))
            password.send_keys(self.password)
            # 点击登陆按钮
            submit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@data-propertyname="submit"]')))
            submit_button.click()
            time.sleep(5)
        except TimeoutException as e:
            spider.logger.info('Locate Login Element Failed: %s' % e.msg)

    def fetch_index_page(self, request, spider):
        try:
            # 判断是否需要切换城市
            city_location = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="lg_tnav"]/div/div/div/strong')))
            if city_location.text is not self.city:
                time.sleep(2)
                # 根据搜索城市定位到相应元素并点击切换
                city_choice = self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, self.city)))
                city_choice.click()
                # 定位关键字输入框并输入关键字
                keywords_input = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_input"]')))
                keywords_input.send_keys(self.job_keywords)
                # 定位搜索按钮并点击
                keywords_submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="search_button"]')))
                keywords_submit.click()
                # 确定下一页已经加载出来，确保能够提取到数据
                # self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="s_position_list"]//span[@class="pager_next"]')))
                # 将brower和wait通过response传递到parse_detail函数，进行后续的翻页解析使用
                request.meta['brower'] = self.brower
                request.meta['wait'] = self.wait
                time.sleep(10)
                body = self.brower.page_source
                # 返回初始搜索页面，在parse_detail函数中进行相关信息的解析
                response = HtmlResponse(
                    url=self.brower.current_url,
                    body=body,
                    encoding='utf-8',
                    request=request
                )
                return response
        except TimeoutException as e:
            spider.logger.info('Locate Index Element Failed：%s' % e.msg)

    def process_request(self, request, spider):
        # 过滤出初始的登陆、切换索引页的request
        if 'index_flag' in request.meta.keys():
            # 判断是否为登陆状态，若未登陆则进行登陆操作
            if self.is_logined(request, spider) is not True:
                # 登陆lagou网
                self.login_lagou(spider)
                # 登陆成功后的索引页的响应体，若不登录，请求响应提详情页面的url时，会重定向到登陆页面
                response = self.fetch_index_page(request, spider)
                return response
        else:
            # 必须返回一个None，让其它request能够继续被处理
            return None

