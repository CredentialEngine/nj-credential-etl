# Re-running the code after state reset

from bs4 import BeautifulSoup
import pandas as pd
import csv

# Specify the output CSV file path
output_csv_path = r"C:\text\NJ\Union\noncredit\ugotclass\Union_UGotClass_Courses.csv"

# Path to the HTML file
html_file_path = r"C:\text\NJ\Union\noncredit\ugotclass\Home - UCNJ Union College of Union County - LERN - UGotClass.html"

# Load HTML file content
with open(html_file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the simulated HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# List to hold certificate and course information
data = []

# Find all certificate blocks
certificates = soup.find_all('div', class_='certificate')
for cert in certificates:
    cert_name = cert.find('a').text.strip()
    cert_url = cert.find('a')['href']

    # Each certificate can have multiple courses
    courses = cert.find_all('div', class_='course')
    for course in courses:
        course_name = course.find('a').text.strip()
        course_url = course.find('a')['href']
        
        # Append data to list
        data.append({
            'Type': 'Course',
            'Name': course_name,
            'URL': course_url
        })

    # Add certificate data
    data.append({
        'Type': 'Certificate',
        'Name': cert_name,
        'URL': cert_url
    })

# Convert data to DataFrame
df = pd.DataFrame(data)

# Save DataFrame to CSV
df.to_csv(output_csv_path, index=False, quoting=csv.QUOTE_ALL, encoding='utf-8-sig')