import pandas as pd
import requests
import os
from urllib.parse import urlparse

def sanitize_filename(filename):
    # Replace or remove invalid characters for Windows filenames
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')  # Replace with underscore or another suitable character
    return filename

def get_last_folder_name(url):
    # Extract the last folder name from the URL path
    path = urlparse(url).path.rstrip('/')
    return os.path.basename(path) if path else 'default'

def download_html_pages(csv_file_path, output_dir):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the CSV file to get URLs
    df = pd.read_csv(csv_file_path)
    
    # Define headers to avoid 403 errors
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Loop through the rows in the DataFrame
    for index, row in df.iterrows():
        url = row['Program Link']
        
        try:
            # Send a GET request to the URL with headers
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error on bad status
            
            # Get filename from the last folder name in the URL
            filename = sanitize_filename(get_last_folder_name(url)) + '.html'
            file_path = os.path.join(output_dir, filename)
            
            # Write the response content to the file
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded and saved: {filename}")
        except requests.RequestException as e:
            print(f"Failed to download {url}: {str(e)}")

# Define the CSV file path and the output directory path
csv_file_path = r"C:\text\NJ\Morris\credentials\programs\credentials_parsed.csv"
output_dir = r"C:\text\NJ\Morris\credentials\programs\CredentialHTML"

# Call the function to download webpages
download_html_pages(csv_file_path, output_dir)
