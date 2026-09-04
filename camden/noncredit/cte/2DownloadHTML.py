import pandas as pd
import requests
import os
from urllib.parse import urlparse

def sanitize_filename(url):
    """Create a sanitized filename from a URL."""
    parsed_url = urlparse(url)
    filename = parsed_url.netloc + parsed_url.path.replace('/', '_')
    return filename.strip('_') + '.html'

# Path to the CSV file
csv_path = r"C:\text\NJ\Camden\noncredit\CTE\program_details.csv"
# Directory to save the downloaded HTML files
output_dir = r"C:\text\NJ\Camden\noncredit\CTE\programHTML"

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Load URLs from the CSV file
df = pd.read_csv(csv_path)

# Loop through the URLs in the DataFrame
for url in df['Program URL']:
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        # Check if the request was successful
        if response.status_code == 200:
            # Create a sanitized filename from the URL
            filename = sanitize_filename(url)
            # Define the full path to save the file
            file_path = os.path.join(output_dir, filename)
            # Write the content of the response to an HTML file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(response.text)
            print(f"Downloaded {url} to {file_path}")
        else:
            print(f"Failed to download {url} (Status code: {response.status_code})")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

print("Finished downloading all webpages.")
