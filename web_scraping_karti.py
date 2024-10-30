# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 17:15:34 2024

@author: dconl
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

# Set Firefox options
options = Options()
options.headless = True  # Run in headless mode (without opening a browser window)

# Initialize a Firefox webdriver
driver = webdriver.Chrome(options=options)

# Define the path to your local image
IMAGE_PATH = "scooter.jpg"  # Change this to the path of your local image

# Step 1: Navigate to Google Lens
driver.get("https://lens.google.com/")

# Wait for the page to load
time.sleep(2)

# Step 2: Interact with the page and upload the local image
try:
    # Find the input for uploading images
    upload_box = driver.find_element(By.XPATH, '//input[@type="file"]')

    # Upload the local image file
    upload_box.send_keys(os.path.abspath(IMAGE_PATH))

    # Wait for Lens to process the image
    time.sleep(4)

    # Step 3: Extract the links from the results
    links = driver.find_elements(By.XPATH, "//a[@href]")
    link_urls = [link.get_attribute("href") for link in links]

    amazon_links = [link for link in link_urls if "amazon" in link]
    
    for i, link in enumerate(amazon_links):
        print(f"{link}")

except Exception as e:
    print(f"Error during interaction: {str(e)}")

print("Search complete.")

driver = webdriver.Chrome(options=options)

driver.get(amazon_links[0])
time.sleep(2)

price_whole = driver.find_element(By.CLASS_NAME, "a-price-whole").text
price_fraction = driver.find_element(By.CLASS_NAME, "a-price-fraction").text
product_name = driver.find_element(By.ID, "productTitle").text

print(f"{product_name}: ${price_whole}.{price_fraction}")

