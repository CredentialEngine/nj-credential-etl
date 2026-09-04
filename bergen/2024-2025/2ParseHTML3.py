import csv
import os
from bs4 import BeautifulSoup
from datetime import datetime
import uuid
import re

# Define the directory containing the HTML files
programs_dir = 'output'

# Define the CSV file names
output_csv = 'extracted_program_data.csv'
output_comp_csv = 'extracted_comp_data.csv'

# Mapping for credential types
credential_mapping = {
    'AA': 'AssociateOfArtsDegree',
    'AS': 'AssociateOfScienceDegree',
    'AAS': 'AssociateOfAppliedScienceDegree',
    'ATS': 'AssociateDegree',
    'AFA': 'AssociateDegree',
    'COA': 'Certificate',
    'CERT': 'Certificate',
    'BSN': 'BachelorOfScienceDegree',
    'BAS': 'BachelorOfScienceDegree'
}

# Function to extract data from an HTML file
def extract_data_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Extract program name
    program_name = ''
    title = soup.find('title')
    if title:
        program_name = title.get_text(strip=True).replace('Program: ', '').replace(' - Bergen Community College - Modern Campus Catalog™', '')

    # Extract current date and time
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Extract program description
    program_description = ''
    program_desc_div = soup.find('div', class_='program_description')
    if program_desc_div:
        # Find the first <p> tag immediately following the div
        first_p_tag = program_desc_div.find_next('p')
        if first_p_tag:
            # Extract the text from the <p> tag
            program_description = first_p_tag.get_text(strip=True)

    # Extract program code
    code = ''
    strong_tag = program_desc_div.find('strong') if program_desc_div else None
    if strong_tag:
        code_text = strong_tag.get_text(strip=True)
        code = code_text.replace('Code: ', '')

    # Extract total credit hours
    credit = ''
    possible_tag = soup.find(string=re.compile(r"Total Credit Hours", re.IGNORECASE))
    if possible_tag:
        parent_tag = possible_tag.find_parent('h2')  # Adjust if necessary
        if parent_tag:
            credit_text = parent_tag.get_text(strip=True)
            credit = re.sub(r"Total Credit Hours:\s*", "", credit_text)
            print(f"Extracted Credit: {credit}")
    else:
        print("Credit info not found.")

    # Extract <li> items under "Program Outcomes"
    program_outcomes = []
    #outcomes_header = soup.find('h2', string="Program Learning Outcomes")
    outcomes_header = soup.find(string=re.compile(r"Program Learning Outcomes", re.IGNORECASE))

    if outcomes_header:
        ol = outcomes_header.find_next('ol')
        if ol:
            program_outcomes = [li.get_text(strip=True) for li in ol.find_all('li')]

    # Extract program URL from the <link rel="canonical"> tag
    program_url = ''
    program_url = file_name.replace('edu_preview','edu/preview').replace('.html','').replace('php_catoid','php?catoid').replace('catalog','http://catalog')

    # Extract and map credential type
    credential_type = 'Unknown'
    if code:
        credential_code = code.split('.')[0]
        credential_type = credential_mapping.get(credential_code, 'Unknown')

    # Assign CTID to the competency framework for the program
    framework_id = 'ce-' + str(uuid.uuid4())

    return {
        'Program Name': program_name,
        'Date and Time': current_datetime,
        'Code': code,
        'Program Description': program_description,
        'Program Outcomes': ' | '.join(program_outcomes),
        'Program URL': program_url,
        'Credit': credit,
        'Credential Type': credential_type,
        'Framework': framework_id,
        'Raw Program Outcomes': program_outcomes
    }

# Extract data from all HTML files in the directory
extracted_data = []
for file_name in os.listdir(programs_dir):
    if file_name.endswith('.html'):
        file_path = os.path.join(programs_dir, file_name)
        data = extract_data_from_html(file_path)
        extracted_data.append(data)

# Define the main CSV headers
csv_headers = [
    'Comment', 'Code', 'CTID', 'Program Name', 'Credential Type', 'Description', 'Subject Webpage',
    'Credit', 'ConditionProfile: External Identifier', 'ConditionProfile: Condition Type',
    'Condition Profile: Required Competency Framework'
]

# Write the extracted data to the main CSV file
with open(output_csv, 'w', newline='', encoding='utf-8-sig') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
    writer.writeheader()
    for row in extracted_data:
        writer.writerow({
            'Comment': "Processed on " + row['Date and Time'],
            'Code': row['Code'],
            'CTID': 'ce-' + str(uuid.uuid4()),
            'Program Name': row['Program Name'],
            'Credential Type': row['Credential Type'],
            'Description': row['Program Description'],
            'Subject Webpage': row['Program URL'],
            'Credit': row['Credit'],
            'ConditionProfile: External Identifier': "Condition_" + row['Code'],
            'ConditionProfile: Condition Type': "requires",
            'Condition Profile: Required Competency Framework': row['Framework']
        })

# Define the Competency CSV headers
csv_comp_headers = [
    'ceasn:comment', '@id', '@type', 'ceasn:description', 'ceasn:inLanguage', 
    'ceasn:name', 'ceasn:publicationStatusType', 'ceasn:source', 
    'ceasn:competencyLabel', 'ceasn:competencyText', 'ceasn:isPartOf'
]

# Write the extracted competency data to another CSV file
with open(output_comp_csv, 'w', newline='', encoding='utf-8-sig') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_comp_headers)
    writer.writeheader()
    for row in extracted_data:
        # Write the competency framework data
        framework_row = {
            'ceasn:comment': row['Code'], 
            '@id': row['Framework'],
            '@type': "ceasn:CompetencyFramework",
            'ceasn:description': 'Program learning outcomes are identified and assessed within the ' + row['Program Name'] + " program.",
            'ceasn:inLanguage': 'en',
            'ceasn:name': row['Program Name'] + "'s Program Learning Outcomes",
            'ceasn:publicationStatusType': "http://credreg.net/ctdlasn/vocabs/publicationStatus/Published",
            'ceasn:source': row['Program URL']
        }
        writer.writerow(framework_row)

        # Write each program outcome as a separate row
        for outcome in row['Raw Program Outcomes']:
            competency_row = {
                '@id': 'ce-' + str(uuid.uuid4()),
                '@type': "ceasn:Competency",
                'ceasn:inLanguage': 'en',
                'ceasn:competencyLabel': "Program Learning Outcome",
                'ceasn:competencyText': outcome,
                'ceasn:isPartOf': row['Framework']
            }
            writer.writerow(competency_row)
