from bs4 import BeautifulSoup
import pandas as pd
import os
import uuid


def parse_html_files(directory):
    # Create empty lists to store the data
    program_data = []
    competency_data = []
    
    # Iterate over each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            file_path = os.path.join(directory, filename)
            
            # Read the HTML content
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                
                # Extract the canonical URL
                canonical_link = soup.find('link', rel='canonical')
                url = canonical_link['href'] if canonical_link else "No URL found"
                
                # Extract the credential title
                title_elem = soup.find('h1')
                title = title_elem.get_text(strip=True) if title_elem else "No Title Found"
                
                # Extract credential description
                description_elem = soup.find('div', class_='field field--name-body field--type-text-with-summary field--label-hidden field__item')
                description = description_elem.get_text(separator=' ', strip=True) if description_elem else "No description available"
                
                # Get Credits
                total_credits_div = soup.find('div', class_='col-10', string=lambda text: text and "Total Credits" in text)
                credits_ = ""
                if total_credits_div:
                    next_div = total_credits_div.find_next_sibling('div')
                    if next_div:
                        credits_ = next_div.get_text(strip=True)
                
                # Extract program outcomes (competencies)
                outcomes_elem = soup.find('div', class_='field field--name-field-program-outcomes field--type-text-with-summary field--label-above')
                formatted_outcomes = []
                if outcomes_elem:
                    outcomes_items = outcomes_elem.find_all('li')
                    for item in outcomes_items:
                        outcome = item.get_text(separator=' ', strip=True)
                        outcome = outcome[0].upper() + outcome[1:] if outcome else outcome
                        if outcome.endswith(';'):
                            outcome = outcome[:-1]
                        if outcome and not outcome.endswith('.'):
                            outcome += '.'
                        formatted_outcomes.append(outcome)
                
                outcomes_text = " | ".join(formatted_outcomes) if formatted_outcomes else "No outcomes listed"
                
                # Assign a unique Framework ID
                framework_id = 'ce-' + str(uuid.uuid4())
                
                # Append data to the program CSV list
                program_data.append({
                    "Filename": filename,
                    "URL": url,
                    "Title": title,
                    "Description": description,
                    "Program Outcomes": framework_id,
                    "Credits": credits_,
                })
                
                # Append competency framework data
                competency_data.append({
                    "ceasn:comment": title,
                    "@id": framework_id,
                    "@type": "ceasn:CompetencyFramework",
                    "ceasn:description": f"Upon completion of this program students will be able to:",
                    "ceasn:inLanguage": "en",
                    "ceasn:name": f"{title}'s Program Learning Outcomes",
                    "ceasn:publicationStatusType": "http://credreg.net/ctdlasn/vocabs/publicationStatus/Published",
                    "ceasn:source": url
                })
                
                # Append each program outcome as a separate competency
                for outcome in formatted_outcomes:
                    competency_data.append({
                        "@id": 'ce-' + str(uuid.uuid4()),
                        "@type": "ceasn:Competency",
                        "ceasn:inLanguage": "en",
                        "ceasn:competencyLabel": "Program Learning Outcome",
                        "ceasn:competencyText": outcome,
                        "ceasn:isPartOf": framework_id
                    })
    
    # Convert lists to DataFrames
    df_program = pd.DataFrame(program_data)
    df_competency = pd.DataFrame(competency_data)
    
    # Save DataFrames to CSV
    df_program.to_csv("credentials_extracted.csv", index=False, encoding="utf-8-sig")
    df_competency.to_csv(r"C:\text\NJ\Atlantic Cape\credentials\Review\Atlantic_Cape_BU_Credit_Credential_Competencies.csv", index=False, encoding="utf-8-sig")
    print("Data successfully extracted and saved to credentials_extracted.csv and competencies_extracted.csv")


# Define the directory path
directory_path = r"C:\\text\\NJ\\Atlantic Cape\\credentials\\CredentialsHTML"

# Call the function to parse HTML files and save data
parse_html_files(directory_path)
