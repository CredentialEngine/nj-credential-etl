import os
import pandas as pd
import requests

def download_pdfs(csv_file_path, download_folder):
    # Ensure the download folder exists
    os.makedirs(download_folder, exist_ok=True)

    # Load the CSV file
    df = pd.read_csv(csv_file_path)

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        link = row['Credential Link']
        if link.endswith('.pdf'):  # Ensuring it is a PDF link
            # Create a local filename
            filename = os.path.basename(link)
            local_path = os.path.join(download_folder, filename)

            # Check if file already exists to avoid re-downloading it
            if not os.path.exists(local_path):
                try:
                    # Download the file
                    response = requests.get(link, stream=True)
                    response.raise_for_status()  # Check for request errors

                    # Save the file
                    with open(local_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"Downloaded {filename} to {local_path}")
                except requests.RequestException as e:
                    print(f"Failed to download {link}. Error: {e}")
            else:
                print(f"File already exists: {filename}")
        else:
            print(f"Skipped non-PDF link: {link}")

# Specify the path to your CSV file and the download folder
csv_file_path = r"C:\text\NJ\Warren\credentials\credentials.csv"
download_folder = r"C:\text\NJ\Warren\credentials\CredentialPDF"

# Call the function
download_pdfs(csv_file_path, download_folder)
