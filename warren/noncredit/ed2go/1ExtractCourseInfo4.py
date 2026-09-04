import os
from bs4 import BeautifulSoup, NavigableString
import pandas as pd

# Path to the HTML file
html_path = r"C:\text\NJ\Warren\noncredit\ed2go\Browse Online Courses for Warren County Community College _ ed2go.html"
# Output CSV file path
output_csv = r"C:\text\NJ\Warren\noncredit\ed2go\course_details.csv"

# Assuming 'name_div' is your BeautifulSoup object for the <div> tag
def extract_direct_text(div_tag):
    if div_tag:
        # Iterate through the contents of the div tag
        text_parts = []
        for content in div_tag.contents:
            # Check if the content is a direct NavigableString and not another tag
            if isinstance(content, NavigableString):
                text_parts.append(content.strip())
        # Join all parts of text collected to form the full direct text string
        return ''.join(text_parts)
    else:
        return 'No course name'

def extract_description(div_tag):
    description_texts = []
    # Find the next sibling elements, specifically looking for <p> tags
    next_p = div_tag.find_next('p')  # This skips the empty <p class="desc-text">
    for _ in range(2):  # Adjust the range number if more <p> tags are considered
        if next_p:
            description_texts.append(next_p.get_text(strip=True))
            next_p = next_p.find_next_sibling('p')
    return ' '.join(description_texts) if description_texts else 'No description'

# Read the HTML file
with open(html_path, 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file.read(), 'html.parser')

# List to store course data
course_details = []

# Find all <a> tags that might contain course information
for a_tag in soup.find_all('a', href=True):
    if 'onclick' in a_tag.attrs:  # Check if there's an 'onclick' attribute that might contain course details
        # Extract URL
        course_url = a_tag['href']
        
        # Attempt to extract data from the 'onclick' attribute
        onclick_text = a_tag['onclick']
        
        # Extracting hidden values would require parsing the JavaScript or JSON within the onclick attribute
        # For demonstration, let's focus on easily extractable details like the name from the <div> tag.
        
        name_div = a_tag.find('div', class_='sr-c-title')
        #course_name = name_div.get_text(strip=True) if name_div else 'No course name'
        course_name = extract_direct_text(name_div)
        
        # Extract description if available
        #desc_p = name_div.find('p', class_='desc-text') if name_div else None
        #description = desc_p.get_text(strip=True) if desc_p else 'No description'
        # Extract description by checking for subsequent <p> tags
        description = extract_description(name_div).strip()
        
        # Add course data to the list
        course_details.append({
            'Course URL': course_url,
            'Course Name': course_name,
            'Description': description,
            'Onclick Data': onclick_text  # Raw data; needs further parsing to be meaningful
        })

# Create a DataFrame from the list of dictionaries
df = pd.DataFrame(course_details)

# Save DataFrame to CSV
df.to_csv(output_csv, index=False, encoding='utf-8-sig')

print(f"Data has been written to {output_csv}.")
