import pandas as pd
import requests
import os

# Path to the CSV file
csv_file_path = r"C:\text\NJ\Union\noncredit\ugotclass\Union_UGotClass_Courses.csv"

# Directory to save the HTML files
output_directory = r"C:\text\NJ\Union\noncredit\ugotclass\CourseCertHTML"

# Create the directory if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Read the CSV file
df = pd.read_csv(csv_file_path)

def sanitize_filename(url):
    """Sanitize the URL to be safe for use as a filename."""
    invalid_chars = "<>:\"/\\|?*"
    for char in invalid_chars:
        url = url.replace(char, '_')
    return url

# Loop through the URLs in the DataFrame
for index, row in df.iterrows():
    url = row['URL']
    # Sanitize the URL to use as a filename
    sanitized_filename = sanitize_filename(url)
    filename = os.path.join(output_directory, f"{sanitized_filename}.html")
    
    # Set up headers for the request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    
    # Send a GET request to fetch the HTML
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Write the content to a file
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(response.text)
    else:
        print(f"Failed to download {url}")

print("Download complete.")
