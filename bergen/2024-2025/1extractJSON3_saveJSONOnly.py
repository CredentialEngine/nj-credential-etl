from seleniumwire import webdriver  # Use selenium-wire instead of selenium
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
import time
import requests

# Path to ChromeDriver
chromedriver_path = r"C:\chromedriver-win64\chromedriver.exe"

# Set up Selenium WebDriver with selenium-wire
service = Service(chromedriver_path)
options = webdriver.ChromeOptions()
# Uncomment the line below to run in headless mode if needed
# options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)

# Base folder to save files
output_folder = "output"
os.makedirs(output_folder, exist_ok=True)


# Load the web page
html_file_path = r"https://catalog.bergen.edu/content.php?catoid=7&navoid=304"
driver.get(html_file_path)


# Wait for the main content to load
time.sleep(3)

# Parse the page with BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser")

# Locate program links
program_links = soup.find_all('a', href=True)
program_urls = [
    link['href'] for link in program_links
    if 'program' in link['href']
]

# Initialize set to collect JSON endpoints
json_endpoints = set()

# Visit each program URL and save its HTML and JSON data
for relative_url in program_urls:
    try:
        # Construct the absolute URL and visit it
        full_url = f"https://catalog.bergen.edu/{relative_url}"
        driver.get(full_url)
        time.sleep(2)

        # Save HTML content
        #safe_filename = full_url.replace("https://", "").replace("/", "_").replace("?", "_")
        #html_file_name = os.path.join(output_folder, f"{safe_filename}.html")
        #with open(html_file_name, "w", encoding="utf-8") as html_file:
        #    html_file.write(driver.page_source)
        #print(f"HTML saved: {html_file_name}")

        # Intercept JSON requests in network traffic
        for request in driver.requests:
            #swtich to 'pathways' instead of json in URL
            if request.response and "pathways" in request.url:
                if request.url not in json_endpoints:  # Avoid duplicates
                    json_endpoints.add(request.url)

    except Exception as e:
        print(f"Error processing URL {full_url}: {e}")

# Download JSON files
for endpoint in json_endpoints:
    try:
        response = requests.get(endpoint)
        if response.status_code == 200:
            # Generate a safe filename from the URL
            safe_filename = endpoint.replace("https://", "").replace("/", "_").replace("?", "_")
            json_file_name = os.path.join(output_folder, f"{safe_filename}.json")
            with open(json_file_name, "w", encoding="utf-8") as json_file:
                json_file.write(response.text)
            print(f"JSON saved: {json_file_name}")
        else:
            print(f"Failed to download JSON: {endpoint}, Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading JSON from {endpoint}: {e}")

# Close the driver
driver.quit()
