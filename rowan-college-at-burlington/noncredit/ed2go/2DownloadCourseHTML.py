import os
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


# File paths
csv_file_path = r"C:\text\NJ\Rowan College at Burlington\noncredit\ed2go\rcbcenrich_ed2go_Courses.csv"
output_directory = r"C:\text\NJ\Rowan College at Burlington\noncredit\ed2go\coursesHTML"

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Set up Selenium WebDriver
options = webdriver.ChromeOptions()
#options.add_argument('--headless')  # Run in headless mode (no browser UI)
#options.add_argument('--disable-gpu')
#options.add_argument('--window-size=1920,1080')
#options.add_argument('--log-level=3')  # Suppress logs
# Initialize Chrome options

#driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#capabilities = DesiredCapabilities.CHROME.copy()
#capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
#driver = webdriver.Chrome(desired_capabilities=capabilities, options=options)
#driver_path = r"C:\chromedriver-win64\chromedriver.exe"
#driver = webdriver.Chrome(service=Service(driver_path, desired_capabilities=capabilities, options=options))
# Initialize the driver with automatic driver management
chrome_install = ChromeDriverManager().install()

folder = os.path.dirname(chrome_install)
chromedriver_path = os.path.join(folder, "chromedriver.exe")

#service = ChromeService(chromedriver_path)

driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)


# Read the CSV and process links
with open(csv_file_path, 'r', encoding='utf-8-sig') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        # Extract the Course Link
        course_link = row.get("Course Link", "").strip()
        course_name = row.get("Course Name", "course").strip().replace(" ", "_").replace("/", "_").replace(":", "-")
        html_file_path = os.path.join(output_directory, f"{course_name}.html")

        # Skip if file already exists
        if os.path.exists(html_file_path):
            print(f"File already exists, skipping: {html_file_path}")
            continue

        if course_link:
            try:
                # Navigate to the course link
                driver.get(course_link)
                time.sleep(3)  # Allow time for the page to load
                print(driver.page_source[:500])  # Print the first 500 characters

                # Capture the page source
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "html")))
                page_source = driver.page_source
               
                # Save the page source to a uniquely named file
                with open(html_file_path, 'w', encoding='utf-8') as html_file:
                    html_file.write(page_source)
                print(f"Downloaded and saved: {html_file_path}")
                
            except Exception as e:
                print(f"Failed to process {course_link}: {e}")

# Clean up WebDriver
driver.quit()
print("Download complete.")

