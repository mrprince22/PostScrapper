import os
import time
from datetime import timedelta
import datetime
import re
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
class Scraper:
    def __init__(self):
        self.page_url = 'https://www.facebook.com/VicoSotto/'
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("window-size=1920,1080")
        self.options.add_argument('--headless')
        self.options.add_argument('--lang=en')
        self.options.add_argument('--incognito')
        # self.options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options = self.options)
        self.driver.maximize_window()
        self.driver.get(self.page_url)
        time.sleep(3)
    
    def close_button(self):
        # Click on the close button to show the page behind
        close_button_xpath = '//*[@aria-label="Close"]'
        close_button_xpath = '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/div'
        self.driver.find_element(By.XPATH, close_button_xpath).click()
        time.sleep(3)
    
    def get_last_post_url(self):
        post_url_xpath = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div/div[1]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a'
        url = self.driver.find_element(By.XPATH,post_url_xpath)
        self.url, self.url_element = (url.get_attribute('href'), url)

    def scrape_post(self)->None:
        self.post = {}
        
        def convert_to_date(time):
            post_date = datetime.date.today()
            if 'd' in time:
                days_ago = int(time[0])
                post_date -= timedelta(days = days_ago)
            
            post_date = post_date.strftime("%Y-%m-%d")
            year, month, day = map(int, post_date.split('-'))            
            date = datetime.date(year, month, day)
            week_day = date.strftime("%A")
            ret = f"{week_day}, {day}-{month}-{year}"
            return (ret, (f'{day}_{month}_{year}'))
        
        date = self.url_element.text
        date, file_name = convert_to_date(str(date))
        self.post['title'] = date
        self.post['file_name'] = file_name

        self.driver.get(self.url)
        time.sleep(3)
        
        try:
            body_xpath = '//*[@data-testid="post_message"]'
            body = self.driver.find_element(By.XPATH, body_xpath).text
            body = re.sub(r"(https?://\S+)", r"<a href='\1'>\1</a>", body)
        except NoSuchElementException: # This is now a video
            try:
                close_button_xpath = '/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div[1]/div'
                close_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, close_button_xpath)))
                close_button.click()
                time.sleep(2)
            except :
                pass
            
            time.sleep(3)
            see_more_xpath = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[2]/div[1]/div/div/div[2]/div[1]/div[3]/div[2]/span/div'
            try:
                see_more_button = self.driver.find_element(By.XPATH, see_more_xpath)
                see_more_button.click()
                time.sleep(3)
            except:
                try:
                    see_more_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(By.XPATH, see_more_xpath))
                    see_more_button.click()
                    time.sleep(2)
                except:
                    pass
            
            try:
                body_xpath = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[2]/div[1]/div/div/div[2]/div[1]/div[3]/div[1]'
                body = self.driver.find_element(By.XPATH, body_xpath).text
            except:
                body = "N/A"
        
        body += f"<br><br> <a href = '{self.url}'> Original Post </a>"

        self.post['body'] = f"<p> {body} </p>"
        
        images_xpath = '//*[@rel="theater"]'
        try:
            images = self.driver.find_elements(By.XPATH, images_xpath)
        except:
            images = []
        
        
        def get_image_url(image_url):
            
            self.driver = webdriver.Chrome(options = self.options)
            self.driver.get(image_url)
            time.sleep(3)
            try:
                image = self.driver.find_element(By.TAG_NAME, 'img')
                return image.get_attribute('src')
            except:
                return "#"
            
        
            
        self.post['images'] = [get_image_url(image.get_attribute('href')) for image in images]
    
    def export_to_html(self, output_dir)-> None:
        
        
        output = f"""
        <!DOCTYPE html>
        <html>
            <head>
            <link href = 'style.css' rel = 'stylesheet'>
            <title>Post</title>
            </head>
        <body>
        <header>
        <h1>{self.post['title']}</h1>
        </header>
        <article>
        {self.post['body']}
        <div id = 'images_container'>
        <!--  <meta name="viewport" content="width=device-width, initial-scale=1.0"> -->
        """
        
        
        for image in self.post['images']:
            output += f"<img src = {image}>\n"
        
        ending = """
        </div>
        </article>
        </body>
        </html>
        
        """
        output += ending
        
        output_path = f"{output_dir}/{self.post['file_name']}.html"
        if os.path.exists(output_path):
            print(f"File: {output_path}  already scraped before!")
            return
        
        with open(output_path, 'w') as f:
                f.write(output)
        print(f"Exported {output_path}")
        
        
    
    
    def close(self):
        self.driver.quit()


