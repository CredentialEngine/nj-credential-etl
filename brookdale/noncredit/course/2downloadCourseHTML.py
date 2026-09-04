import os
import pandas as pd
import requests

# Path to the CSV file
csv_path = r'C:\text\NJ\Brookdale\noncredit\course\extracted_urls.csv'

# Directory to save the downloaded HTML files
output_dir = r'C:\text\NJ\Brookdale\noncredit\course\courseHTML'

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Load URLs from the CSV file
df = pd.read_csv(csv_path)

# Iterate over the URLs in the DataFrame
for index, row in df.iterrows():
    url = row['URL']
    filename = os.path.join(output_dir, f"page_{index + 1}.html")

    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Write the content of the response to an HTML file
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(response.text)
        print(f"Downloaded {url} to {filename}")
    else:
        print(f"Failed to download {url} (Status code: {response.status_code})")

print("Finished downloading all webpages.")
import os
import pandas as pd
import requests

# Path to the CSV file
csv_path = r'C:\text\NJ\Brookdale\noncredit\course\extracted_urls.csv'

# Directory to save the downloaded HTML files
output_dir = r'C:\text\NJ\Brookdale\noncredit\course\courseHTML'

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Load URLs from the CSV file
df = pd.read_csv(csv_path)

# Iterate over the URLs in the DataFrame
for index, row in df.iterrows():
    url = row['URL']
    filename = os.path.join(output_dir, f"page_{index + 1}.html")

    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Write the content of the response to an HTML file
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(response.text)
        print(f"Downloaded {url} to {filename}")
    else:
        print(f"Failed to download {url} (Status code: {response.status_code})")

print("Finished downloading all webpages.")
