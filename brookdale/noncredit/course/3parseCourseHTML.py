import os
import re
from bs4 import BeautifulSoup
import pandas as pd

# Directory containing HTML files
directory_path = r"C:\text\NJ\Brookdale\noncredit\course\courseHTML"
# Output CSV file
output_csv = 'course_details.csv'

# List to store data dictionaries
course_details = []

# Loop through each HTML file in the directory
for filename in os.listdir(directory_path):
    if filename.endswith(".html"):
        file_path = os.path.join(directory_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
                # Contact Hours
                contact_hours_label = soup.find('span', class_='labelSpanStyle', string='Contact Hours')
                contact_hours = contact_hours_label.find_parent().find_next_sibling('div').get_text(strip=True) if contact_hours_label and contact_hours_label.find_parent().find_next_sibling('div') else 'No contact hours found'
                
                for span in soup.find_all('span'):
                    span.insert_before(" ")
                    span.unwrap()

                for p in soup.find_all('p'):
                    p.insert_before("\n")
                    p.insert_after("\n")
                    p.unwrap()

                title = soup.find('meta', {'name': 'title'})['content'] if soup.find('meta', {'name': 'title'}) else 'No title found'
                title = title.replace("\n","")
                course_id = soup.find('div', {'id': 'courseId'}).get_text(strip=True) if soup.find('div', {'id': 'courseId'}) else 'No ID found'
                description = soup.find('div', {'id': 'courseProfileOfficialCourseDescription'}).get_text(" ", strip=True) if soup.find('div', {'id': 'courseProfileOfficialCourseDescription'}) else 'No description found'
                description = description.replace("Course Description","").strip()
                fee = soup.find('td', {'class': 'tuitionProfileFees'}).get_text(strip=True) if soup.find('td', {'class': 'tuitionProfileFees'}) else 'No fee found'
                location = soup.find('a', string='Lincroft Main Campus').get_text(strip=True) if soup.find('a', string='Lincroft Main Campus') else 'No location found'
                ceus = soup.find('div', {'class': 'sectionCEUs'}).get_text(strip=True) if soup.find('div', {'class': 'sectionCEUs'}) else 'No CEUs found'
                ceus = ceus.replace("CEUs","").strip()
                online = soup.find('div', {'class': 'content col-4 col-sm-4'}).get_text(strip=True) if soup.find('div', {'class': 'content col-4 col-sm-4'}) else 'No online info'

                certificate_section = soup.find('h2', string='Applies Towards the Following Certificates')
                if certificate_section:
                    # Find the parent <div> of <h2>
                    parent_div = certificate_section.find_parent('div')
                    if parent_div:
                        # Get all content as text from the parent <div> starting after <h2>
                        #apply_text = ''.join(str(element) for element in certificate_section.next_siblings)
                        apply_text = ''.join(element.get_text(separator=' ', strip=True) if isinstance(element, Tag) else str(element).strip()
                        #cleaned_text = re.sub(r'<[^>]+>', '', apply_text)  # Remove all HTML tags
                     for element in certificate_section.next_siblings)
                    else:
                        apply_text = 'No application information found'
                else:
                    apply_text = 'No application information found'
                
                course_details.append({
                    "Filename": filename,
                    'Title': title,
                    'Course ID': course_id,
                    'Description': description,
                    'Fee': fee,
                    'Location': location,
                    'CEUs': ceus,
                    'Contact Hours': contact_hours,
                    'Online': online,
                    'Apply Text': apply_text
                })
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

# Convert list of dictionaries to DataFrame
df = pd.DataFrame(course_details)

# Save DataFrame to CSV
df.to_csv(output_csv, index=False, encoding='utf-8-sig')

print(f"Data has been written to {output_csv}")
