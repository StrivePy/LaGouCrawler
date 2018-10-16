# 简介

用Scrapy框架实现一个爬虫，来爬取拉钩网招聘详情页中的公司名称、职位名称、薪资待遇、岗位需求等详细信息，并将抓取的数据存入Mongodb数据库。用Selenium解决拉钩网页面动态加载问题。用阿布云服务器解决请求频繁，爬虫被重定向问题。

# 各模块功能

* **LagouCrawler.spiders.lagoucrawler.py**

  > 爬虫模块
  
    * *start_requests()*
    
      > 对[https://www.lagou.com](https://www.lagou.com) 发起请求，并指定parse_index为回调函数，该请求的meta中有index_flag属性，用于在  middlewares中过滤出该请求，来完成相应的输入关键字，点击搜索按钮进入索引页等操作。
      
    * *parse_index()*
    
      > 索引页面的回调函数，用于解析第一页列表页中的详情url，然后执行翻页动作，并解析每一页中的详情url，然后对每个url发起请求，并指定parse_detail为回调函数。
      
    * *next_page()*
    
      > 翻页函数，用Selenium模拟翻页。
      
    * *parse_url()*
    
      > url解析函数，用于解析出列表页中各个招聘详情的url。
      
    * *parse_detail()*
    
      > 详情页解析函数，利用ItemLoader和Xpath来提取详情页面中公司名称、职位名称、岗位需求等详细信息。
      
* **LagouCrawler.items.py**

  > Item模块，定义提取数据的各个字段
    
    * CompanyItemLoader类
    
      > 定义的ItemLoader类，指定默认输出为TakeFires。
     
    * CompanyItem类
    
      > 定义详情页中的提取字段，每个字段提取后，先进过**input_processor**和**output_processor**处理后，再由ItemLoader指定的**defaulf_output_processor**进行处理。
      
* **LagouCrawler.middlewares.py**

  > 中间件模块，可以在这个模块中自定义SpiderMiddlewares和DownloaderMiddlewares，这里主要实现DownloaderMiddlewares。
  
    * LagoucrawlerDownloaderMiddleware类
      
      > 下载中间件，在发起初始请求后，过滤出带有index_flag的请求，然后进行相应的切换城市、输入关键字、点击搜索按钮等操作，最后进入搜索职位索引页，并将该索引页返回。

        * *is_logined()*
          
          > 通过右上角是否显示用户名判断是否为登陆状态。
          
        * *login_lagou()*
        
          > 用Selenium模拟点击，进行拉钩网的登陆操作，登陆成功后，将cookies保存为本地文件。
          
        * *save_cookies()*
        
          > 将cookies保存为本地文件
          
        * *fetch_index_page()*
        
          > 进行城市切换、职位关键字输入、点击搜索等操作，进入搜索职位列表页后，将该页面的Response返回。
          
        * *load_cookies()*
        
          > 加载本地cookies文件到Selenium的brower。
          
        * *process_request()*
        
          > DownloaderMiddleware的核心方法，
