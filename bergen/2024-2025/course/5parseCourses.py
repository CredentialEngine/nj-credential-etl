import os
import csv
import unicodedata
from bs4 import BeautifulSoup
import datetime
from urllib.parse import urlparse, parse_qs
import re

# Define the directory containing your HTML files and the base URL for the catalog
directory = r"C:\text\NJ\Bergen\course\courseHTML"
BASE_URL = 'https://catalog.bergen.edu'

# Output CSV file
csv_file = 'Bergen_courses.csv'

def normalize_text(text):
    """Normalize Unicode data to remove extraneous characters."""
    return unicodedata.normalize("NFKD", text)

def clean_text(input_text):
    """Clean text by replacing specific unicode characters with their correct counterparts."""
    text = input_text.decode('utf-8') if isinstance(input_text, bytes) else input_text
    replacements = {
        'â€œ': '"', 'â€': '"', 'â€™': "'", 'â€˜': "'", 'â€”': '—',
        'â€“': '–', 'â€¦': '…', 'â€¢': '•', 'â€¦': '...'
    }
    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)
    return text

with open(csv_file, 'w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    writer.writerow(['UploadComments', 'Internal Identifier', 'External Identifier', 'Learning Type', 'Learning Opportunity Name', 'Description', 'Subject Webpage', 'Life Cycle Status Type', 'Language', 'Credit Unit Type', 'Credit Unit Value', 'Coded Notation', 'Syllabus', 'Lecture Hours'])
    
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as html_file:
                soup = BeautifulSoup(html_file, 'html.parser')
                course_title = soup.find('h1', id='course_preview_title').get_text(strip=True)
                
                # Skip files with blank or just a dash course codes
                course_code = course_title.split(' ')[0].strip()
                #New functionality here to skip course_codes that are "-" from 7parsecourses.
                if not course_code or course_code == '-':
                    continue
                
                # Initialize variables
                course_title = ''
                description = ''
                syllabus_link = ''

                # Extract course title
                title_tag = soup.find('h1', id='course_preview_title')
                if title_tag:
                    course_title = title_tag.get_text(strip=True)
                
                # Extract course description
                description_text = ''
                description_tag = title_tag.find_next('br') if title_tag else None
                if description_tag and description_tag.next_sibling:
                    # Check if next sibling is a NavigableString (text content)
                    sibling_text = description_tag.next_sibling
                    description_text = str(sibling_text).strip() if sibling_text else ''
                if not description_text:
                    description_text = "This course is more fully described in Bergen's linked course catalog."
                description = description_text

                # Extract syllabus link
                syllabus_tag = soup.find('a', href=True, text="Syllabus for this course")
                if syllabus_tag:
                    syllabus_link = syllabus_tag['href']

                link_element = soup.find('a', class_='print_link acalog-highlight-ignore')
                link = BASE_URL + link_element['href'] if link_element and link_element.has_attr('href') else ''                
                
                catalog = soup.find(class_='acalog_catalog_name')
                uploadcomments = "Created on " + str(datetime.date.today()) + " from " + catalog.get_text(strip=True) if catalog else ''
                
                
                # Extracting credit hours
                # Find the <strong> tag that contains 'Credit(s)'
                credit_hours_tag = soup.find('strong', string='Credit(s)')
                # Initialize variable
                credit_hours = None
                if credit_hours_tag:
                    # The number of credit hours should be the next sibling of the <strong> tag
                    credit_hours_text = credit_hours_tag.get_text(strip=True)

                    # Use regular expression to extract the number
                    if credit_hours_text:
                        credit_hours_match = re.search(r'(\d+)', credit_hours_text)
                        if credit_hours_match:
                            credit_hours = int(credit_hours_match.group())
                
                # Extracting lecture hours
                # Locate the text node that contains 'LECTURE HOURS MIN:'
                lecture_hours_text = soup.find(string=lambda string: string and 'Lecture Hour(s)' in string)
                # Initialize variable
                lecture_hours = None
                if lecture_hours_text:
                    # The lecture hours are expected to be within the same text node, so we use regex to extract the number
                    lecture_hours_match = re.search(r'(\d+)\s*Lecture Hour(s)', lecture_hours_text)
                    if lecture_hours_match:
                        lecture_hours = int(lecture_hours_match.group(1))
                                
                parsed_url = urlparse(link)
                internalid = parse_qs(parsed_url.query).get('coid', [None])[0]

                # Write to CSV
                writer.writerow([uploadcomments, internalid, course_code, "course", course_title, description, link, "Active", "english", "Semester Hours", credit_hours, course_code, syllabus_link, lecture_hours])

                print(f"Processed {filename}")

print('Extraction complete. Data saved to', csv_file)
