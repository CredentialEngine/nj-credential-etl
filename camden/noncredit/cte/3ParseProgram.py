import os
from bs4 import BeautifulSoup
import pandas as pd

# Directory containing HTML files
directory_path = r"C:\text\NJ\Camden\noncredit\CTE\programHTML"
# Output CSV file
output_csv = r"C:\text\NJ\Camden\noncredit\CTE\program_details.csv"

# List to store data dictionaries
program_details = []

# Loop through each HTML file in the directory
for filename in os.listdir(directory_path):
    if filename.endswith(".html"):
        file_path = os.path.join(directory_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            
            # Extract the meta tag contents
            title = soup.find('meta', property='og:title')['content'] if soup.find('meta', property='og:title') else 'No title found'
            description = soup.find('meta', property='og:description')['content'] if soup.find('meta', property='og:description') else 'No description found'
            url = soup.find('meta', property='og:url')['content'] if soup.find('meta', property='og:url') else 'No URL found'
            
             # Parse attribute-value pairs from the table
            attributes = {}
            for tr in soup.find_all('tr', class_='woocommerce-product-attributes-item'):
                key = tr.find('th').get_text(strip=True) if tr.find('th') else 'No Attribute'
                value = tr.find('td').get_text(strip=True) if tr.find('td') else 'No Value'
                attributes[key] = value
            
            # Add dictionary to list
            program_details.append({
                'Filename': filename,
                'Title': title,
                'Description': description,
                'URL': url,
                **attributes  # Unpack attribute-value pairs directly into the dictionary
            })

# Create a DataFrame from the list of dictionaries
df = pd.DataFrame(program_details)

# Save DataFrame to CSV
df.to_csv(output_csv, index=False, encoding='utf-8-sig')

print(f"Data has been written to {output_csv}.")
