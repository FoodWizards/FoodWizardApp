
import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
from items import FoodscrapperItem

class FoodSpiderAK(scrapy.Spider):
    name = 'foodspiderak'
        
    def start_requests(self):
        url = 'https://www.archanaskitchen.com/recipes'
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
        while True:
            count += 1
            time.sleep(3)
            # Extracting links with class name 'CoveoResultLink'
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[itemprop='url']")
            # Extract and print the href attribute of each link
            for linkTag in links:
                href = linkTag.get_attribute("href")
                print("-------------------------NEXT---URL--------------------------")
                print(href)
                yield scrapy.Request(href)

            # If button available click and go to next page else break
            try:
                nextButton = self.driver.find_element(By.CSS_SELECTOR, "a.page-link[title='Next']")
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
