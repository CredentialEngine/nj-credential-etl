from seleniumwire import webdriver  # Use selenium-wire instead of selenium
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
import time

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

# Load the main web page
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

# Visit each program URL and capture pathways files
for relative_url in program_urls:
    try:
        # Construct the absolute URL and visit it
        full_url = f"https://catalog.bergen.edu/{relative_url}"
        driver.get(full_url)
        time.sleep(2)  # Allow the page to load

        # Capture and save pathways files
        for request in driver.requests:
            if request.response and "pathways" in request.url:
                # Save the response content
                safe_filename = request.url.replace("https://", "").replace("/", "_").replace("?", "_")
                pathways_file_name = os.path.join(output_folder, f"{safe_filename}.pathways")
                with open(pathways_file_name, "wb") as file:
                    file.write(request.response.body)
                print(f"Pathways file saved: {pathways_file_name}")

    except Exception as e:
        print(f"Error processing URL {full_url}: {e}")

# Close the driver
driver.quit()
