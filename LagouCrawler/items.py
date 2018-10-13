# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import datetime
from scrapy import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join


def formate_date(value):
    """
    根据提取到的发布时间，若是当天发布则是H:M格式，则获取当天日期的年月日然后返回，否则是Y:M:D格式，
    则直接返回该年月日
    :param value: 提取到的时间字符串
    :return: 格式化后的年月日
    """
    if ':' in value:
        now = datetime.datetime.now()
        publish_date = now.strftime('%Y-%m-%d')
        publish_date += '(今天)'
        return publish_date
    else:
        return value


class CompanyItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class CompanyItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    # 公司名称
    company_name = Field(
        input_processor=MapCompose(lambda x: x.replace(' ', ''), lambda x: x.strip())
    )
    # 公司地址
    company_location = Field(
        input_processor=MapCompose(lambda x: x.replace(' ', ''), lambda x: x.replace('\n', ''), lambda x: x[:-4])
    )
    # 公司官网
    company_website = Field()
    # 公司规模
    company_figure = Field(
        input_processor=MapCompose(lambda x: x.replace(' ', ''), lambda x: x.replace('\n', '')),
        output_processor=Join('')
    )
    # 公司领域
    company_square = Field(
        input_processor=MapCompose(lambda x: x.replace(' ', ''), lambda x: x.replace('\n', '')),
        output_processor=Join('')
    )
    # 公司阶段
    company_trend = Field(
        input_processor=MapCompose(lambda x: x.replace(' ', ''), lambda x: x.replace('\n', '')),
        output_processor=Join('')
    )
    # 投资机构
    invest_organization = Field()

    # 岗位名称
    job_position = Field()
    # 岗位薪资
    job_salary = Field(
        input_processor=MapCompose(lambda x: x.strip())
    )
    # 经验需求
    work_experience = Field(
        input_processor=MapCompose(lambda x: x.replace(' /', ''))
    )
    # 学历需求
    degree = Field(
        input_processor=MapCompose(lambda x: x.replace(' /', ''))
    )
    # 工作性质
    job_category = Field()

    # 职位亮点
    job_lightspot = Field()
    # 职位描述
    job_description = Field(
        input_processor=MapCompose(lambda x: x.replace('\xa0\xa0\xa0\xa0', '').replace('\xa0', ''), lambda x: x.replace('\n', '').replace(' ', ''))
    )

    # 职位发布者
    job_publisher = Field()
    # 发布时间
    publish_date = Field(
        input_processor=MapCompose(lambda x: x.replace('\xa0 ', '').strip(), lambda x: x[:-6], formate_date)
    )
    # # 聊天意愿
    # chat_will = Field()
    # 简历处理
    resume_processing = Field(
        input_processor=MapCompose(lambda x: x.replace('\xa0', '').strip())
    )
    # 活跃时段
    active_time = Field(
        input_processor=MapCompose(str.strip)
    )
