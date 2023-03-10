from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import config

PAGE_URL_SUFFIX = '-pagina-'
HTML_EXTENSION = '.html'

FEATURE_UNIT_DICT = {
    'm²': 'square_meters_area',
    'amb': 'rooms',
    'dorm': 'bedrooms',
    'baño': 'bathrooms',
    'baños': 'bathrooms',
    'coch': 'parking',
}


class Scraper:
    def __init__(self, browser, base_url):
        self.browser = browser
        self.base_url = base_url

    def scrape_page(self, page_number):
        if page_number == 1:
            page_url = f'{self.base_url}{HTML_EXTENSION}'
        else:
            page_url = f'{self.base_url}{PAGE_URL_SUFFIX}{page_number}{HTML_EXTENSION}'

        print(f'URL: {page_url}')

        page = self.browser.get(page_url)
        soup = BeautifulSoup(page.text, "html.parser")
        estate_posts = soup.find_all('div', attrs={'data-posting-type': True})
        estates = []
        for estate in estate_posts[:5]:
            estates.append(self.parse_estate(estate))
        return estates
    
    def parse_estate(self, estate_post):
    # find div with anything data-qa atributte
        url = estate_post.get_attribute_list('data-to-posting')[0]
        print(url)
        features = {}
        features['url'] = url
        data_qa = estate_post.find_all('div', attrs={'data-qa': True})
        for data in data_qa:
            label = data['data-qa']
            if label == 'POSTING_CARD_FEATURES':
                features['Features']= self.parse_features(data.get_text())
            elif label == 'POSTING_CARD_DESCRIPTION':
                features['Description']= data.get_text()
            elif label == 'POSTING_CARD_PRICE':
                features['Price']= data.get_text()
            elif label == 'expensas':
                features['Expenses']= data.get_text()
            elif label == 'POSTING_CARD_LOCATION':
                features['Location']= data.get_text()
        images = self.get_images("https://www.zonaprop.com.ar"+url)
        features['Images'] = images
                    
        return features

    def get_images(self, url):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(config.PATH)
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # images = driver.find_elements(By.XPATH, "/html/head/link[11]")
        images = driver.find_elements(By.TAG_NAME, 'div')
        imgs=[]
        for image in images:
            if image.get_attribute('src') is not None:
                imgs.append(image.get_attribute('src'))
        return imgs
        #get src of images in zonaprop
        
        

    def parse_features(self, features):
        # features_dict = {'total_square_meters':0, 'covered_square_meter':0, 'rooms':0, 'bedrooms':0,'bathrooms':0, 'parking':0}
        features_appearance = {'square_meters_area': [],
                               'rooms': 0, 'bedrooms': 0, 'bathrooms': 0, 'parking': 0}
        features_matches  = re.compile(r'(\d+\.?\d*)\s(\w+)').findall(features)

        for feature in features_matches:
            try:
                if feature[1] == 'm²':
                    features_appearance[FEATURE_UNIT_DICT[feature[1]]].append(int(feature[0]))
                else:
                    features_appearance[FEATURE_UNIT_DICT[feature[1]]] = feature[0]
            except KeyError:
                pass
        return features_appearance


        

