from bs4 import BeautifulSoup
from bs4.element import Tag  # Ensure Tag is correctly imported
import pandas as pd
import os
import re

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
    data = []
    # Traverse through each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

                # Extract the program name
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

                #Program Code
                program_code_text = ""
                program_code_container = soup.find('th', string=lambda t: t and t.strip() == "Program Code")
                if program_code_container:
                    #print("Found program Code container and Program Code text for " + filename)
                    td_container = program_code_container.find_next_sibling('td')
                    if td_container:
                        program_code_text = td_container.get_text(strip=True)
                
                #Credential Type
                type_ = ""
                abbreviation =""
                if program_code_text:
                    abbreviation, _type = program_code_text.split('.')
                    type_ = map_type(_type)
                    name = name+": "+_type

                #CIP Code
                cip_code_text = ""
                cip_code_container = soup.find('th', string=lambda t: t and t.strip() == "CIP Code")
                if cip_code_container:
                    #print("Found CIP Code container and CIP Code text for " + filename)
                    td_container = cip_code_container.find_next_sibling('td')
                    if td_container:
                        cip_code_text = td_container.get_text(strip=True)

                        
                # Extract description
                description_container = soup.find('div', class_='woocommerce-product-details__short-description')
                if description_container:
                    # Get text directly from the container
                    description_text = description_container.get_text(strip=True)
                    if description_text:
                        description = description_text
                        description=description.replace(".Apply & Register",".")
                    else:
                        # Fallback: Look for the next sibling <div> with actual text if main description is empty
                        fallback_container = description_container.find_next_sibling('div', string=True)
                        if fallback_container:
                            description = fallback_container.get_text(strip=True)
                            description=description.replace(".Apply & Register",".")
                        else:
                            description = 'No Description no tag'
                else:
                    description = 'No Description no container'

                #Extract a canonical URL if available
                canonical_link = soup.find('link', rel='canonical')
                url = canonical_link['href'] if canonical_link and canonical_link.has_attr('href') else ""
                
                # Extract total program hours
                hours_code_text = ""
                #hours_code_container = soup.find('td', string=lambda t: t and t.strip() == "Total Minimum Credits")
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
                outcome_section = soup.find(lambda tag: (tag.name == 'h2' or tag.name == 'h3' or tag.name == 'h4' or tag.name == 'strong' or tag.name == 'p') and any(phrase in tag.string for phrase in [
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
                #print(f"No outcome section found in file {filename}")

                # Append to list
                data.append({
                    'Filename': filename,
                    'Credential Name': name,
                    'Credential Program Code': program_code_text,
                    'Type': type_,
                    'CIP': cip_code_text,
                    'URL': url,
                    'Description': description,
                    'Hours': hours_code_text,
                    'Outcomes': outcomes
                })

    # Convert to DataFrame
    df = pd.DataFrame(data)
    output_csv = os.path.join('parsed_credentials.csv')
    df.to_csv(output_csv, index=False)
    print(f"Data successfully parsed and saved to {output_csv}")

# Specify the directory containing HTML files
directory_path = r"C:\text\NJ\Camden\credentials\CredentialHTML"
parse_html(directory_path)
