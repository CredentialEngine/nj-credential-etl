from bs4 import BeautifulSoup
import csv
import re

# Load the HTML file
html_file = r"C:\text\NJ\Bergen\ContinuingEd\ed2go\onlinecareertraining.bergen.edu.html"
with open(html_file, 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Find the course entries
courses = soup.find_all('div', class_='product-content')

# Prepare a list to hold the extracted data
course_data = []

# Loop through the courses and extract information
for course in courses:
    # Extract course name
    course_name = course.find('span', class_='ed-cat-copy ed-text-blue ed-cat-hdr').get_text(strip=True) if course.find('span', class_='ed-cat-copy ed-text-blue ed-cat-hdr') else 'N/A'
    
    # Extract description
    description = course.find('span', class_='res-desc-space-saver ed-text-grey ed-cat-desc course-description').get_text(strip=True) if course.find('span', class_='res-desc-space-saver ed-text-grey ed-cat-desc course-description') else 'N/A'
    
    # Extract cost from embedded JavaScript object
    script_tag = course.find_previous_sibling('script')
    cost = 'N/A'
    if script_tag and script_tag.string:
        match = re.search(r"\"price\":\s*(\d+\.\d+)", script_tag.string)
        if match:
            cost = f"${match.group(1)}"
    
    # Extract duration
    duration = course.find('span', class_='course-duration').get_text(strip=True) if course.find('span', class_='course-duration') else 'N/A'
    
    # Check for voucher availability
    voucher = 'Yes' if 'voucher' in course.get_text(strip=True).lower() else 'No'
    
    # Extract hours
    hours = course.find('span', class_='det-info-block ed-cat-ico-span').get_text(strip=True) if course.find('span', class_='det-info-block ed-cat-ico-span') else 'N/A'
    
    # Extract product type
    productType = course.find('span', class_='grey-tag').get_text(strip=True) if course.find('span', class_='grey-tag') else 'N/A'
    
    # Extract product ID
    product_id = course.get('data-id', 'N/A')  # Assuming a data attribute holds the product ID
    
    # Extract course link from `onclick` attribute in a sibling <a> tag
    course_link = 'N/A'
    link_tag = course.find_previous('a', class_='catalog-product-link')
    if link_tag and link_tag.has_attr('onclick'):
        link_match = re.search(r"navigate\('([^']+)'\)", link_tag['onclick'])
        if link_match:
            course_link = link_match.group(1)

    # Append to course data list
    course_data.append([course_name, description, cost, duration, voucher, hours, productType, product_id, course_link])

# Save the data to a CSV file
csv_file = r"C:\text\NJ\Bergen\ContinuingEd\ed2go\CEonlinecourses.csv"
with open(csv_file, 'w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    # Write header
    writer.writerow(['Course Name', 'Description', 'Cost', 'Duration', 'Voucher Available', 'Hours', 'Product Type', 'Product ID', 'Course Link'])
    # Write data
    writer.writerows(course_data)

print(f"Data has been extracted and saved to {csv_file}")
