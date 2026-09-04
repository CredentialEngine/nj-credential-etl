import os
from bs4 import BeautifulSoup
import pandas as pd
import uuid

# Generate a unique CTID
def generate_ctid():
    return f"ce-{uuid.uuid4()}"

def custom_split(text):
    parts = text.rsplit('-', 4)  # Split the text from the right at most twice
    if len(parts) > 3:
        parts = text.split(' - ', 1)  # Split only once
        if len(parts) == 2:
            course_code = parts[0].strip()
            course_code = course_code.replace('Course Detail: ','').strip()
            course_title = parts[1].strip()
            return course_code, course_title
    elif len(parts) == 3:
        course_code = parts[0].strip() + "-" + parts[1].strip()
        course_code = course_code.replace('Course Detail: ','').strip()
        course_title = '-'.join(parts[2:]).strip()  # Join the remaining parts to handle titles with dashes
        return course_code, course_title
    else:
        return 'No course code', text.strip()  # Default case if no dash is found

def filename_to_url(filename):
    # Remove the file extension
    filename = filename.replace('.html', '')
    
    url = filename
    
    # Insert the '?' before the first parameter
    url = url.replace('p_sessionId-', 'p?sessionId=')

    
    # Insert the '?' before the first parameter
    url = url.replace('p_categoryId-', 'p?categoryId=')
    
    # Replace the remaining underscore with '&' to correctly format the query string
    url = url.replace('_courseId-', '&courseId=')
    
    # Replace underscores with slashes to revert to the original path structure
    url = url.replace('_', '/')
    
    # Add 'https://' at the beginning to complete the URL
    url = 'https://' + url

    return url

# Directory containing HTML files
directory_path = r"C:\text\NJ\Camden\noncredit\courses\CoursesHTML"
# Output CSV file path
output_csv = r"C:\text\NJ\Camden\noncredit\courses\Camden_BU_Noncredit_Courses.csv"

# List to store data dictionaries
course_details = []

# Loop through each HTML file in the directory
for filename in os.listdir(directory_path):
    if filename.endswith(".html"):
        file_path = os.path.join(directory_path, filename)
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            
            # Extract course code and title
            h1_tag = soup.find('h1', class_='subHeader')
            if h1_tag:
                course_code, course_title = custom_split(h1_tag.get_text(strip=True))
                '''# Split on the last dash and reverse parts
                course_detail = h1_tag.get_text(strip=True).rsplit('-', 1)
                course_detail = [part.strip() for part in course_detail[::-1]]  # Reverse and strip parts
                course_title = course_detail[0] if len(course_detail) > 0 else 'No course title'
                course_code = course_detail[1] if len(course_detail) > 1 else 'No course code'
                course_code = course_code.replace('Course Detail: ','')
                course_detail = h1_tag.get_text(strip=True).split('-')
                course_code = course_detail[0].strip() if len(course_detail) > 1 else 'No course code'
                course_title = course_detail[1].strip() if len(course_detail) > 1 else 'No course title'''
                full_title = h1_tag.get_text(strip=True)
                full_title = full_title.replace('Course Detail: ','')
            else:
                course_code, course_title, full_title = '', '', ''

            # Extract description
            course_description = soup.find('div', class_='courseinner').get_text(strip=True) if soup.find('div', class_='courseinner') else ''
            if len(course_description)< 8:
                course_description = "Camden County College's " + full_title
            if course_description=="No course details available":
                course_description = "Camden County College's " + full_title

            # Extract hidden input values
            hidden_values = {input_tag['name']: input_tag['value'] for input_tag in soup.find_all('input', type='hidden')}
            
            #Convertfilename to URL
            converted_url = filename_to_url(filename)

             # Add dictionary to list
            course_details.append({
                "CTID": generate_ctid(),
                "Learning Type": "Course",
                #'Filename': filename,
                'Learning Opportunity Name': full_title,
                #'Course Code': course_code,
                #'Course Title': course_title,
                'Description': course_description,
                'Subject Webpage': converted_url,
                "Life Cycle Status Type": "Active",
                "Language": "English",
                "Coded Notation": course_code,
                "Is Non-Credit": "TRUE",
                "Version Identifier": "2024-2025 Catalog",
                #**hidden_values  # Unpack hidden values directly into the dictionary
            })

# Create a DataFrame from the list of dictionaries
df = pd.DataFrame(course_details)

# Save DataFrame to CSV
df.to_csv(output_csv, index=False, encoding='utf-8-sig')

print(f"Data has been written to {output_csv}.")