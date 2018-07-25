# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose


class CompanyItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class CompanyItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    # 公司名称
    company_name = Field()
    # # 公司地址
    # company_location = Field()
    # # 公司官网
    # company_website = Field()
    # # 公司规模
    # company_scale = Field()
    # # 公司领域
    # company_field = Field()
    # # 公司阶段
    # company_stage = Field()
    # # 投资机构
    # invest_organization = Field()
    #
    # # 岗位名称
    # job_position = Field()
    # # 岗位薪资
    # job_salary = Field()
    # # 经验需求
    # work_experience = Field()
    # # 学历需求
    # degree = Field()
    # # 工作性质
    # job_category = Field()
    #
    # # 职位亮点
    # job_lightspot = Field()
    # # 职位描述
    # job_description = Field()
    #
    # # 职位发布者
    # job_publisher = Field()
    # # 聊天意愿
    # chat_will = Field()
    # # 简历处理
    # resume_processing = Field()
    # # 活跃时段
    # active_time = Field()
