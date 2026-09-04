import pandas as pd
import requests
import os

def download_webpages(csv_file_path, download_directory):
    # Create the directory if it does not exist
    os.makedirs(download_directory, exist_ok=True)
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)
    
    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        url = row['Link URL']
        try:
            # Send a GET request to the URL
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            # Construct filename based on row index and save the webpage content
            file_path = os.path.join(download_directory, f'webpage_{index}.html')
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(response.text)
            print(f"Downloaded and saved: {file_path}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {url}. Error: {e}")

# Path to the CSV file
csv_file_path = r"C:\text\NJ\Atlantic Cape\noncredit\noncredit.csv"

# Directory to save the downloaded HTML files
download_directory = r"C:\text\NJ\Atlantic Cape\noncredit\noncreditHTML"

# Call the function
download_webpages(csv_file_path, download_directory)
