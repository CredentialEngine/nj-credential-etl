from bs4 import BeautifulSoup
from bs4.element import Tag  # Ensure Tag is correctly imported
import pandas as pd
import os
import re

def map_type(type_):
    type_mapping = {
        "A.A.": "Associate of Arts Degree",
        "A.A. - Liberal Arts": "Associate of Arts Degree",
        "A.A.S.": "Associate of Applied Science Degree",
        "A.A.S": "Associate of Applied Science Degree",
        "A.A.S. - Business Management": "Associate of Applied Science Degree",
        "A.A.S. - Computer Information Systems": "Associate of Applied Science Degree",
        "A.A.S. - Graphic Design": "Associate of Applied Science Degree",
        "A.A.S. - Technical Studies": "Associate of Applied Science Degree",
        "A.F.A.": "Associate of Arts Degree",
        "A.F.A. - Studio Arts": "Associate of Arts Degree",
        "A.S.": "Associate of Science Degree",
        "A.S. - Science/Mathematics": "Associate of Science Degree",
        "C.O.A.": "Certificate",
        "Certificate": "Certificate",
        "CT.": "Certificate",
        "CT.A.": "Certificate",
        "JFK Muhlenberg Harold B. and Dorothy A. Snyder Schools of Nursing and Medical Imaging, A.S.": "Associate of Science Degree",
        "Restaurant, and Tourism Management, A.A.S.": "Associate of Applied Science Degree",
        "Restaurant, and Tourism Management, CT.A.": "Certificate",
        "Suggested Grades 4-12, A.A.": "Associate of Arts Degree",
        "Suggested Grades Pre-K-3, A.A.": "Associate of Arts Degree",
        "Trinitas School of Nursing/RWJ Barnabas Health, A.S.": "Associate of Science Degree",
        "AA": "Associate of Arts Degree",
        "AAS": "Associate of Applied Science Degree",
        "Academic Certificate": "Certificate",
        "AS": "Associate of Science Degree",
        "Certificate of Achievement": "Certificate"
    }
    # Default to original type if not in dictionary
    return type_mapping.get(type_.strip(), type_)

def parse_html(directory):
    data = []
    # Traverse through each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

                # Extract the program name and type
                title_element = soup.find('title')
                if title_element:
                    title_text = title_element.text.replace(' County College of Morris','').strip()
                    if filename:
                        name = title_text.strip()
                        nameType = filename.replace('.html','').strip()
                        # Extracting the number inside the parenthesis
                        start = nameType.find('(') + 1  # Find the position of '(' and move one place to the right
                        end = nameType.find(')')  # Find the position of ')'
                        substring = nameType[start:end].strip()
                        # Attempt to convert the extracted substring to an integer
                        try:
                            internal_code = int(substring)  # Try to convert the substring to an integer
                        except ValueError:
                            print("Error: Non-numeric data found:", substring)
                            # Handle the situation, e.g., by skipping this item or cleaning the data
                            internal_code = substring  # Optional: assign a default value or handle differently
                        # Removing the number and parenthesis from the original string
                        type_cleaned = nameType[:start-2]  # Extract everything before '(' minus the space
                        type_ = map_type(type_cleaned.strip())
                    else:
                        name = title_text
                        type_ = filename
                else:
                    name = 'No Title'
                    type_ = 'No Type'

                # Extract description
                description_container = soup.find('p', text = '('+substring+')')
                description = ''
                if description_container:
                    # Gather all paragraphs until the next heading is found
                    for sibling in description_container.find_next_siblings():
                        if sibling.name and sibling.name.startswith('h'):
                            break
                        if sibling.name == 'p':
                            description += sibling.get_text(strip=True) + '\n'  # Adding two new lines for separation
                    description = description.strip()
                elif soup.find('div', class_='tab_content'):
                    # If the specific paragraph isn't found, look in the div with class 'tab_content'
                    description_text = soup.find('div', class_='tab_content').find('p')
                    if description_text:
                        description = description_text.get_text(strip=True)
                    # If the specific paragraph isn't found, look in the div with class 'tab_content'
                    description_text_div = soup.find('div', class_='tab_content').find('div').next_sibling
                    if description_text_div and description == '':
                        description = description_text_div.get_text(strip=True)
                else:
                    description = 'No Description found anywhere'
#
                # Extract program hours
                # Find the table cell containing "Total Credits"
                credits_label_cell = soup.find('td', text='Total Credits')

                if credits_label_cell:
                    # Find the next sibling of the cell that has "Total Credits" which contains the credits
                    credits_value_cell = credits_label_cell.find_next_sibling('td', class_='hourscol')
                    if credits_value_cell:
                        program_hours = credits_value_cell.get_text(strip=True)
                    else:
                        program_hours = 'No program_hours'
                else:
                    program_hours = 'No program_hours'

                def format_outcome(text):
                    """Format the outcome text by stripping leading numbering, capitalizing the first letter, and ensuring it ends with a period."""
                    text = text.strip()
                    # Remove leading numbering such as "1. " or "10. "
                    text = re.sub(r'^\d+\.\s+', '', text)
                    if text:
                        text = text[0].upper() + text[1:]  # Capitalize the first letter
                        if not text.endswith('.'):
                            text += '.'  # Ensure it ends with a period
                    return text
                outcome_section = soup.find(lambda tag: any(phrase in tag.string for phrase in [
                    'Upon completion of this program, graduates will be able to:',
                    'A student in the program is expected to be able to meet the following outcomes at the time of graduation:',
                    'A student in this program will have met the following outcomes at the time of their graduation:'
                    'Upon completion graduates will be able to:',
                    'Upon Completion of this program, graduates will be able to:',
                    'Upon completion of this program, graduates',
                    'Upon completion of this program, graduates&nbsp;will be able to:',
                    'Upon completion of this program, graduates will be able to',
                    'Upon completion of this certificate, graduates will be able to:',
                    'Upon successful completion of all program requirements, graduates will be able to:',
                    'Upon successful completion of all program requirements, graduates will be&nbsp;able to:',
                    'Upon successful completion of all program requirements, graduates',
                    'Program Student Learning Outcomes',
                    'Upon successful completion of all requirements, graduates will be able to:',
                    'Upon successful completion of the Certificate of Achievement requirements, graduates will be able to:',
                    'End of Program Student Learning Outcomes',
                    'Upon successful completion, graduates will be able to:',
                    'Upon successful completion of the Emergency Medical Studies graduates will be able to:',
                    'Upon successful completion of the Emergency Medical Studies Certificate of Achievement graduates will be able to:',
                    'At the end of this program, students will be able to:',
                    'At the end of the program, the graduate will be able to:',
                    'Upon successful completion of all program requirements, graduates will be able to:'
                    'According to the National Research Council, students should be able to demonstrate that:',
                    'Program Outcomes:',
                    'Program Goals:',
                    'Program Goals',
                    'Goals and objectives:',
                    'The objectives of this program are to:',
                    'Successful graduates of the Machine Tool Technology Program can:',
                    'The objectives of this program are to:'
                ]) if tag.string else False)
                outcomes = []

                if outcome_section:
                    outcome_list = outcome_section.find_next(lambda tag: tag.name in ['ul', 'ol'])  # Search any following ul or ol
                    if outcome_list:
                        list_items = outcome_list.find_all('li')
                        outcomes = [format_outcome(li.get_text()) for li in list_items]
                    else:
                        print(f"No list found following the outcome section in file {filename}")
                else:
                    outcome_container = soup.find('div', class_='woocommerce-Tabs-panel woocommerce-Tabs-panel--ywtm-learning-outcomes-218 panel entry-content wc-tab')
                    if outcome_container:
                        outcome_list = outcome_container.find_next(lambda tag: tag.name in ['ul', 'ol'])  # Search any following ul or ol
                        if outcome_list:
                            list_items = outcome_list.find_all('li')
                            outcomes = [format_outcome(li.get_text()) for li in list_items]
                        else:
                            print(f"No list found following the outcome section in file {filename}")
                print(f"No outcome section found in file {filename}")

                # Append to list
                data.append({
                    'Filename': filename,
                    'Credential Name': name,
                    'Credential Named Type': nameType,
                    'Internal Code': internal_code,
                    'Credential Type': type_,
                    'Description': description,
                    'Total Program Hours': program_hours,
                    'Outcomes': outcomes
                })

    # Convert to DataFrame
    df = pd.DataFrame(data)
    output_csv = os.path.join('parsed_credentials.csv')
    df.to_csv(output_csv, index=False)
    print(f"Data successfully parsed and saved to {output_csv}")

# Specify the directory containing HTML files
directory_path = r"C:\text\NJ\Morris\credentials\CredentialHTML"
parse_html(directory_path)
