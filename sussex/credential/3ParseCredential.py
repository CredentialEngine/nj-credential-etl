from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import uuid

def map_type(type_):
    type_mapping = {
        "A.A.": "AssociateofArtsDegree",
        "A.A. - Liberal Arts": "AssociateofArtsDegree",
        "A.A.S.": "AssociateofAppliedScienceDegree",
        "A.A.S. - Business Management": "AssociateofAppliedScienceDegree",
        "A.A.S. - Computer Information Systems": "AssociateofAppliedScienceDegree",
        "A.A.S. - Graphic Design": "AssociateofAppliedScienceDegree",
        "A.A.S. - Technical Studies": "AssociateofAppliedScienceDegree",
        "A.F.A.": "AssociateofArtsDegree",
        "A.F.A. - Studio Arts": "AssociateofArtsDegree",
        "A.S.": "AssociateofScienceDegree",
        "A.S. - Science/Mathematics": "AssociateofScienceDegree",
        "C.O.A.": "Certificate",
        "Certificate": "Certificate"
    }
    # Default to original type if not in dictionary
    return type_mapping.get(type_.strip(), type_)

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

def parse_html(directory):
    data = []
    competency_data = []
    outcomes = []
    # Traverse through each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

                # Extract the program name and type
                title_element = soup.find('h1', id='acalog-content')
                if title_element:
                    title_text = title_element.text.strip()
                    if ',' in title_text:
                        name, type_ = title_text.split(',', 1)
                        name = name.strip()
                        nameType = type_.strip()
                        type_ = map_type(type_.strip())
                    else:
                        name = title_text
                        type_ = 'No Type'
                else:
                    name = 'No Title'
                    type_ = 'No Type'

                # Extract description
                description = soup.find('div', class_='program_description').p.text if soup.find('div', class_='program_description') and soup.find('div', class_='program_description').p else ''

                # Extract total program hours Find the <h2> tag that contains "Total Program Hours:"
                program_hours_tag = soup.find(string=lambda text: text and "Total Program Hours:" in text)
                # Extract the number from the text
                if program_hours_tag:
                    hours = program_hours_tag.get_text(strip=True).split(":")[-1].strip()
                else:
                    hours = ""

                outcome_section = soup.find(lambda tag: (tag.name == 'h2' or tag.name == 'h4' or tag.name == 'strong') and any(phrase in tag.string for phrase in [
                    'Upon completion of this program, graduates will be able to:',
                    'According to the National Research Council, students should be able to demonstrate that:',
                    'Program Outcomes:',
                    'Program Goals:',
                    'Goals and objectives:',
                    'The objectives of this program are to:',
                    'Successful graduates of the Machine Tool Technology Program can:',
                    'The objectives of this program are to:'
                ]) if tag.string else False)

                if outcome_section:
                    outcome_list = outcome_section.find_next(lambda tag: tag.name in ['ul', 'ol'])  # Search any following ul or ol
                    if outcome_list:
                        list_items = outcome_list.find_all('li')
                        outcomes = [format_outcome(li.get_text()) for li in list_items]
                    else:
                        print(f"No list found following the outcome section in file {filename}")
                else:
                    print(f"No outcome section found in file {filename}")
                #Framework ID
                framework_id = ""
                if outcomes:
                    framework_id = 'ce-' + str(uuid.uuid4())

                # URL  - Find the anchor tag inside the div with class "gateway-toolbar-print gateway-toolbar-item"
                # Find the div element
                url = ''
                div_tag = soup.find("span", class_="print_degree_planner_link")
                # Ensure div exists before proceeding
                if div_tag:
                    a_tag = div_tag.find("a", href=True)  # Find the <a> inside div
                    if a_tag:
                        raw_url = a_tag["onclick"]
                        raw_url = raw_url.replace("acalogPopup('preview_degree_planner.php?","preview_program.php?")
                        url = "https://catalog.sussex.edu/" + raw_url.split("&print")[0]  # Remove '&print'

                # Append to list
                data.append({
                    'Filename': filename,
                    'Name': name+": "+nameType,
                    'Credential Named Type': nameType,
                    'Type': type_,
                    'Description': description,
                    'URL': url,
                    'Hours': hours,
                    'Outcomes': framework_id
                })
                
                # --- Build Competency Data for Outcomes ---
                if outcomes:
                    # Competency framework entry
                    competency_framework_entry = {
                        "ceasn:comment": name,
                        "@id": framework_id,
                        "@type": "ceasn:CompetencyFramework",
                        "ceasn:description": "Graduates will be able to:",
                        "ceasn:inLanguage": "en",
                        "ceasn:name": f"{name}: {nameType}'s Student Learning Outcomes",
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

    # Convert to DataFrame
    df = pd.DataFrame(data)
    output_csv = os.path.join('parsed_credentials.csv')
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"Data successfully parsed and saved to {output_csv}")
    
    df_competency = pd.DataFrame(competency_data)
    competency_csv = r"C:\text\NJ\Sussex\credential\Review\Sussex_BU_Credit_Credential_Competencies.csv"
    df_competency.to_csv(competency_csv, index=False, encoding="utf-8-sig")
    print(f"Competency data successfully saved to {competency_csv}")

# Specify the directory containing HTML files
directory_path = r"C:\text\NJ\Sussex\credential\CredentialHTML"
parse_html(directory_path)
