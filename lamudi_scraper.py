import pandas as pd
import numpy as np
import re
import requests
from bs4 import BeautifulSoup as bs
import time
from tqdm import tqdm

from src.scraper.scraper import scraper

def main():
    # Prompt the user for inputs
    province = input("Please enter the province: ")
    property_type = input("Please enter the property type: ")
    num = int(input("Please enter the number of properties to scrape: "))

    # Call the scraper function with user inputs
    df = scraper(province, property_type, num)
    print(df.head(10))

if __name__ == "__main__":
    main()