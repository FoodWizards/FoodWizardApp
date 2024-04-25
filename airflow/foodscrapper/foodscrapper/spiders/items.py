# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class FoodscrapperItem(scrapy.Item):
    RecipeName =  Field()
    PrepTimeInMinutes = Field()
    CookTimeInMinutes = Field()
    TotalTimeInMinutes = Field()
    Servings = Field()
    Cuisine = Field()
    Ingredients = Field()
    Instructions = Field()
    Tags = Field()
    YouTubeLink = Field()
    Course = Field()
    Diet = Field()