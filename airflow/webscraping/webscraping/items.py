# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class DataItem(Item):
    topic = Field()
    year = Field()
    level = Field()
    introduction = Field()
    learning_outcomes = Field()
    summary = Field()
    link_summary = Field()
    link_pdf = Field()
