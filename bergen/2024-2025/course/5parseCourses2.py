import os
import csv
from bs4 import BeautifulSoup
import datetime
from urllib.parse import urlparse, parse_qs
import re

# Directory containing your HTML files
directory = r"C:\text\NJ\Bergen\course\courseHTML"
BASE_URL = 'https://catalog.bergen.edu'
output_csv = 'Bergen_courses.csv'

def clean_text(input_text):
    """Clean text by removing unnecessary characters."""
    return input_text.strip() if input_text else ''

def extract_course_data(file_path):
    """Extract course details from a single HTML file."""
    with open(file_path, 'r', encoding='utf-8') as html_file:
        soup = BeautifulSoup(html_file, 'html.parser')

        # Initialize data dictionary
        data = {
            'UploadComments': '',
            'Internal Identifier': '',
            'External Identifier': '',
            'Learning Type': 'course',
            'Learning Opportunity Name': '',
            'Description': '',
            'Subject Webpage': '',
            'Life Cycle Status Type': 'Active',
            'Language': 'english',
            'Credit Unit Type': 'Semester Hours',
            'Credit Unit Value': '',
            'Coded Notation': '',
            'Syllabus': '',
            'Lecture Hours': ''
        }

        # Extract course title and code
        title_tag = soup.find('h1', id='course_preview_title')
        if title_tag:
            course_title = title_tag.get_text(strip=True)
            data['Learning Opportunity Name'] = course_title
            data['External Identifier'] = course_title.split(' ')[0].strip()

        # Skip invalid or empty course codes
        if not data['External Identifier'] or data['External Identifier'] == '-':
            return None

        # Extract course description
        description_tag = title_tag.find_next('br') if title_tag else None
        if description_tag and description_tag.next_sibling:
            data['Description'] = clean_text(description_tag.next_sibling)
        if not data['Description']:
            data['Description'] = "This course is more fully described in Bergen's linked course catalog."

        # Extract syllabus link
        syllabus_tag = soup.find('a', href=True, text="Syllabus for this course")
        if syllabus_tag:
            data['Syllabus'] = syllabus_tag['href']

        # Extract subject webpage
        link_element = soup.find('a', class_='print_link acalog-highlight-ignore')
        if link_element and link_element.has_attr('href'):
            data['Subject Webpage'] = BASE_URL + link_element['href']

        # Extract upload comments
        catalog = soup.find(class_='acalog_catalog_name')
        if catalog:
            data['UploadComments'] = f"Created on {datetime.date.today()} from {catalog.get_text(strip=True)}"

        # Extract credit unit value
        credit_tag = soup.find(string=re.compile(r"Credit\(s\)"))
        if credit_tag:
            credit_match = re.search(r"(\d+)", credit_tag)
            if credit_match:
                data['Credit Unit Value'] = credit_match.group(1)

        # Extract lecture hours
        lecture_hours_tag = soup.find(string=re.compile(r"Lecture Hour\(s\)"))
        if lecture_hours_tag:
            lecture_match = re.search(r"(\d+)\s*Lecture Hour\(s\)", lecture_hours_tag)
            if lecture_match:
                data['Lecture Hours'] = lecture_match.group(1)

        # Extract internal identifier from URL
        parsed_url = urlparse(data['Subject Webpage'])
        data['Internal Identifier'] = parse_qs(parsed_url.query).get('coid', [None])[0]

        return data

def process_html_files(directory, output_csv):
    """Process all HTML files in the directory and save the data to a CSV file."""
    with open(output_csv, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            'UploadComments', 'Internal Identifier', 'External Identifier', 'Learning Type',
            'Learning Opportunity Name', 'Description', 'Subject Webpage', 'Life Cycle Status Type',
            'Language', 'Credit Unit Type', 'Credit Unit Value', 'Coded Notation', 'Syllabus', 'Lecture Hours'
        ])
        writer.writeheader()

        for filename in os.listdir(directory):
            if filename.endswith('.html'):
                file_path = os.path.join(directory, filename)
                course_data = extract_course_data(file_path)
                if course_data:
                    writer.writerow(course_data)
                    print(f"Processed {filename}")

if __name__ == "__main__":
    process_html_files(directory, output_csv)
    print(f"Extraction complete. Data saved to {output_csv}")
