import os
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse, parse_qs

# Define the directory containing HTML files
directory_path = r"C:\text\NJ\Camden\noncredit\courses"
# Define the output CSV file path
output_csv = r"noncredit_course_links.csv"

# Prepare a list to store data dictionaries
course_details = []

# Loop through each HTML file in the directory
for filename in os.listdir(directory_path):
    if filename.endswith(".html"):
        file_path = os.path.join(directory_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')

            # Find all <a> tags
            for a_tag in soup.find_all('a', href=True):
                url = a_tag['href']
                # Check if 'courseId' is in the URL
                if 'courseId' in url:
                    parsed_url = urlparse(url)
                    query_params = parse_qs(parsed_url.query)
                    
                    # Extract courseId and categoryId
                    course_id = query_params.get('courseId', [''])[0]
                    category_id = query_params.get('categoryId', [''])[0]
                    
                    # Get link text
                    link_text = a_tag.get_text(strip=True)
                    
                    # Append details to the list
                    course_details.append({
                        'Filename': filename,
                        'Course ID': course_id,
                        'Category ID': category_id,
                        'Link Text': link_text,
                        'URL': url
                    })

# Create a DataFrame from the list of dictionaries
df = pd.DataFrame(course_details)

# Save DataFrame to CSV
df.to_csv(output_csv, index=False, encoding='utf-8-sig')

print(f"Data has been written to {output_csv}.")
