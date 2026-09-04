import csv
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = Options()
chrome_options.add_argument("--headless")

driver_path = r"C:\chromedriver-win64\chromedriver.exe"
service = Service(driver_path)

#driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Define the CSV file name and the subdirectory for saving HTML files
csv_file = r"C:\text\NJ\Bergen\ContinuingEd\extracted_CE_links.csv"
programs_dir = 'CE_HTML'

# Create the subdirectory if it doesn't exist
if not os.path.exists(programs_dir):
    os.makedirs(programs_dir)

# Set up Selenium WebDriver options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no browser window)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("start-maximized")  # Start maximized for full content rendering
chrome_options.add_argument("enable-automation")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-browser-side-navigation")
chrome_options.add_argument("--disable-features=NetworkService")

# Specify the path to the ChromeDriver if it's not in your PATH
#driver_path = r"C:\chromedriver-win64\chromedriver.exe"
#service = Service(driver_path)  # Use Service to specify the ChromeDriver path

# Function to download HTML content from a URL using Selenium
def download_html_with_selenium(url, file_path):
    try:
        # Initialize the WebDriver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Open the URL
        driver.get(url)
        
        # Wait for page to fully load (increase time if needed)
        time.sleep(3)
        
        # Save the page source (HTML) after fully rendering
        html_content = driver.page_source
        
        # Create directories if they do not exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
        print(f'Successfully downloaded {url} to {file_path}')
        
        # Close the WebDriver for the current page
        driver.quit()
    except Exception as e:
        print(f'Failed to download {url}: {e}')

# Open the CSV file and process each row
with open(csv_file, 'r', newline='', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file)
    for row in reader:
        program_url = row['URL']
        if program_url:  # Check if the URL is not empty
            program_name = row['Link Name'].replace(' ', '_').replace('/', '_').replace(':', '_')  # Use link name for the file name
            file_name = f'{program_name}.html'
            file_path = os.path.join(programs_dir, file_name)
            download_html_with_selenium(program_url, file_path)

print('All URLs have been processed.')
