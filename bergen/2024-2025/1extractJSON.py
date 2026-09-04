from seleniumwire import webdriver  # Use selenium-wire instead of selenium
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import csv

# Path to ChromeDriver
chromedriver_path = r"C:\chromedriver-win64\chromedriver.exe"

# Set up Selenium WebDriver with selenium-wire
service = Service(chromedriver_path)
options = webdriver.ChromeOptions()
# Uncomment the line below to run in headless mode if needed
# options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)

# Load the web page
html_file_path = r"https://catalog.bergen.edu/content.php?catoid=7&navoid=304"
driver.get(html_file_path)

# Wait for the main content to load
time.sleep(3)

# Initialize set to collect JSON endpoints
json_endpoints = set()

# Locate and click on each "+" button to expand sections
try:
    # Find all elements for the "+" buttons using the filter__icon class
    plus_buttons = driver.find_elements(By.CLASS_NAME, 'filter__icon')
    for button in plus_buttons:
        button.click()  # Click to expand and reveal content
        time.sleep(2)   # Short pause to let content load

        # Intercept JSON requests in network traffic
        for request in driver.requests:
            if request.response and "_format=json" in request.url:
                json_endpoints.add(request.url)

except Exception as e:
    print("Error expanding button or locating JSON link:", e)

# Write JSON endpoints to CSV
output_csv = 'json_endpoints.csv'
with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["JSON Endpoint"])
    for endpoint in json_endpoints:
        writer.writerow([endpoint])

print(f"JSON endpoints have been saved to {output_csv}")

# Close the driver
driver.quit()
