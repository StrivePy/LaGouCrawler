# 简介

用Scrapy框架实现一个爬虫，来爬取拉钩网招聘详情页中的公司名称、职位名称、薪资待遇、岗位需求等详细信息，并将抓取的数据存入Mongodb数据库。用Selenium解决拉钩网页面动态加载问题。用阿布云服务器解决请求频繁，爬虫被重定向问题。

# 各模块功能

* LagouCrawler.spiders.lagoucrawler.py

  > 爬虫模块
  
    * start_requests()
    
      > 对[https://www.lagou.com](https://www.lagou.com) 发起请求，并指定parse_index为回调函数，该请求的meta中有index_flag属性，用于在  middlewares中过滤出该请求，来完成相应的输入关键字，点击搜索按钮进入索引页等操作。
      
    * parse_index()
    
      > 索引页面的回调函数，用于解析第一页列表页中的详情url，然后执行翻页动作，并解析每一页中的详情url，然后对每个url发起请求，并指定parse_detail为回调函数。
      
    * next_page()
    
    > 翻页函数，用Selenium模拟翻页。
      
    * parse_url()
    
      > url解析函数，用于解析出列表页中各个招聘详情的url。
      
    * parse_detail()
    
      > 详情页解析函数，利用ItemLoader和Xpath来提取详情页面中公司名称、职位名称、岗位需求等详细信息。
      
* LagouCrawler.items.py

  > Item模块，定义提取数据的各个字段
    
    * CompanyItemLoader类
    
      > 定义的Itemloader类，指定默认输出为TakeFires
