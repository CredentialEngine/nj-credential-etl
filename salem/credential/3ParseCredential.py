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

# Custom function to check the combined text of <h2> tags including nested elements
def matches_total_credits(tag):
    if tag.name == 'h2' and re.search(r'Total Credits \d+', tag.get_text(), re.I):
        return True
    return False

def map_type(type_):
    type_mapping = {
        # Extend or adjust mappings as needed
        "Associate in Applied Science": "AssociateofAppliedScienceDegree",
        "Associate in Applied Science | Joint degree in partnership with Atlantic Cape Community College": "AssociateofAppliedScienceDegree",
        "Associate in Arts": "AssociateofArtsDegree",
        "Associate in Fine Arts": "AssociateofArtsDegree",
        "Associate in Science": "AssociateofScienceDegree",
        "Career Certificate": "Certificate",
        "Certificate": "Certificate",
        # Add more mappings here
    }
    return type_mapping.get(type_.strip(), type_)

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
            with open(filepath, 'r', encoding='utf-8-sig') as file:
                soup = BeautifulSoup(file, 'html.parser')

                #credential_name
                h1 = soup.find('h1')
                title_text = h1.get_text(strip=True) if h1 else soup.find('title').get_text(strip=True) if soup.find('title') else "No Title"
                #Type
                span_tag = soup.find('span', class_=re.compile(r'coh-style-pre-heading'))
                if span_tag:
                    type_ = span_tag.text.strip()
                    type_ = type_.replace("| Joint degree in partnership with Atlantic Cape Community College","").strip()
                # Clean institution-specific text
                name = title_text.replace(" | Salem Community College", "").strip()
                
                description_div = soup.find('div', class_=re.compile(r'coh-style-text-color-dark-background'))
                
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

                #Career Information - find the 'Career' section by locating the preceding 'a' tag
                career_section = soup.find("a", string="Career")
                # Find the next div that contains the list
                if career_section:
                    careers_div = career_section.find_next("div", class_="coh-accordion-tabs-content")
                    if careers_div:
                        # Extract all list items (LI) under UL
                        career_list = [li.get_text(strip=True) for li in careers_div.find_all("li")]
                        # Join the careers with a pipe separator
                        career = " | ".join(career_list)
                    else:
                        career = ""
                else:
                    career = ""


                #Cost- Find the element containing "Total Program Cost"
                cost_element = soup.find(string=re.compile("Total Program Cost"))
                # Extract and clean the cost value
                if cost_element:
                    cost_match = re.search(r"\$([\d,]+(?:\.\d{2})?)", cost_element)
                    if cost_match:
                        cost = cost_match.group(1).replace(",", "")  # Remove commas
                    else:
                        cost = ""
                else:
                    cost = ""
                
                # Outcomes - Example usage
                outcomes = extract_outcomes(soup)

                # Use the custom function in find
                total_credits_tag = soup.find(matches_total_credits)
                #Framework ID
                framework_id = ""
                if outcomes:
                    framework_id = 'ce-' + str(uuid.uuid4())
                    
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
                url = soup.find("link", rel="canonical")["href"] if soup.find("link", rel="canonical") else "No URL"

                data.append({
                    'Filename': filename,
                    'Type': map_type(type_),
                    'Credential Name': name,
                    'Name': name+": "+type_,
                    #'Internal Identifier': programid,
                    'Description': description,
                    'URL': url,
                    #'Outcomes': framework_id,
                    #'Hours': total_credits
                    'Occupation': career,
                    'Cost': "tuition~"+cost,
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
                        "ceasn:name": f"{name}: {type_}'s Student Learning Outcomes",
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
    df.to_csv(output_csv_path, index=False, encoding = 'utf-8-sig')
    print(f"Data successfully parsed and saved to {output_csv_path}")
    if outcomes:
        df_competency = pd.DataFrame(competency_data)
        competency_csv = r"C:\text\NJ\Salem\credential\Review\Salem_BU_Credit_Credential_Competencies.csv"
        df_competency.to_csv(competency_csv, index=False, encoding="utf-8-sig")
        print(f"Competency data successfully saved to {competency_csv}")

# Specify the directory containing HTML files
directory_path = r"C:\text\NJ\Salem\credential\CredentialHTML"
parse_html(directory_path)