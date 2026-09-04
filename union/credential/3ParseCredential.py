from bs4 import BeautifulSoup
from bs4.element import Tag  # Ensure Tag is correctly imported
import pandas as pd
import uuid
import os
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def clean_url(url):
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Parse query parameters into a dictionary
    query_params = parse_qs(parsed_url.query)
    
    # Remove the 'hl' parameter if it exists
    query_params.pop('hl', None)
    query_params.pop('returnto', None)
    query_params.pop('_gl', None)
    
    # Reconstruct the query string without 'hl'
    new_query = urlencode(query_params, doseq=True)
    
    # Rebuild the full URL
    cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, new_query, parsed_url.fragment))
    
    return cleaned_url


def map_type(type_):
    type_mapping = {
        "A.A.": "AssociateofArtsDegree",
        "A.A.S.": "AssociateofAppliedScienceDegree",
        "A.A.S": "AssociateofAppliedScienceDegree",
        "A.S.": "AssociateofScienceDegree",
        "CT.": "Certificate",
        "CT.A.": "Certificate",
        "JFK Muhlenberg Harold B. and Dorothy A. Snyder Schools of Nursing and Medical Imaging, A.S.": "AssociateofScienceDegree",
        "Restaurant, and Tourism Management, A.A.S.": "AssociateofAppliedScienceDegree",
        "Restaurant, and Tourism Management, CT.A.": "Certificate",
        "Suggested Grades 4-12, A.A.": "AssociateofArtsDegree",
        "Suggested Grades Pre-K-3, A.A.": "AssociateofArtsDegree",
        "Trinitas School of Nursing/RWJ Barnabas Health, A.S.": "AssociateofScienceDegree"

    }
    # Default to original type if not in dictionary
    return type_mapping.get(type_.strip(), type_)

# Find the next <p> tag that contains the actual description
def collect_description_until_outcomes(soup):
    # Use a regular expression to allow for flexible matching
    description_start = soup.find(string=re.compile(r"\s*Program Description\s*", re.I))
    
    if not description_start:
        return "Program Description not found."
    
    description_texts = []
    outcome_phrases = [
        # List all your phrases here, adding \s* around and inside to handle arbitrary spaces
        r"\s*Upon\s+successful\s+completion\s+of\s+all\s+program\s+requirements,\s+graduates\s+will\s+be\s+able\s+to:\s*",
        # Add more phrases as needed
        'Upon completion of this program, graduates will be able to:',
        'Upon successful completion of all program requirements, graduates will be able to:',
        'Upon successful completion of all program requirements, graduates will be&nbsp;able to:',
        'Upon successful completion of all program requirements, graduates',
        'Upon successful completion of all requirements, graduates will be able to:',
        'Upon successful completion of the Certificate of Achievement requirements, graduates will be able to:',
        'End of Program Student Learning Outcomes',
        'Upon successful completion, graduates will be able to:',
        'Upon successful completion of the Emergency Medical Studies graduates will be able to:',
        'Upon successful completion of the Emergency Medical Studies Certificate of Achievement graduates will be able to:',
        'At the end of this program, students will be able to:',
        'Upon successful completion of all program requirements, graduates will be able to:'
        'According to the National Research Council, students should be able to demonstrate that:',
        'Program Outcomes:',
        'Program Goals:',
        'Goals and objectives:',
        'The objectives of this program are to:',
        'Successful graduates of the Machine Tool Technology Program can:',
        'The objectives of this program are to:'
    ]

    # Compile a regex from the outcome phrases to check against each tag's text
    outcome_regex = re.compile('|'.join(outcome_phrases), re.I)

    # Collect all elements until an outcome section is found
    element = description_start.find_next('p')
    while element:
        if isinstance(element, Tag):  # Corrected from BeautifulSoup.Tag to Tag
            if outcome_regex.search(element.get_text()):
                break  # Stop collecting text when an outcome section starts
            description_texts.append(element.get_text(strip=True))
        element = element.find_next_sibling()

    return ' '.join(description_texts) if description_texts else "No Description found."

# Custom function to check the combined text of <h2> tags including nested elements
def matches_total_credits(tag):
    if tag.name == 'h2' and re.search(r'Total Credits \d+', tag.get_text(), re.I):
        return True
    return False

def format_outcome(text):
    """Format the outcome text by stripping leading numbering, capitalizing the first letter, and ensuring it ends with a period."""
    text = text.strip()
    # Remove leading numbering such as "1. " or "10. "
    text = re.sub(r'^\d+\.\s+', '', text)
    if text.endswith(';'):
        text = text[:-1]
    if text.endswith(','):
        text = text[:-1]
    if text:
        text = text[0].upper() + text[1:]  # Capitalize the first letter
        if not text.endswith('.'):
            text += '.'  # Ensure it ends with a period
    return text

def parse_html(directory):
    data = []
    competency_data = []

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
                #description = soup.find('h2', class_='ProgramDescription').p.text if soup.find('h2', class_='ProgramDescription') and soup.find('h2', class_='ProgramDescription').p else 'No Description'
                #description_tag = soup.find('h2', string=lambda text: text and "Program Description" in text)
                #description = description_tag.find_next('p').text if description_tag and description_tag.find_next('p') else 'No Description'
                
                # Locate the <h2> element that contains 'Program Description' in its text
                description_tag = None
                for h2 in soup.find_all('h2'):
                    if 'Program Description' in h2.get_text():
                        description_tag = h2
                        break

                # Example usage
                description = collect_description_until_outcomes(soup)

                # Extract total program hours Find the <h2> tag that contains "Total Program Hours:"
                #program_hours_tag = soup.find(string=lambda text: text and "Total Program Credits:" in text)
                program_hours_tag = soup.find(string=lambda text: text and ("Total Program Credits:" in text or "Total Program Credits (including all pre-clinical course work):" in text))
                
                # Extract the number from the text
                if program_hours_tag:
                    hours = program_hours_tag.get_text(strip=True).split(":")[-1].strip()
                else:
                    hours = ""
                    
                outcome_section = soup.find(lambda tag: (tag.name == 'h2' or tag.name == 'h4' or tag.name == 'strong' or tag.name == 'p') and any(phrase in tag.string for phrase in [
                    'Upon completion of this program, graduates will be able to:',
                    'Upon successful completion of all program requirements, graduates will be able to:',
                    'Upon successful completion of all program requirements, graduates will be&nbsp;able to:',
                    'Upon successful completion of all program requirements, graduates',
                    'Upon successful completion of all requirements, graduates will be able to:',
                    'Upon successful completion of the Certificate of Achievement requirements, graduates will be able to:',
                    'End of Program Student Learning Outcomes',
                    'Upon successful completion, graduates will be able to:',
                    'Upon successful completion of the Emergency Medical Studies graduates will be able to:',
                    'Upon successful completion of the Emergency Medical Studies Certificate of Achievement graduates will be able to:',
                    'At the end of this program, students will be able to:',
                    'Upon successful completion of all program requirements, graduates will be able to:'
                    'According to the National Research Council, students should be able to demonstrate that:',
                    'Program Outcomes:',
                    'Program Goals:',
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
                        url = "http://onlinecatalog.ucc.edu/" + raw_url.split("&print")[0]  # Remove '&print'
                        url = clean_url(url)

                # Append to list
                data.append({
                    'Filename': filename,
                    'Credential Name': name,
                    'Credential Named Type': nameType,
                    'Credential Type': type_,
                    'Name': name+": "+nameType,
                    'Description': description,
                    'URL': url,
                    'Hours': hours,
                    'Outcomes': framework_id,
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
    competency_csv = r"C:\text\NJ\Union\credential\Review\Union_BU_Credit_Credential_Competencies.csv"
    df_competency.to_csv(competency_csv, index=False, encoding="utf-8-sig")
    print(f"Competency data successfully saved to {competency_csv}")

# Specify the directory containing HTML files
directory_path = r"C:\text\NJ\Union\credential\CredentialHTML"
parse_html(directory_path)
