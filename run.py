from scrapy.cmdline import execute


def main():
    spider_name = 'lagoucrawler'
    cmd_string = 'scrapy crawl {spider_name}'.format(spider_name=spider_name)
    execute(cmd_string.split())


if __name__ == '__main__':
    main()
