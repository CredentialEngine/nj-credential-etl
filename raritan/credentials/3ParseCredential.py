import os
import re
from bs4 import BeautifulSoup
import pandas as pd
import uuid


search_patterns = [
        r"Graduates will be able to:",
        r"Graduates  will be able to:",
        r"Graduates are be able to:",
        r"Graduates are able to:",
        r"Graduates\s+are\s+able\s+to:\s*",
        r"Graduates, who must work under the supervision of an attorney and may not provide legal services directly to the public except as permitted by law, are able to:",
        r"Graduates, who must work under the supervision of an attorney and may not provide legal services directly to the public except as permitted by law, will be able to:",
        r"Upon successful completion of the program students will",
        r"Upon completion of this certificate, students will be able to:",
        r"Students who complete the program will be able to:",
        r"Upon completion of the certificate, students will be able to:",
        r"Graduates of this Certificate of Completion will be able to:",
        r"Students will be able to:"
    ]

def format_outcome(text):
    """
    Format an outcome statement by stripping extra whitespace and numbering,
    ensuring the first letter is capitalized, and that it ends with a period.
    """
    text = text.strip()
    # Remove any leading numbering such as "1. " or "10. "
    text = re.sub(r'^\d+\.\s+', '', text)
    if text:
        text = text[0].upper() + text[1:]
        if not text.endswith('.'):
            text += '.'
    return text

# Custom function to check the combined text of <h2> tags including nested elements
def matches_total_credits(tag):
    if tag.name == 'h2' and re.search(r'Total Credits \d+', tag.get_text(), re.I):
        return True
    return False

def map_type(type_):
    type_mapping = {
        # Extend or adjust mappings as needed
        "A.A.S.": "AssociateofAppliedScienceDegree",
        "Certificate": "Certificate",
        "Associate of Applied Science": "AssociateofAppliedScienceDegree",
        "Associate of Applied Science Degree": "AssociateofAppliedScienceDegree",
        "Associate of Applied Science Degree in Computer Information Systems": "AssociateofAppliedScienceDegree",
        "Associate of Applied Science Degree in Ophthalmics": "AssociateofAppliedScienceDegree",
        "Associate of Applied Science Degree Option in Nursing": "AssociateofAppliedScienceDegree",
        "Associate of Arts": "AssociateofArtsDegree",
        "Associate of Arts Degree in Liberal Arts": "AssociateofArtsDegree",
        "Associate of Fine Arts": "AssociateofArtsDegree",
        "Associate of Science": "AssociateofScienceDegree",
        "Associate of Science Degree in Science and Mathematics": "AssociateofScienceDegree",
        "Certificate – Apprenticeship Option": "Certificate",
        "Certificate of Completion": "Certificate",
        "Certificate of Professional Competency": "Certificate",
        "Certificate Program": "Certificate",
        "An Articulated Agreement Leading to the A.S. Degree in Veterinary Technology from St. Petersburg College (Florida)": "AssociateofArtsDegree",
        "unknown": "Certificate",
        # Add more mappings here
    }
    return type_mapping.get(type_.strip(), type_)

def parse_filename(filename):
    # Split the filename at the comma to separate the name and the remaining part
    parts = filename.split(',')
    credential_name = parts[0].strip()  # Get the credential name from the first part

    # Further split the second part of the filename at the underscore to separate type and program ID
    if len(parts) > 1:
        second_part = parts[1].split('_')
        credential_type = second_part[0].strip()  # Get the type from the first part of the second split

        # Get the program ID from the second part of the second split, and remove the file extension
        if len(second_part) > 1:
            program_id = second_part[1].split('.')[0]
        else:
            program_id = 'unknown'
    else:
        credential_type = 'unknown'
        program_id = 'unknown'
    if ',' not in filename and filename.endswith("_1964.html"):
        credential_name = filename[:-10]  # Removes "_1964.html"
        credential_type = "Certificate"

    return credential_name, credential_type, program_id

# Assuming 'soup' is already defined and holds the parsed HTML
def extract_outcomes(soup):
    outcomes = []
    # Iterate through search patterns and extract outcomes
    for pattern in search_patterns:
        outcomes_section = soup.find('p', string=re.compile(pattern))
        if outcomes_section:
            outcomes_list = outcomes_section.find_next_sibling(['ul', 'ol'])
            if outcomes_list:
                for li in outcomes_list.find_all('li'):
                    outcome_text = process_list_item(li)
                    outcome_text = format_outcome(outcome_text)
                    outcomes.append(outcome_text)
            break  # Exit after finding the first matching pattern

    return outcomes

def process_list_item(li):
    # Process each list item to extract clean text before a <br> or end of li
    text_parts = []
    for element in li.children:
        if element.name == 'br':
            break
        if isinstance(element, str):
            text_parts.append(element.strip())
        elif element.name in ['span', 'strong', 'em']:
            text_parts.append(element.get_text().strip())
    return " ".join(text_parts)


def parse_html(directory):
    data = []
    competency_data = []
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

                credential_name, credential_type, programid = parse_filename(filename)
                description_div = soup.find('div', class_=re.compile(r'program_description'))
                if description_div:
                    description_text = description_div.text.strip()

                    # Create a regex pattern to match any of the defined patterns
                    pattern = re.compile('|'.join(search_patterns), re.IGNORECASE)

                    # Search for the pattern in the description text
                    match = pattern.search(description_text)
                    if match:
                        cutoff_index = match.start()
                        description = description_text[:cutoff_index].strip()
                    else:
                        description = description_text

                    # Now, remove double line breaks (or more) from the description
                    description = re.sub(r'\n{2,}', '\n', description)
                else:
                    description = 'No Description Found'

                # Example usage
                outcomes = extract_outcomes(soup)
                #Framework ID
                framework_id = ""
                if outcomes:
                    framework_id = 'ce-' + str(uuid.uuid4())

                # Use the custom function in find
                total_credits_tag = soup.find(matches_total_credits)
                if total_credits_tag:
                    # Extract the number from the text of the <h2> tag
                    match = re.search(r'\d+', total_credits_tag.get_text())
                    if match:
                        total_credits = match.group()
                    else:
                        total_credits = ''
                else:
                    total_credits = ''
                
                #URL from filename
                url = "https://catalog.raritanval.edu/preview_program.php?catoid=15&poid=" + re.search(r'_(\d+)\.html$', filename).group(1)+"&returnto=1319"

                data.append({
                    'Filename': filename,
                    'Type': map_type(credential_type),
                    'Credential Name': credential_name,
                    'Name': credential_name+": "+credential_type,
                    'Internal Identifier': programid,
                    'Description': description,
                    'URL': url,
                    'Outcomes': framework_id,
                    'Hours': total_credits
                })
                # --- Build Competency Data for Outcomes ---
                if outcomes:
                    # Competency framework entry
                    competency_framework_entry = {
                        "ceasn:comment": credential_name,
                        "@id": framework_id,
                        "@type": "ceasn:CompetencyFramework",
                        "ceasn:description": "Graduates will be able to:",
                        "ceasn:inLanguage": "en",
                        "ceasn:name": f"{credential_name}: {credential_type}'s Student Learning Outcomes",
                        "ceasn:publicationStatusType": "http://credreg.net/ctdlasn/vocabs/publicationStatus/Published",
                        "ceasn:source": url
                    }
                    competency_data.append(competency_framework_entry)

                    # Append each outcome as a separate competency entry
                    for outcome in outcomes:
                        competency_entry = {
                            "@id": f'ce-{uuid.uuid4()}',
                            "@type": "ceasn:Competency",
                            "ceasn:inLanguage": "en",
                            "ceasn:competencyLabel": "Student Learning Outcome",
                            "ceasn:competencyText": outcome,
                            "ceasn:isPartOf": framework_id
                        }
                        competency_data.append(competency_entry)

    # Save to DataFrame and CSV
    df = pd.DataFrame(data)
    output_csv_path = os.path.join('parsed_credentials.csv')
    df.to_csv(output_csv_path, index=False)
    print(f"Data successfully parsed and saved to {output_csv_path}")
    
    df_competency = pd.DataFrame(competency_data)
    competency_csv = r"C:\text\NJ\Raritan\credentials\Review\Raritan_BU_Credit_Credential_Competencies.csv"
    df_competency.to_csv(competency_csv, index=False, encoding="utf-8-sig")
    print(f"Competency data successfully saved to {competency_csv}")

# Specify the directory containing HTML files
directory_path = r"C:\text\NJ\Raritan\credentials\CredentialHTML"
parse_html(directory_path)