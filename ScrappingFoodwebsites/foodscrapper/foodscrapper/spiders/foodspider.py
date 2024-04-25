
import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
from items import FoodscrapperItem

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class FoodSpiderAK(scrapy.Spider):
    name = 'foodspiderak'
        
    def start_requests(self):
        url = 'https://www.archanaskitchen.com/recipes'
        options = webdriver.ChromeOptions()
        options.headless = True
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        count = 0
        while True:
            count += 1
            time.sleep(3)
            # Extracting links with class name 'CoveoResultLink'
            links = driver.find_elements(By.CSS_SELECTOR, "a[itemprop='url']")
            # Extract and print the href attribute of each link
            for linkTag in links:
                href = linkTag.get_attribute("href")
                print("-------------------------NEXT---URL--------------------------")
                print(href)
                yield scrapy.Request(href)
            
            # If button available click and go to next page else break
            try:
               
             
                nextButton = driver.find_element(By.CSS_SELECTOR, "a.page-link[title='Next']")
                # driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(0.5)
                nextButton.click()
                print("-------------------------NEXT---PAGE--------------------------")
            except:
                print("Done scraping")
                break

    def parse(self, response):
        RecipeName = response.css("h1.recipe-title ::text").get()
        abcdef = response.css(".col-md-2.col-3  p *::text").getall()

        PrepTimeInMinutes = None
        CookTimeInMinutes = None
        TotalTimeInMinutes = None
        
        if len(abcdef)>0:
            PrepTimeInMinutes = re.search(r'\d+(?=\D*$)', (abcdef)[0]).group(0)
        if len(abcdef)>1:
            CookTimeInMinutes = re.search(r'\d+(?=\D*$)',  (abcdef)[1]).group(0)
        if len(abcdef)>2:
            TotalTimeInMinutes = re.search(r'\d+(?=\D*$)',  (abcdef)[2]).group(0)

        Servings = None
        if response.css(".col-md-2.col-4.recipeYield  p *::text").get():
            Servings = re.search(r'\d+(?=\D*$)', response.css(".col-md-2.col-4.recipeYield  p *::text").get()).group(0)
        
        Cuisine = response.css("div.cuisine span ::text").get()
        Course = response.css("div.course span ::text").get()
        Diet = response.css("div.diet span ::text").get()
        IngredientsRaw = response.css("div.col-md-4.col-12.recipeingredients *::text").getall()
        Ingredients = [item.strip() for item in IngredientsRaw if item.strip()]
        InstructionsRaw = response.css(".col-md-8.col-12.recipeinstructions  *::text").getall()
        Instructions = [item.strip() for item in  InstructionsRaw if item.strip()]
        Tags= "None"
        YouTubeLink = response.css("div.recipe-image  a ::attr(href)").get() if response.css("div.recipe-image  a ::attr(href)").get() else None




        
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
             Course = Course,
             Diet = Diet
        )
        yield data_item

    

class FoodSpiderRB(scrapy.Spider):
    name = 'foodspiderrb'
        
    def start_requests(self):
        url = 'https://ranveerbrar.com/recipes/'
        options = webdriver.ChromeOptions()
        options.headless = True
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        count = 0
        while True:
            count += 1
            time.sleep(3)
            # Extracting links with class name 'CoveoResultLink'
            links = driver.find_elements(By.CSS_SELECTOR, ".rc_thumb_wrap.rb_thumb_wrap a")
            # Extract and print the href attribute of each link
            for linkTag in links:
                href = linkTag.get_attribute("href")
                yield scrapy.Request(href)
            
            # If button available click and go to next page else break
            try:
                nextButton = driver.find_element(By.CSS_SELECTOR, "li[class='active next_page']")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(0.5)
                nextButton.click()
            except:
                print("Done scraping")
                break

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



from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from scrapy.utils.log import configure_logging
import os 
file_path = "foodscrapper/foodscrapper/spiders/scraped_data.csv"

# Check if the file exists before attempting to delete it
if os.path.exists(file_path):
    # Attempt to delete the file
    try:
        os.remove(file_path)
        print(f"File '{file_path}' deleted successfully.")
    except OSError as e:
        print(f"Error: {file_path} : {e.strerror}")
else:
    print(f"The file '{file_path}' does not exist.")



configure_logging()
settings = get_project_settings()
process = CrawlerProcess(settings)
process.crawl(FoodSpiderRB)
process.crawl(FoodSpiderAK)
process.start()  # the script will block here until all crawling jobs are finished

