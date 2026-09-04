from bs4 import BeautifulSoup
from bs4.element import Tag  # Ensure Tag is correctly imported
import pandas as pd
import os
import re
import uuid

def map_type(type_):
    type_mapping = {
        "A.A.": "AssociateOfArtsDegree",
        "A.A. - Liberal Arts": "AssociateOfArtsDegree",
        "A.A.S.": "AssociateOfAppliedScienceDegree",
        "A.A.S": "AssociateOfAppliedScienceDegree",
        "A.A.S. - Business Management": "AssociateOfAppliedScienceDegree",
        "A.A.S. - Computer Information Systems": "AssociateOfAppliedScienceDegree",
        "A.A.S. - Graphic Design": "AssociateOfAppliedScienceDegree",
        "A.A.S. - Technical Studies": "AssociateOfAppliedScienceDegree",
        "A.F.A.": "AssociateOfArtsDegree",
        "A.F.A. - Studio Arts": "AssociateOfArtsDegree",
        "A.S.": "AssociateOfScienceDegree",
        "A.S. - Science/Mathematics": "AssociateOfScienceDegree",
        "C.O.A.": "Certificate",
        "Certificate": "Certificate",
        "CT.": "Certificate",
        "CT.A.": "Certificate",
        "JFK Muhlenberg Harold B. and Dorothy A. Snyder Schools of Nursing and Medical Imaging, A.S.": "AssociateOfScienceDegree",
        "Restaurant, and Tourism Management, A.A.S.": "AssociateOfAppliedScienceDegree",
        "Restaurant, and Tourism Management, CT.A.": "Certificate",
        "Suggested Grades 4-12, A.A.": "AssociateOfArtsDegree",
        "Suggested Grades Pre-K-3, A.A.": "AssociateOfArtsDegree",
        "Trinitas School of Nursing/RWJ Barnabas Health, A.S.": "AssociateOfScienceDegree",
        "AA": "AssociateOfArtsDegree",
        "AAS": "AssociateOfAppliedScienceDegree",
        "Academic Certificate": "Certificate",
        "AS": "AssociateOfScienceDegree",
        "Certificate of Achievement": "Certificate"
    }
    # Default to original type if not in dictionary
    return type_mapping.get(type_.strip(), type_)

def parse_html(directory):
    data = []
    competency_data = [] # List for competency framework and competencies

    # Traverse through each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

                # Extract the program name and type
                title_element = soup.find('title')
                if title_element:
                    title_text = title_element.text.strip()
                    if '-' in title_text:
                        #name, type_ = title_text.split('-', 1)
                        
                        # Reversing the string to split from the last hyphen
                        reversed_text = title_text[::-1]
                        parts = reversed_text.split('-', 1)  # Split once from the reversed string
                        # Reversing the split parts back to normal order
                        name = parts[1][::-1]  # Reverse the second part back to normal
                        type_ = parts[0][::-1]  # Reverse the first part back to normal
                        
                        name = name.strip()
                        nameType = type_.replace(' < Essex County College','').strip()
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
                        type_ = 'No Type'
                else:
                    name = 'No Title'
                    type_ = 'No Type'

                # Extract description
                description_container = soup.find('div', class_='woocommerce-product-details__short-description')
                if description_container:
                    # Get text directly from the container
                    description_text = description_container.get_text(strip=True)
                    if description_text:
                        description = description_text
                    else:
                        # Fallback: Look for the next sibling <div> with actual text if main description is empty
                        fallback_container = description_container.find_next_sibling('div', text=True)
                        if fallback_container:
                            description = fallback_container.get_text(strip=True)
                        else:
                            description = 'No Description no tag'
                else:
                    description = "Essex County College's " + name + ": "+type_cleaned+" program."

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
                #Subject Webpoage
                #Find the link with the text "Download Page (PDF)"
                download_link = soup.find('a', string="Download Page (PDF)")
                if download_link:
                    # Extract the href attribute
                    href = download_link.get('href')
                    
                    # Remove the filename from the URL (using os.path.dirname)
                    directory_path = os.path.dirname(href)
                    
                    # Prepend the base URL
                    url = "https://catalog.essex.edu" + directory_path

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
                        # Generate a unique framework ID for this program's competencies
                        framework_id = 'ce-' + str(uuid.uuid4())
                        list_items = outcome_list.find_all('li')
                        outcomes = [format_outcome(li.get_text()) for li in list_items]
                    else:
                        print(f"No list found following the outcome section in file {filename}")
                else:
                    outcome_container = soup.find('div', class_='woocommerce-Tabs-panel woocommerce-Tabs-panel--ywtm-learning-outcomes-218 panel entry-content wc-tab')
                    if outcome_container:
                        outcome_list = outcome_container.find_next(lambda tag: tag.name in ['ul', 'ol'])  # Search any following ul or ol
                        if outcome_list:
                            # Generate a unique framework ID for this program's competencies
                            framework_id = 'ce-' + str(uuid.uuid4())
                            list_items = outcome_list.find_all('li')
                            outcomes = [format_outcome(li.get_text()) for li in list_items]
                        else:
                            print(f"No list found following the outcome section in file {filename}")

                # Append to list
                data.append({
                    'Filename': filename,
                    'Credential Name': name + ": "+type_cleaned,
                    'Credential Named Type': nameType,
                    'Internal Code': internal_code,
                    'URL': url,
                    'Type': type_,
                    'Description': description,
                    'Hours': program_hours,
                    'Outcomes': framework_id
                })
                # ----- Build competency data for this file -----
                # Competency framework entry
                competency_framework_entry = {
                    "ceasn:comment": name + ": "+type_cleaned,
                    "@id": framework_id,
                    "@type": "ceasn:CompetencyFramework",
                    "ceasn:description": "Upon completion of this program students will be able to:",
                    "ceasn:inLanguage": "en",
                    "ceasn:name": f"{name}: {type_cleaned}'s Program Learning Outcomes",
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

    # Convert to DataFrame
    df = pd.DataFrame(data)
    output_csv = os.path.join('parsed_credentials.csv')
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"Data successfully parsed and saved to {output_csv}")
    
    # Save the competency data to CSV
    df_competency = pd.DataFrame(competency_data)
    competency_csv = r"C:\text\NJ\Middlesex\credentials\Review\Middlesex_BU_Credit_Credential_Competencies.csv"
    df_competency.to_csv(competency_csv, index=False, encoding="utf-8-sig")
    print(f"Competency data successfully saved to {competency_csv}")

# Specify the directory containing HTML files
directory_path = r"C:\text\NJ\Middlesex\credentials\CredentialHTML"
parse_html(directory_path)