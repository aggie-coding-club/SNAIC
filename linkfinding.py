# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 17:15:34 2024

@author: dconl
"""
import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse

# Set Chrome options
options = Options()
options.add_argument("--headless")  # Run in headless mode

# Initialize a Chrome webdriver
driver = webdriver.Chrome(options=options)

# Define the path to your local image
IMAGE_PATH = "imgs/bag.jpg"  # Change this to the path of your local image

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

    # domain grouping
    links_by_domain = {}
    filename = 'links.csv'

    for link in link_urls:
        domain = urlparse(link).netloc
        if domain not in links_by_domain:
            links_by_domain[domain] = []
        links_by_domain[domain].append(link)

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Domain', 'Link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for domain in sorted(links_by_domain.keys()):
            for link in links_by_domain[domain]:
                writer.writerow({'Domain': domain, 'Link': link})

    print("Links have been written to", filename)

except Exception as e:
    print(f"Error during interaction: {str(e)}")

print("Search complete.")

driver.quit()
