import pandas as pd
import requests
import os

def download_webpages(csv_file_path, output_dir):
    # Read the CSV file to get the URLs
    df = pd.read_csv(csv_file_path)
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Loop through each URL in the 'Type URL' column
    for url in df['Type URL']:
        if pd.notna(url):
            try:
                # Send a GET request to the URL
                response = requests.get(url)
                response.raise_for_status()  # Raise an error on bad status
                
                # Create a filename from the URL by extracting the last part after the last '/'
                filename = url.split('/')[-1] + '.html'
                
                # Define the path to save the file
                file_path = os.path.join(output_dir, filename)
                
                # Write the response content to the file
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded and saved {filename}")
            except requests.RequestException as e:
                print(f"Failed to download {url}: {str(e)}")
        else:
            print("Invalid URL encountered.")

# Define the paths
csv_file_path = r"C:\text\NJ\Atlantic Cape\credentials\credentials_output.csv"
output_dir = r"C:\text\NJ\Atlantic Cape\credentials\CredentialsHTML"

# Call the function
download_webpages(csv_file_path, output_dir)
