import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
from items import FoodscrapperItem

class FoodSpiderRB(scrapy.Spider):
    name = 'foodspiderrb'
        
    def start_requests(self):
        url = 'https://ranveerbrar.com/recipes/'
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--no-sandbox')
        self.driver = webdriver.Remote(
            command_executor='http://host.docker.internal:4444/wd/hub',
            options=options
        )
        self.driver.get(url)
        count = 0
        # while True:
        count += 1
        time.sleep(3)
        # Extracting links with class name 'CoveoResultLink'
        links = self.driver.find_elements(By.CSS_SELECTOR, ".rc_thumb_wrap.rb_thumb_wrap a")
        # Extract and print the href attribute of each link
        for linkTag in links:
            href = linkTag.get_attribute("href")
            yield scrapy.Request(href)
            
            # If button available click and go to next page else break
            # try:
            #     nextButton = self.driver.find_element(By.CSS_SELECTOR, "li[class='active next_page']")
            #     self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            #     time.sleep(0.5)
            #     nextButton.click()
            # except:
            #     print("Done scraping")
            #     break

    def parse(self, response):
        RecipeName = response.css('h1::text').get()
        PrepTimeInMinutes = re.search(r'\d+(?=\D*$)', response.css('.recipe_time_left label::text').get()).group(0)
        CookTimeInMinutes = re.search(r'\d+(?=\D*$)', response.css('.recipe_time_left label:nth-child(2)::text').get()).group(0)
        TotalTimeInMinutes = re.search(r'\d+(?=\D*$)', response.css('.recipe_time_right span::text').get()).group(0)
        Servings = re.search(r'\d+(?=\D*$)', response.css('.recipe_intro_other:nth-child(1)  span::text').get()).group(0)
        
        Cuisine = response.css('.recipe_intro_other  a::text').getall()
        Ingredients = response.css('div.ingredients_wrap p *::text').getall()
        Instructions = response.css('div.process_wrap  *::text').getall()
        Tags= response.css('div.recipe_tags_wrap a *::text').getall()
        YouTubeLink =  response.css('div.recipe_media_wrap a[href*="youtube.com/watch"]::attr(href)').get()

        data_item = FoodscrapperItem(
            RecipeName =  RecipeName,
            PrepTimeInMinutes = PrepTimeInMinutes,
            CookTimeInMinutes =   CookTimeInMinutes,
            TotalTimeInMinutes =  TotalTimeInMinutes,
           Servings = Servings,
           Cuisine =  Cuisine,
           Ingredients =  Ingredients,
            Instructions =  Instructions,
            Tags= Tags,
            YouTubeLink = YouTubeLink,
            Course = None,
             Diet = None
        )
        yield data_item
