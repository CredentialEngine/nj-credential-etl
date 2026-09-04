from bs4 import BeautifulSoup
from bs4.element import Tag  # Ensure Tag is correctly imported
import pandas as pd
import os
import re
import uuid

def map_type(type_):
    type_mapping = {
        "AA": "AssociateOfArtsDegree",
        "AAS": "AssociateOfAppliedScienceDegree",
        "AS": "AssociateOfScienceDegree",
        "CA": "Certificate",
        "CT": "Certificate",
    }
    # Default to original type if not in dictionary
    return type_mapping.get(type_.strip(), type_)

def parse_html(directory):
    data = []            # List for credentials data
    competency_data = [] # List for competency framework and competencies

    # Traverse through each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

                # Extract the program name from the <title> tag
                title_element = soup.find('title')
                if title_element:
                    title_text = title_element.text.strip()
                    if '-' in title_text:
                        name, college_ = title_text.split('-', 1)
                        name = name.strip()
                    else:
                        name = title_text
                else:
                    name = 'No Title'

                # Program Code
                program_code_text = ""
                program_code_container = soup.find('th', string=lambda t: t and t.strip() == "Program Code")
                if program_code_container:
                    td_container = program_code_container.find_next_sibling('td')
                    if td_container:
                        program_code_text = td_container.get_text(strip=True)
                
                # Credential Type & adjust name if program code is split by a period
                type_ = ""
                abbreviation = ""
                if program_code_text:
                    parts = program_code_text.split('.')
                    if len(parts) == 2:
                        abbreviation, _type = parts
                        type_ = map_type(_type)
                        name = name + ": " + _type
                    else:
                        type_ = program_code_text

                # CIP Code
                cip_code_text = ""
                cip_code_container = soup.find('th', string=lambda t: t and t.strip() == "CIP Code")
                if cip_code_container:
                    td_container = cip_code_container.find_next_sibling('td')
                    if td_container:
                        cip_code_text = td_container.get_text(strip=True)

                # Extract description
                description_container = soup.find('div', class_='woocommerce-product-details__short-description')
                if description_container:
                    description_text = description_container.get_text(strip=True)
                    if description_text:
                        description = description_text.replace(".Apply & Register", ".")
                    else:
                        fallback_container = description_container.find_next_sibling('div', string=True)
                        if fallback_container:
                            description = fallback_container.get_text(strip=True).replace(".Apply & Register", ".")
                        else:
                            description = 'No Description no tag'
                else:
                    description = 'No Description no container'

                # Extract canonical URL if available
                canonical_link = soup.find('link', rel='canonical')
                url = canonical_link['href'] if canonical_link and canonical_link.has_attr('href') else ""

                # Extract total program hours (credits)
                hours_code_text = ""
                hours_code_container = soup.find(
                    'td', 
                    string=lambda t: t and t.strip() in ["Total Minimum Credits", "Total Credits", "TOTAL CREDITS", "Total Program Credits"]
                )
                if hours_code_container:
                    td_container = hours_code_container.find_next_sibling('td')
                    if td_container:
                        hours_code_text = td_container.get_text(strip=True)
                else:
                    print("No hours container and hours text for " + filename)

                # Find the <h3> element that contains "Employment Opportunities"
                h3_elem = soup.find('h3', string=lambda t: t and "Employment Opportunities" in t)
                occupation = ""

                if h3_elem:
                    # Use the parent container (the <div>) of the <h3> element
                    container = h3_elem.find_parent('div')
                    if container:
                        # Find the <ul> element within the container
                        ul = container.find('ul')
                        if ul:
                            # Extract all <li> element texts and join them with a pipe separator
                            occupation_list = [li.get_text(strip=True) for li in ul.find_all('li')]
                            occupation = "|".join(occupation_list)

                # Function to format outcomes
                def format_outcome(text):
                    #Remove newline and carriage return characters
                    text = text.replace("\n", " ").replace("\r", " ")
                    #Strip leading numbering, capitalize first letter, and ensure outcome ends with a period.
                    text = text.strip()
                    #Remove double spaces
                    text = text.replace("\s\s","\s").replace("  "," ")
                    text = re.sub(r'^\d+\.\s+', '', text)
                    if text:
                        text = text[0].upper() + text[1:]
                        if not text.endswith('.'):
                            text += '.'
                    return text

                # Look for an outcome section using various possible headings
                outcome_section = soup.find(lambda tag: (tag.name in ['h2', 'h3', 'h4', 'strong', 'p']) and 
                                            tag.string and any(phrase in tag.string for phrase in [
                    'Upon completion of this program, graduates will be able to:',
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
                    'Upon successful completion of all program requirements, graduates will be able to:',
                    'According to the National Research Council, students should be able to demonstrate that:',
                    'Program Outcomes:',
                    'Program Goals:',
                    'Program Goals',
                    'Goals and objectives:',
                    'The objectives of this program are to:',
                    'Successful graduates of the Machine Tool Technology Program can:',
                    'The objectives of this program are to:',
                ]))
                outcomes = []
                if outcome_section:
                    outcome_list = outcome_section.find_next(lambda tag: tag.name in ['ul', 'ol'])
                    if outcome_list:
                        # Generate a unique framework ID for this program's competencies
                        framework_id = 'ce-' + str(uuid.uuid4())
                        list_items = outcome_list.find_all('li')
                        outcomes = [format_outcome(li.get_text()) for li in list_items]
                    else:
                        print(f"No list found following the outcome section in file {filename}")
                else:
                    outcome_container = soup.find('div', class_='woocommerce-Tabs-panel woocommerce-Tabs-panel--ywtm-learning-outcomes-218 panel entry-content wc-tab')
                    if outcome_container:
                        outcome_list = outcome_container.find_next(lambda tag: tag.name in ['ul', 'ol'])
                        if outcome_list:
                            # Generate a unique framework ID for this program's competencies
                            framework_id = 'ce-' + str(uuid.uuid4())
                            list_items = outcome_list.find_all('li')
                            outcomes = [format_outcome(li.get_text()) for li in list_items]
                        else:
                            print(f"No list found following the outcome section in file {filename}")

                # Append credential data to the main data list
                data.append({
                    'Filename': filename,
                    'Credential Name': name,
                    'Credential Program Code': program_code_text,
                    'Type': type_,
                    'CIP': cip_code_text,
                    'URL': url,
                    'Description': description,
                    'Hours': hours_code_text,
                    'Occupation': occupation,
                    'Outcomes': framework_id
                })

                # ----- Build competency data for this file -----
                # Competency framework entry
                competency_framework_entry = {
                    "ceasn:comment": name,
                    "@id": framework_id,
                    "@type": "ceasn:CompetencyFramework",
                    "ceasn:description": "Upon completion of this program students will be able to:",
                    "ceasn:inLanguage": "en",
                    "ceasn:name": f"{name}'s Program Learning Outcomes",
                    "ceasn:publicationStatusType": "http://credreg.net/ctdlasn/vocabs/publicationStatus/Published",
                    "ceasn:source": url
                }
                competency_data.append(competency_framework_entry)

                # Append each outcome as a separate competency entry
                for outcome in outcomes:
                    competency_entry = {
                        "@id": 'ce-' + str(uuid.uuid4()),
                        "@type": "ceasn:Competency",
                        "ceasn:inLanguage": "en",
                        "ceasn:competencyLabel": "Program Learning Outcome",
                        "ceasn:competencyText": outcome,
                        "ceasn:isPartOf": framework_id
                    }
                    competency_data.append(competency_entry)

    # Save the credentials data to CSV
    df = pd.DataFrame(data)
    credentials_csv = os.path.join('parsed_credentials.csv')
    df.to_csv(credentials_csv, index=False)
    print(f"Credentials data successfully parsed and saved to {credentials_csv}")

    # Save the competency data to CSV
    df_competency = pd.DataFrame(competency_data)
    competency_csv = r"C:\text\NJ\Camden\credentials\Review\Camden_BU_Credit_Credential_Competencies.csv"
    df_competency.to_csv(competency_csv, index=False, encoding="utf-8-sig")
    print(f"Competency data successfully saved to {competency_csv}")

# Specify the directory containing HTML files
directory_path = r"C:\text\NJ\Camden\credentials\CredentialHTML"
parse_html(directory_path)
