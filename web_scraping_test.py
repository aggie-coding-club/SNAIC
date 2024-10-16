import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

# Set Firefox options
options = Options()
options.headless = True  # Run in headless mode (without opening a browser window)

# Initialize a Firefox webdriver
driver = webdriver.Firefox(options=options)

# Define the path to your local image
IMAGE_PATH = "scooter.jpg"  # Change this to the path of your local image

# Step 1: Navigate to Google Lens
driver.get("https://lens.google.com/")

# Wait for the page to load
time.sleep(5)

# Step 2: Interact with the page and upload the local image
try:
    # Find the input for uploading images
    upload_box = driver.find_element(By.XPATH, '//input[@type="file"]')

    # Upload the local image file
    upload_box.send_keys(os.path.abspath(IMAGE_PATH))

    # Wait for Lens to process the image
    time.sleep(10)

    # Step 3: Extract the links from the results
    links = driver.find_elements(By.XPATH, "//a[@href]")
    link_urls = [link.get_attribute("href") for link in links]

    amazon_links = [link for link in link_urls if "amazon" in link]
    
    for i, link in enumerate(link_urls):
        print(f"{link}")

except Exception as e:
    print(f"Error during interaction: {str(e)}")

finally:
    # Close the browser
    driver.quit()

print("Search complete.")
