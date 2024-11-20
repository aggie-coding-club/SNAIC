import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from urllib.parse import urlparse

def link_find():
    options = Options()
    options.add_argument("--headless")
    options.headless = True
    
    service = Service('geckodriver')
    driver = webdriver.Firefox(service=service)

    IMAGE_PATH = "imgs/car.png"

    driver.get("https://lens.google.com/")

    time.sleep(2)

    try:
        upload_box = driver.find_element(By.XPATH, '//input[@type="file"]')
        upload_box.send_keys(os.path.abspath(IMAGE_PATH))
        time.sleep(6)

        links = driver.find_elements(By.XPATH, "//a[@href]")
        link_urls = [link.get_attribute("href") for link in links]

        #link_urls = [link for link in link_urls if "amazon" in urlparse(link).netloc]

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

    print("Search complete")

    driver.quit()
