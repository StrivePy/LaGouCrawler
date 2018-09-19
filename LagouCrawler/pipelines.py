# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient


class LagoucrawlerPipeline(object):

    def __init__(self, host=None, db=None, collection=None):
        self.mongo_uri = host
        self.mongo_db = db
        self.mongo_collection = collection
        self.client = None
        self.db = None
        self.collection = None

    @classmethod
    def from_crawler(cls, crawler):
        """
        通过该函数，获取在settings.py文件中定义的Mongodb地址、数据库名称和表名
        :param crawler:
        :return:
        """
        return cls(
            host=crawler.settings.get('MONGO_URI'),
            db=crawler.settings.get('MONGO_DB'),
            collection=crawler.settings.get('MONGO_COLLECTION')
        )

    def open_spider(self, spider):
        """
        在spider打开时，完成mongodb数据库的初始化工作。
        :param spider:
        :return:
        """
        self.client = MongoClient(host=self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.mongo_collection]

    def process_item(self, item, spider):
        """
        pipeline的核心函数，在该函数中执行对item的一系列操作，例如存储等。
        :param item: parse_detail函数解析出来的item
        :param spider: 抓取该item的spider
        :return: 返回处理后的item，供其它pipeline再进行处理(如果有的话)
        """
        # 以公司名称做为查询条件
        condition = {'company_name': item.get('company_name')}
        # upsert参数设置为True后，若数据库中没有该条记录，会执行插入操作；
        # 同时，使用update_one()函数，也可以完成去重操作。
        result = self.collection.update_one(condition, {'$set': item}, upsert=True)
        spider.logger.debug('The Matched Item is: {} And The Modified Item is: {}'.format(result.matched_count, result.modified_count))
        return item

    def close_spider(self, spider):
        """
        在spider关闭时，关闭mongodb数据连接。
        :param spider:
        :return:
        """
        self.client.close()
