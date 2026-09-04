import os
import pandas as pd
import requests
from urllib.parse import urlparse, parse_qs, unquote

def url_to_filename(url):
    """
    Convert a URL into a valid filename by incorporating the entire URL.
    """
    parsed_url = urlparse(url)
    # Include path and query in filename
    filename = parsed_url.netloc + parsed_url.path.replace('/', '_') + '?' + parsed_url.query.replace('&', '_').replace('=', '-')
    # Decode URL-encoded characters
    filename = unquote(filename)
    # Remove unwanted characters
    filename = filename.replace('?', '_').replace('/', '_').replace(':', '_').replace('*', '_').replace('<', '_').replace('>', '_').replace('|', '_').strip('_')
    return filename + ".html"

# Define the CSV file path
csv_path = r"C:\text\NJ\Camden\noncredit\courses\noncredit_course_links.csv"
# Define the directory to save the downloaded HTML files
output_dir = r"C:\text\NJ\Camden\noncredit\courses\CoursesHTML"


# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Load URLs from the CSV file
df = pd.read_csv(csv_path)

# Loop through the URLs in the DataFrame
for index, row in df.iterrows():
    url = row['URL']
    filename = url_to_filename(url)
    file_path = os.path.join(output_dir, filename)  # Construct file path with the new filename

    # Send a GET request to the URL
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Write the content of the response to an HTML file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(response.text)
            print(f"Downloaded {url} to {file_path}")
        else:
            print(f"Failed to download {url} (Status code: {response.status_code})")
    except Exception as e:
        print(f"Error downloading from {url}: {e}")

print("Finished downloading all webpages.")
