import pandas as pd 
import requests
import os
import time

def sanitize_filename(filename):
    # More robust sanitization to handle newlines and other problematic characters
    invalid_chars = '<>:"/\\|?*\n\t'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()

def extract_unique_id_from_url(url):
    # Extract the numerical ID from the URL
    try:
        # Assuming the URL ends with a number followed by a slash or ends directly with a number
        return url.strip('/').split('/')[-1]
    except IndexError:
        return 'unknown'

def download_html_pages(csv_file_path, output_dir, attempts=3, delay=3):
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(csv_file_path)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for index, row in df.iterrows():
        url = row['Program Link']
        credential_name = row['Program Name']
        unique_id = extract_unique_id_from_url(url)
        filename = sanitize_filename(f"{credential_name}_{unique_id}.html")
        file_path = os.path.join(output_dir, filename)
        
        if os.path.exists(file_path):
            print(f"Skipping download, file already exists: {filename}")
            continue
        
        success = False
        for attempt in range(attempts):
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded and saved: {filename}")
                success = True
                break  # Break the retry loop on success
            except requests.RequestException as e:
                print(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                time.sleep(delay)  # Wait before retrying
        if not success:
            print(f"Failed to download {url} after {attempts} attempts.")

# Define the CSV file path and the output directory path
csv_file_path = r"C:\text\NJ\Passaic\credentials\credentials_parsed.csv"
output_dir = r"C:\text\NJ\Passaic\credentials\CredentialHTML"

# Call the function to download webpages
download_html_pages(csv_file_path, output_dir)
