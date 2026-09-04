import os
import pandas as pd
import requests
from urllib.parse import urlparse, unquote

def sanitize_filename(url):
    """
    Creates a valid filename from a URL by extracting parts of the URL and replacing special characters.
    """
    parsed_url = urlparse(url)
    filename = parsed_url.netloc + parsed_url.path.replace('/', '_').replace('?', '_').replace('&', '_').strip('_')
    return unquote(filename) + '.html'

# Define paths
csv_path = r"C:\text\NJ\Atlantic Cape\noncredit\ed2go\course_details.csv"
output_dir = r"C:\text\NJ\Atlantic Cape\noncredit\ed2go\coursesHTMLCourse"

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Load URLs from the CSV file
df = pd.read_csv(csv_path)

# Headers to simulate a request from a web browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Loop through the URLs in the DataFrame
for url in df['Course URL'].dropna():
    filename = sanitize_filename(url)
    file_path = os.path.join(output_dir, filename)

    # Send a GET request with headers
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # Write the content to an HTML file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(response.text)
            print(f"Downloaded and saved: {url} to {file_path}")
        else:
            print(f"Failed to download {url} (Status code: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")

print("Finished downloading all webpages.")
