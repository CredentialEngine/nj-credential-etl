import os 
from bs4 import BeautifulSoup, NavigableString
import pandas as pd
import json

# Path to the HTML file
html_path = r"C:\text\NJ\Camden\noncredit\ed2go\careertraining.ed2go.com.html"
# Output CSV file path
output_csv = r"C:\text\NJ\Camden\noncredit\ed2go\course_details.csv"

# Function to extract direct text from a tag
def extract_direct_text(tag):
    if tag:
        return ''.join(content.strip() for content in tag.contents if isinstance(content, NavigableString)).strip()
    return 'No course name'

# Function to extract course details from onclick JavaScript event
def extract_onclick_data(onclick_text):
    try:
        # Extract JSON-like string from onclick
        json_start = onclick_text.find('{')
        json_end = onclick_text.rfind('}') + 1
        json_text = onclick_text[json_start:json_end]
        json_text = json_text.replace('&quot;', '"')  # Convert encoded quotes
        onclick_data = json.loads(json_text)
        
        # Extract product details if present
        product = onclick_data.get("ecommerce", {}).get("click", {}).get("products", [{}])[0]
        return {
            "Course Name": product.get("name", "Unknown"),
            "Course ID": product.get("id", "Unknown"),
            "Price": product.get("price", "Unknown"),
            "Brand": product.get("brand", "Unknown"),
            "Category": product.get("category", "Unknown"),
            "Variant": product.get("variant", "Unknown"),
            "Quantity": product.get("quantity", "Unknown")
        }
    except Exception as e:
        return {"Error": str(e)}

# Read the HTML file
with open(html_path, 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file.read(), 'html.parser')

# List to store course data
course_details = []

# Find all result blocks
for div in soup.find_all('div', class_='ed-body-text ed-row res-container-one cls-ed-body-text'):
    # Find the link with onclick data
    a_tag = div.find('a', class_='catalog-product-link')
    if a_tag and 'onclick' in a_tag.attrs:
        onclick_text = a_tag['onclick']
        course_url = a_tag.get('onclick', '').split("navigate('")[-1].split("')")[0]
        course_data = extract_onclick_data(onclick_text)
        
        # Extract description
        description_tag = div.find('span', class_='course-description')
        description = description_tag.get_text(strip=True) if description_tag else 'No description'
        
        # Extract course hours
        hours_tag = div.find('span', class_='det-info-block ed-cat-ico-span')
        course_hours = hours_tag.get_text(strip=True) if hours_tag else 'Unknown hours'
        
        # Add course data to the list
        course_details.append({
            'Course URL': course_url,
            'Course Name': course_data.get('Course Name', 'Unknown'),
            'Course ID': course_data.get('Course ID', 'Unknown'),
            'Price': course_data.get('Price', 'Unknown'),
            'Brand': course_data.get('Brand', 'Unknown'),
            'Category': course_data.get('Category', 'Unknown'),
            'Variant': course_data.get('Variant', 'Unknown'),
            'Quantity': course_data.get('Quantity', 'Unknown'),
            'Description': description,
            'Course Hours': course_hours
        })

# Create a DataFrame from the list of dictionaries
df = pd.DataFrame(course_details)

# Save DataFrame to CSV
df.to_csv(output_csv, index=False, encoding='utf-8-sig')

print(f"Data has been written to {output_csv}.")
