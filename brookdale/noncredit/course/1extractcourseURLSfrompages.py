import os
from bs4 import BeautifulSoup
import pandas as pd

# Directory containing HTML files
directory_path = r'C:\text\NJ\Brookdale\noncredit\course'

# List to hold all the extracted data
data = []

# Loop through each file in the directory
for filename in os.listdir(directory_path):
    if filename.endswith(".html"):  # Check if the file is an HTML file
        file_path = os.path.join(directory_path, filename)
        
        # Open and read the HTML file
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            
            # Find all 'a' tags that have 'href' containing 'courseId'
            links = soup.find_all('a', href=lambda href: href and 'courseId' in href)
            for link in links:
                name = link.get_text(strip=True)
                if name:  # Check if the name is not empty
                    url = link['href']
                    data.append({'URL': url, 'Name of URL': name})

# Create a DataFrame from the list of data
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
output_path = r'C:\text\NJ\Brookdale\noncredit\course\extracted_urls.csv'
df.to_csv(output_path, index=False, encoding='utf-8')

print(f"Data has been written to {output_path}")
