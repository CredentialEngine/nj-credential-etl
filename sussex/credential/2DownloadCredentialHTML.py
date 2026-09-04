import pandas as pd
import requests
import os

def download_html_pages(csv_file_path, output_dir):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the CSV file to get URLs and credential names
    df = pd.read_csv(csv_file_path)
    
    # Loop through the rows in the DataFrame
    for index, row in df.iterrows():
        url = row['Link']
        credential_name = row['Credential Name']
        
        try:
            # Send a GET request to the URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an error on bad status
            
            # Create a filename from the credential name
            filename = credential_name.replace('/', '_') + '.html'  # Replace '/' with '_' to avoid file path issues
            file_path = os.path.join(output_dir, filename)
            
            # Write the response content to the file
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded and saved: {filename}")
        except requests.RequestException as e:
            print(f"Failed to download {url}: {str(e)}")

# Define the CSV file path and the output directory path
csv_file_path = r"C:\text\NJ\Sussex\credential\credentials_parsed.csv"
output_dir = r"C:\text\NJ\Sussex\credential\CredentialHTML"

# Call the function to download webpages
download_html_pages(csv_file_path, output_dir)
