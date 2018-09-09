# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import time
import random
import os
import json
import base64
from scrapy.http import HtmlResponse
from scrapy.exceptions import IgnoreRequest
from selenium.webdriver import Chrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from fake_useragent import UserAgent


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
        """
        从setting.py文件提取出用户名、用户密码、搜索城市和搜索职位
        :param crawler:
        :return:
        """
        return cls(
            username=crawler.settings.get('USERNAME'),
            password=crawler.settings.get('PASSWORD'),
            city=crawler.settings.get('CITY'),
            job_keywords=crawler.settings.get('JOB_KEYWORDS')
        )

    def is_logined(self, request, spider):
        """
        初始请求时，总会弹出切换城市的窗口，所以先关掉它，然后通过判断右上角是否显示
        用户名判断是否为登陆状态,并初始化整个程序的brower实例
        :param request: 初始请求request，其meta包含index_page属性
        :param spider:
        :return: 已经登陆返回True， 否则返回False
        """
        self.brower.get(request.url)
        try:
            # time.sleep(1)
            # 关掉城市选择窗口
            box_close = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cboxClose"]')))
            box_close.click()
            # time.sleep(1)
            # 获取右上角的登录状态
            login_status = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="lg_tbar"]/div/ul/li[1]/a')))
            # 若右上角显示为登陆，则说明用户还没有登陆
            if login_status.text == '登录':
                return False
            else:
                return True
        except TimeoutException as e:
            # 二次请求，不会出现地址框，需要重新设计
            spider.logger.info('Locate Username Element Failed：%s' % e.msg)
            return False

    def login_lagou(self, spider):
        """
        用selenium模拟登陆流程，并将登陆成功后的cookies保存为本地文件。
        :param spider:
        :return:
        """
        try:
            # 设置等待时间，否则会出现登陆元素查找不到的异常
            time.sleep(2)
            # 点击进入登录页面
            login_status = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="loginToolBar"]//a[@class="button bar_login passport_login_pop"]')))
            login_status.click()
            # 输入用户名
            username = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@data-propertyname="username"]/input')))
            username.send_keys(self.username)
            # 输入用户密码
            password = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@data-propertyname="password"]/input')))
            password.send_keys(self.password)
            # 点击登陆按钮
            submit_button = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@data-propertyname="submit"]/input')))
            submit_button.click()
            # time.sleep(1)
            # 获取登录成功后的cookies
            cookies = self.brower.get_cookies()
            # 保存登陆后的cookies
            self.save_cookies(cookies)
        except TimeoutException as e:
            spider.logger.info('Locate Login Element Failed: %s' % e.msg)

    @staticmethod
    def save_cookies(cookies):
        """
        登陆成功后，将cookie保存为本地文件，供下次程序运行或者以后使用
        :param cookies:
        :return:
        """
        path = os.getcwd() + '/cookies/'
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path + 'lagou.txt', 'w') as f:
            f.write(json.dumps(cookies))

    def fetch_index_page(self, request, spider):
        """
        该函数使用selenium完成城市切换，搜索关键字输入并点击搜索按钮操作。如果点击搜索按钮后，
        页面没有成功跳转，则会因为149行的代码，抛出NoSuchElementException，而在load_cookies()
        函数报一个NoneType没有get_cookies()的错误。原因是response是空的。
        :param request:
        :param spider:
        :return:
        """
        try:
            # 判断是否需要切换城市
            city_location = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="lg_tnav"]/div/div/div/strong')))
            if city_location.text != self.city:
                time.sleep(1)
                city_change = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="changeCity_btn"]')))
                city_change.click()
                # 根据搜索城市定位到相应元素并点击切换
                # time.sleep(1)
                city_choice = self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, self.city)))
                city_choice.click()
            time.sleep(1)
            # 定位关键字输入框并输入关键字
            keywords_input = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_input"]')))
            keywords_input.send_keys(self.job_keywords)
            # time.sleep(1)
            # 定位搜索按钮并点击,有时候点击后页面不会发生跳转，原因大概是被重定向了。
            keywords_submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="search_button"]')))
            keywords_submit.click()
            # 跳转到列表页等待待抓取的内容元素加载完成,如果被重定向,则跳转不到该页面，会报NoSuchElementException
            self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="s_position_list"]')))
            pagenumber = self.wait.until(EC.presence_of_element_located((
                By.XPATH, '//*[@id="s_position_list"]/div[@class="item_con_pager"]/div/span[@class="pager_next "]/preceding-sibling::span[1]'
            )))
            # 获取一共有多少页，供通过response传递到parse_detail函数，进行后续的翻页解析使用
            request.meta['pagenumber'] = pagenumber.text
            # 将brower和wait通过response传递到parse_detail函数，进行后续的翻页解析使用
            request.meta['brower'] = self.brower
            request.meta['wait'] = self.wait
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
            spider.logger.info('Locate Index Element Failed And Use Proxy')
        # except NoSuchElementException:
            # 如果捕捉到该异常，说明页面被重定向了，没有正常跳转。
            # 给request添加代理，并返回该request，重新请求初始请求。
            proxy = 'http://219.141.153.41:80'
            request.meta['proxy'] = proxy
            return request

    def load_cookies(self, path):
        """
        加载本地cookies文件，实现免登录访问
        :param path: 本地cookies文件路径
        :return:
        """
        with open(path, 'r') as f:
            cookies = json.loads(f.read())
            for cookie in cookies:
                cookies_dict = {'name': cookie['name'], 'value': cookie['value']}
                self.brower.add_cookie(cookies_dict)

    def process_request(self, request, spider):
        """
        middleware的核心函数，每个request都会经过该函数。此函数过滤出初始request和详情页request，
        对于初始request进行验证登陆、cookies等一系列操作，然后将最后获取到的索引页response返回，对
        于详情页的request则，不做任何处理。注意：对于详情页的request，识别出来后，必须返回一个None，
        表示不干预操作，等待合适的downloader下载该request请求。
        :param request:
        :param spider:
        :return:
        """
        # 过滤出初始的登陆、切换索引页的request
        if 'index_flag' in request.meta.keys():
            # 判断是否为登陆状态，若未登陆则判断是否有cookies文件存在
            if not self.is_logined(request, spider):
                path = os.getcwd() + '/cookies/lagou.txt'
                # 若cookies文件存在，则加载cookie文件，否则进行登陆操作
                if os.path.exists(path):
                    self.load_cookies(path)
                else:
                    # 登陆lagou网
                    self.login_lagou(spider)
                # 登陆成功后的索引页的响应体，若不登录，请求响应提详情页面的url时，会重定向到登陆页面
                response = self.fetch_index_page(request, spider)
                return response
        else:
            # 必须返回一个None，让其它request能够继续被处理
            return None


class RandomProxyMiddleware(object):

    def __init__(self, proxy_list=None):
        self.proxy_list = proxy_list

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            proxy_list=crawler.settings.get('PROXY_LIST')
        )

    def process_response(self, request, response, spider):
        """
        在被默认RedirectMiddleware重定向之前或者被服务器发现被禁之后，给改请求添加代理
        后重新请求，若再次被重定向或者被禁，则直接舍弃。
        :param request:
        :param response:
        :param spider:
        :return: 设置代理的request
        """
        if response.status in [302, 403, 500, 503]:
            if not request.meta.get('auto_proxy'):
                proxy = random.choice(self.proxy_list)
                request.meta.update({'auto_proxy': True, 'proxy': proxy})
                new_request = request.replace(meta=request.meta)
                spider.logger.debug('The <{} {}> Use Proxy: {}'.format(response.status, request.url, proxy))
                return new_request
            else:
                spider.logger.debug('The <{} {}> After Use Proxy Still Redirect'.format(response.status, request.url))
                raise IgnoreRequest
        return response


class RandomUserAgentMiddleware(object):
    """
    给每一个request添加随机的User-Agent
    """

    def __init__(self, ua_type=None):
        super(RandomUserAgentMiddleware, self).__init__()
        self.ua = UserAgent()
        self.ua_type = ua_type

    @classmethod
    def from_crawler(cls, crawler):
        """
        获取setting.py中配置的RANDOM_UA_TYPE,如果没有配置，则使用默认值random
        :param crawler:
        :return:
        """
        return cls(
            ua_type=crawler.settings.get('RANDOM_UA_TYPE', 'random')
        )

    def process_request(self, request, spider):
        """
        UserAgentMiddleware的核心方法，getattr(A, B)相当于A.B，也就是获取A
        对象的B属性，在这就相当于ua.random
        :param request:
        :param spider:
        :return:
        """
        request.headers.setdefault('User-Agent', getattr(self.ua, self.ua_type))
        spider.logger.debug('The <{}> User Agent Is: {}'.format(request.url, getattr(self.ua, self.ua_type)))


class AbuYunProxyMiddleware(object):
    """
    接入阿布云代理服务器，该服务器动态IP1秒最多请求5次。需要在setting中设置下载延迟
    """

    def __init__(self, settings):
        self.proxy_server = settings.get('PROXY_SERVER')
        self.proxy_user = settings.get('PROXY_USER')
        self.proxy_pass = settings.get('PROXY_PASS')
        self.proxy_authorization = 'Basic ' + base64.urlsafe_b64encode(
            bytes((self.proxy_user + ':' + self.proxy_pass), 'ascii')).decode('utf8')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
             settings=crawler.settings
        )

    def process_request(self, request, spider):
        request.meta['proxy'] = self.proxy_server
        request.headers['Proxy-Authorization'] = self.proxy_authorization
        spider.logger.debug('The {} Use AbuProxy And proxyAuth is {}'.format(request.url, self.proxy_authorization))
