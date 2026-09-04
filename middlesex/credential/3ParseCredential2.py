from bs4 import BeautifulSoup
from bs4.element import Tag
import pandas as pd
import os
import re
import uuid

def map_type(type_):
    type_mapping = {
        "Associate in Applied Science": "AssociateOfAppliedScienceDegree",
        "Associate in Arts Degree": "AssociateOfArtsDegree",
        "Associate in Fine Arts Degree": "AssociateOfArtsDegree",
        "Associate in Science Degree": "AssociateOfScienceDegree",
        "Certificate": "Certificate",
        "Non-Degree": "Certificate",
    }
    return type_mapping.get(type_.strip(), type_)

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

def parse_html(directory):
    data = []
    competency_data = []  # List for competency framework and competency entries

    # Traverse through each HTML file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

                # --- Extract Program Name ---
                cl_head = soup.find('div', class_='cl-head')
                if cl_head and cl_head.h1:
                    name = cl_head.h1.get_text(strip=True)
                else:
                    name = "No Name"

                # --- Extract Program Type ---
                # The type appears immediately after a <br> element.
                br_elem = soup.find('br')
                if br_elem and br_elem.next_sibling:
                    type_text = br_elem.next_sibling.strip()
                else:
                    type_text = "No Type"
                type_mapped = map_type(type_text)
                # For CSV output, use these variables:
                type_cleaned = type_text
                nameType = type_text
                # No internal code available in this HTML example.
                internal_code = ""

                # --- Extract Description ---
                prog_desc = soup.find('div', class_='prog_desc')
                if prog_desc:
                    description = prog_desc.get_text(strip=True)
                else:
                    description = f"Essex County College's {name}: {type_cleaned} program."

                # --- Extract Program Hours ---
                program_hours = ""

                crd_tot_div = soup.find('div', class_='crd-tot')  # Find the div containing total credits
                if crd_tot_div:
                    total_credits_span = crd_tot_div.find('span', class_='total_numbl')
                    if total_credits_span:
                        program_hours = total_credits_span.get_text(strip=True)  # Extract and clean the number
                        
                # --- Extract URL ---
                # Get the link from the <a class="btn-green"> element.
                download_link = soup.find('a', class_='btn-green')
                if download_link:
                    career_url = download_link.get('href')

                # --- Extract Outcomes ---
                outcomes = []
                framework_id = ""  # Only generated if outcomes are found
                prog_outcomes = soup.find('div', class_='prog_outcomes')
                if prog_outcomes:
                    outcome_list = prog_outcomes.find('ul')
                    if outcome_list:
                        list_items = outcome_list.find_all('li')
                        outcomes = [format_outcome(li.get_text()) for li in list_items]
                        if outcomes:
                            framework_id = 'ce-' + str(uuid.uuid4())
                    else:
                        print(f"No outcome list found in file {filename}")
                else:
                    outcomes = []
                
                #Create a consistent name and remove Certificate from the end.
                if name.endswith("Certificate"):
                    #print("Certificate name is "+ name)
                    name = name.replace("Certificate","").strip()
                    name = name + ": " + type_cleaned
                    #print("New Certificate name is "+ name)
                elif name.endswith("Certificate of Achievement"):
                    #print("Certificate of Achievement name is "+ name)
                    name = name.replace("Certificate of Achievement","").strip()
                    name = name + ": " + type_cleaned
                    #print("New Certificate of Achievement name is "+ name)
                else:
                    name = name + ": " + type_cleaned
                
                #Create Subject Webpage
                url = "https://www.course-catalog.com/mcc/C/2024-2025/degree/"+ filename.replace(".html","").strip()

                # --- Append the Credential Data ---
                data.append({
                    'Filename': filename,
                    'Credential Name': name,
                    'Credential Named Type': nameType,
                    'Internal Code': internal_code,
                    'URL': url,
                    'Career_url': career_url,
                    'Type': type_mapped,
                    'Description': description,
                    'Hours': program_hours,
                    'Outcomes': framework_id
                })

                # --- Build Competency Data for Outcomes ---
                if outcomes:
                    # Competency framework entry
                    competency_framework_entry = {
                        "ceasn:comment": name,
                        "@id": framework_id,
                        "@type": "ceasn:CompetencyFramework",
                        "ceasn:description": "Graduates of the Program will be able to:",
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

    # --- Write CSV Outputs ---
    df = pd.DataFrame(data)
    output_csv = os.path.join('parsed_credentials.csv')
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"Data successfully parsed and saved to {output_csv}")

    df_competency = pd.DataFrame(competency_data)
    competency_csv = r"C:\text\NJ\Middlesex\credential\Review\Middlesex_BU_Credit_Credential_Competencies.csv"
    df_competency.to_csv(competency_csv, index=False, encoding="utf-8-sig")
    print(f"Competency data successfully saved to {competency_csv}")

# --- Specify the directory containing HTML files ---
# The subject webpage is "https://www.course-catalog.com/mcc/C/2024-2025/degree/"
directory_path = r"C:\text\NJ\Middlesex\credential\CredentialsHTML"
parse_html(directory_path)
