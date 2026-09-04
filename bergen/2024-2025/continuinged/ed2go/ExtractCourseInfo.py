from bs4 import BeautifulSoup
import csv

# Load the HTML file
html_file = r"C:\text\NJ\Bergen\ContinuingEd\ed2go\onlinecareertraining.bergen.edu.html"
with open(html_file, 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Find the course entries
courses = soup.find_all('div', class_='product-content')  # Adjust based on HTML structure

# Prepare a list to hold the extracted data
course_data = []

# Loop through the courses and extract information
for course in courses:
    course_name = course.find('span', class_='ed-cat-copy ed-text-blue ed-cat-hdr').get_text(strip=True) if course.find('span', class_='ed-cat-copy ed-text-blue ed-cat-hdr') else 'N/A'
    description = course.find('span', class_='res-desc-space-saver ed-text-grey ed-cat-desc course-description').get_text(strip=True) if course.find('span', class_='res-desc-space-saver ed-text-grey ed-cat-desc course-description') else 'N/A'
    cost = course.find('div', class_='ed-body-text ed-row res-container-one cls-ed-body-text').get_text(strip=True) if course.find('div', class_='ed-body-text ed-row res-container-one cls-ed-body-text') else 'N/A'
    duration = course.find('span', class_='course-duration').get_text(strip=True) if course.find('span', class_='course-duration') else 'N/A'
    voucher = 'Yes' if 'voucher' in course.get_text(strip=True).lower() else 'No'
    hours = course.find('span', class_='det-info-block ed-cat-ico-span').get_text(strip=True) if course.find('span', class_='det-info-block ed-cat-ico-span') else 'N/A'
    productType = course.find('span', class_='grey-tag').get_text(strip=True) if course.find('span', class_='grey-tag') else 'N/A'
    product_id = course.get('data-id', 'N/A')  # Assuming a data attribute holds the product ID

    course_data.append([course_name, description, cost, duration, voucher, hours, productType, product_id])

# Save the data to a CSV file
csv_file = r"C:\text\NJ\Bergen\ContinuingEd\ed2go\CEonlinecourses.csv"
with open(csv_file, 'w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    # Write header
    writer.writerow(['Course Name', 'Description', 'Cost', 'Duration', 'Voucher Available', 'Hours', 'Product Type', 'Product ID'])
    # Write data
    writer.writerows(course_data)

print(f"Data has been extracted and saved to {csv_file}")
