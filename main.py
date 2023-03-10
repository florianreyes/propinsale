import requests
from bs4 import BeautifulSoup
import pandas as pd
import cloudscraper
import time
from browser import Browser
from scraper import Scraper
import streamlit as st

URL = "https://www.zonaprop.com.ar/departamentos-venta-capital-federal.html"

def main(url):
    browser = Browser()
    response = Scraper(browser, url).scrape_page(1)
    # make a df from the response
    df = pd.DataFrame(response)
    st.dataframe(df)
    print(df)
    

if __name__ == "__main__":
    main(URL)