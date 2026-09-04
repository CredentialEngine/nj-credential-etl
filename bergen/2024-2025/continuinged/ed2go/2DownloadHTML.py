import requests
import os

# Base URL with placeholders for pagination
BASE_URL = "https://onlinecareertraining.bergen.edu/training-programs/?PAGE_SIZE=50&PAGE_NUMBER={}"

# Directory to save the HTML files
OUTPUT_DIR = r"C:\text\NJ\Bergen\ContinuingEd\ed2go\pages"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define the range of pages to download (adjust as needed)
START_PAGE = 1
END_PAGE = 10  # Change this to the total number of pages you need

for page_number in range(START_PAGE, END_PAGE + 1):
    # Construct the URL for the current page
    url = BASE_URL.format(page_number)
    
    try:
        # Fetch the page
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Save the HTML content to a file
        output_file = os.path.join(OUTPUT_DIR, f"page_{page_number}.html")
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(response.text)
        
        print(f"Page {page_number} saved successfully.")
    
    except requests.exceptions.RequestException as e:
        print(f"Failed to download page {page_number}: {e}")

print("All pages downloaded.")
