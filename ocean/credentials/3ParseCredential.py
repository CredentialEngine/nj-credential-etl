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
        "Certificate of Achievement": "Certificate",
        "an Option to Associate in Arts in Liberal Arts": "Associate of Arts Degree",
        "an Option to Hospitality, Recreation, and Tourism Management, Associate in Science": "Associate of Science Degree",
        "an Option to the Associate in Applied Science in Computer Science": "Associate of Applied Science Degree",
        "An Option to the Associate in Applied Science in Computer Science_Information Technology": "Associate of Applied Science Degree",
        "an Option to the Associate in Applied Science in Technical Studies": "Associate of Applied Science Degree",
        "an option to the Associate in Applied Science in Technical Studies.": "Associate of Applied Science Degree",
        "an Option to the Associate in Arts in Digital Mass Media": "Associate of Arts Degree",
        "an Option to the Associate in Arts in Liberal Arts": "Associate of Arts Degree",
        "an Option to the Associate in Arts in Performing Arts": "Associate of Arts Degree",
        "an Option to the Associate in Science in Business Administration": "Associate of Science Degree",
        "an Option to the Associate in Science in Computer Science": "Associate of Science Degree",
        "Associate in Applied Science": "Associate of Applied Science Degree",
        "Associate in Arts": "Associate of Arts Degree",
        "Associate in Science": "Associate of Science Degree",
        "Associate in Science - Business Concentration": "Associate of Science Degree",
        "Associate in Science - Computer Science Concentration": "Associate of Science Degree",
        "Associate in Science - Health and Physical Education Concentration": "Associate of Science Degree",
        "Associate in Science - Humanities Concentration": "Associate of Science Degree",
        "Associate in Science - Mathematics Concentration": "Associate of Science Degree",
        "Associate in Science - Science Concentration": "Associate of Science Degree",
        "Associate in Science - Social Science Concentration": "Associate of Science Degree",
        "Certificate of Completion": "Certificate",
        "Certificate of Proficiency": "Certificate",
        "Design, & Media; Associate in Science": "Associate of Science Degree",
        "Option to the Associate in Science in Social Work": "Associate of Science Degree",
        "Recreation, and Tourism Management; Associate in Science": "Associate of Science Degree"

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
                    title_text = title_element.text.replace(' &lt; Ocean County College Academic Catalog','').strip()
                    if filename:
                        name = title_text.strip()
                        nameType = filename.replace('.html','').strip()
                        print(nameType)
                        # Split the string at the first comma
                        name, type_cleaned = nameType.split(',', 1)
                        type_ = map_type(type_cleaned.strip())
                    else:
                        name = title_text
                        type_ = filename
                else:
                    name = 'No Title'
                    type_ = 'No Type'

                # Extract description

                # Regular expression to match desired text
                pattern = re.compile('Program Description|Certification Description|Certificate Description')

                # Use find_all with a lambda to check for both tag names and text match
                description_container = soup.find(lambda tag: tag.name in ['h2', 'strong'] and tag.text and pattern.search(tag.text))

                description = ''
                if description_container:
                    # Gather all paragraphs until the next heading is found
                    for sibling in description_container.find_next_siblings():
                        if sibling.name and sibling.name.startswith('h'):
                            break
                        if sibling.name == 'p':
                            description += sibling.get_text(strip=True) + ' '
                        if sibling.name == 'span':
                            description += sibling.get_text(strip=True) + ' '
                elif soup.find('div', class_='tab_content'):
                    # If the specific paragraph isn't found, look in the div with class 'tab_content'
                    description_text = soup.find('div', class_='tab_content').find('p')
                    if description_text:
                        description = description_text.get_text(strip=True)
                    else:
                        description = 'No Description found in tab_content'
                else:
                    description = 'No Description found anywhere'

                # Extract program hours
                # Find the table cell containing "Total Credit Hours"
                credits_label_cell = soup.find('td', text='Total Credit Hours')

                if credits_label_cell:
                    # Find the next sibling of the cell that has "Total Credit Hours" which contains the credits
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
directory_path = r"C:\text\NJ\Ocean\credentials\CredentialHTML"
parse_html(directory_path)
