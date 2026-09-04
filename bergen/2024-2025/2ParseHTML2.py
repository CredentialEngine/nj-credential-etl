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
    'AIS': 'AssociateDegree',
    'CRT': 'Certificate',
    'STC': 'Certificate',
    'BSN': 'BachelorOfScienceDegree',
    'BAS': 'BachelorOfScienceDegree'
}

# Function to extract data from an HTML file
def extract_data_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    # Extract program name
    #program_name = os.path.basename(file_path).replace('.html', '').replace('_', ' ')
    #program_name = re.sub(r'\d+$', '', program_name).strip()
    h1_tag = soup.find('div', id_='acalog-page-title')
    if h1_tag:
        program_name = h1_tag.get_text(strip=True)

    # Extract current date and time
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Extract text from all <h3> tags
    h3_tags = [h3.get_text(strip=True).replace('\r', '').replace('\n', ' ') for h3 in soup.find_all('h3')]

    # Extract program description
    program_description = ''
    program_name = ''
    code = ''  # Default value if not found
    h2_tag = soup.find('div', class_='program_description')
    if h2_tag:
        next_strong = h2_tag.find_next('strong')
        if next_strong:
            code = next_strong.get_text(strip=True).replace('Code: ', '')
        next_p = h2_tag.find_next('p')
        if next_p:
            program_description = next_p.get_text(strip=True).replace('\r', '').replace('\n', ' ')

    #Extract credit
    credit = ''
    h2_credit = soup.find('h2', string="Total Credit Hours: ")
    if h2_credit:
        credit = h2_credit.get_text(strip=True).replace('Total Credit Hours: ','')

    # Extract <li> items under "Program Outcomes"
    program_outcomes = []
    h3_outcomes = soup.find('h2', string="Program Learning Outcomes")
    if h3_outcomes:
        ol = h3_outcomes.find_next('ol')
        if ol:
            program_outcomes = [li.get_text(strip=True).replace('\r', '').replace('\n', ' ') for li in ol.find_all('li')]

    # Extract program URL from the <link rel="canonical"> tag
    program_url = ''
    link_tag = soup.find('link', rel='canonical')
    if link_tag:
        program_url = link_tag.get('href', '')

    # Extract and map credential type
    credential_type = ''
    external_id = ''
    span_tag = soup.find('span', class_='text-uppercase')
    if span_tag:
        external_id = span_tag.get_text(strip=True)
        credential_code = span_tag.get_text(strip=True).split('.')[-1]
        credential_type = credential_mapping.get(credential_code, 'Unknown')

    # Assign CTID to the competency framework for the program
    framework_id = 'ce-' + str(uuid.uuid4())

    return {
        'Program Name': program_name,
        'Date and Time': current_datetime,
        'Code': code,
        'H3 Tags': h3_tags,
        'Program Description': program_description,
        'Program Outcomes': ' | '.join(program_outcomes),
        'Program URL': program_url,
        'Credit': credit,
        'External Identifier': code,
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
    'Comment', 'External Identifier', 'CTID', 'Credential Name', 'Credential Type', 'H3 Tags', 
    'Description', 'Subject Webpage', 'Credential Status', 'Language', 'Credit',
    'ConditionProfile: External Identifier', 'ConditionProfile: Condition Type', 
    'Condition Profile: Required Competency Framework'
]

# Write the extracted data to the main CSV file
with open(output_csv, 'w', newline='', encoding='utf-8-sig') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
    writer.writeheader()
    for row in extracted_data:
        writer.writerow({
            'Comment': "Processed on " + row['Date and Time'],
            'External Identifier': row['Code'],
            'CTID': 'ce-' + str(uuid.uuid4()),
            'Credential Name': row['Program Name'],
            'Credential Type': row['Credential Type'],
            'H3 Tags': ' | '.join(row['H3 Tags']),
            'Description': row['Program Description'],
            'Subject Webpage': row['Program URL'],
            'Credential Status': "Active",
            'Language': "en",
            'Credit': row['Credit'],
            'ConditionProfile: External Identifier': "Condition_" + row['External Identifier'],
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
            'ceasn:comment': "SNCL" + row['External Identifier'], 
            '@id': row['Framework'],
            '@type': "ceasn:CompetencyFramework",
            'ceasn:description': 'Program outcomes are identified and assessed within the ' + row['Program Name'] + " program.",
            'ceasn:inLanguage': 'en',
            'ceasn:name': row['Program Name'] + "'s Program Outcomes",
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
                'ceasn:competencyLabel': "Program Outcome",
                'ceasn:competencyText': outcome,
                'ceasn:isPartOf': row['Framework']
            }
            writer.writerow(competency_row)

print(f'Data has been written to {output_csv} and {output_comp_csv}')
