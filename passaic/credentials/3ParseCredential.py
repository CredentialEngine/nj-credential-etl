import os
import re
from bs4 import BeautifulSoup
import pandas as pd
import uuid


def map_type(type_):
    type_mapping = {
        # Extend or adjust mappings as needed
        "Associate in Applied Science": "AssociateofAppliedScienceDegree",
        "Associate in Arts": "AssociateofArtsDegree",
        "Associate in Fine Arts": "AssociateofArtsDegree",
        "Associate in Science": "AssociateofScienceDegree",
        "Career Certificate": "Certificate",
        "Certificate of Achievement": "Certificate",

        # Add more mappings here
    }
    return type_mapping.get(type_.strip(), type_)


def parse_html(directory):
    data = []
    competency_data = []
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

                # Find the credential type and name
                credential_type_tag = soup.find('h3')
                if credential_type_tag:
                    credential_type = credential_type_tag.text.strip()
                    # Find the next sibling that is an h4 tag after the h3 tag
                    type_ = map_type(credential_type)
                    credential_name_tag = credential_type_tag.find_next_sibling('h4')
                    if credential_name_tag:
                        credential_name = credential_name_tag.text.strip()
                        credential_name = credential_name.replace("\n","").replace("\t","").strip()
                    else:
                        credential_name = 'No Name Found'
                else:
                    credential_type = 'No Type Found'
                    credential_name = 'No Name Found'


                # Find the description
                description = soup.find('p', class_='Curriculasidebartext')
                if description:
                    description = description.text.strip()
                elif credential_type_tag.find_next_sibling('p'):
                    description_p = credential_type_tag.find_next_sibling('p')
                    description = description_p.text.strip()
                else:
                    description = 'No Description Found'

                # Find outcomes
                outcomes = []
                outcomes_section = soup.find('p', class_='Curriculasidebargraduateswill')
                if outcomes_section:
                    outcomes_list = outcomes_section.find_next_sibling('ul')
                    if outcomes_list:
                        #outcomes = [li.text.strip() for li in outcomes_list.find_all('li')]
                        outcomes = []
                        for li in outcomes_list.find_all('li'):
                            # Process each li individually
                            text_parts = []
                            for element in li.children:
                                if element.name == 'br':  # Stop processing further if a <br> tag is encountered
                                    break
                                if isinstance(element, str):  # Check if the element is a NavigableString (text)
                                    text_parts.append(element.strip())
                                elif element.name in ['span', 'strong', 'em']:  # You might want to include other tags you expect to contain important text
                                    text_parts.append(element.get_text().strip())

                            # Join all parts of text collected from this li, before a <br> tag
                            outcome_text = " ".join(text_parts)
                            outcomes.append(outcome_text)
                elif soup.find('p', string=re.compile(r"Graduates will be able to:")):
                    outcomes_section = soup.find('p', string=re.compile(r"Graduates will be able to:"))
                    outcomes_list = outcomes_section.find_next_sibling('ul')
                    outcomes_list_ol = outcomes_section.find_next_sibling('ol')
                    if outcomes_list:
                        #outcomes = [li.text.strip() for li in outcomes_list.find_all('li')]
                        outcomes = []
                        for li in outcomes_list.find_all('li'):
                            # Process each li individually
                            text_parts = []
                            for element in li.children:
                                if element.name == 'br':  # Stop processing further if a <br> tag is encountered
                                    break
                                if isinstance(element, str):  # Check if the element is a NavigableString (text)
                                    text_parts.append(element.strip())
                                elif element.name in ['span', 'strong', 'em']:  # You might want to include other tags you expect to contain important text
                                    text_parts.append(element.get_text().strip())

                            # Join all parts of text collected from this li, before a <br> tag
                            outcome_text = " ".join(text_parts)
                            outcomes.append(outcome_text)
                    if outcomes_list_ol:
                        outcomes = []
                        for li in outcomes_list_ol.find_all('li'):
                            # Process each li individually
                            text_parts = []
                            for element in li.children:
                                if element.name == 'br':  # Stop processing further if a <br> tag is encountered
                                    break
                                if isinstance(element, str):  # Check if the element is a NavigableString (text)
                                    text_parts.append(element.strip())
                                elif element.name in ['span', 'strong', 'em']:  # You might want to include other tags you expect to contain important text
                                    text_parts.append(element.get_text().strip())

                            # Join all parts of text collected from this li, before a <br> tag
                            outcome_text = " ".join(text_parts)
                            outcomes.append(outcome_text)
                        
                elif soup.find('p', string=re.compile(r"Upon successful completion of the program students will")):
                    outcomes_section = soup.find('p', string=re.compile(r"Upon successful completion of the program students will"))
                    outcomes_list = outcomes_section.find_next_sibling('ul')
                    if outcomes_list:
                        outcomes = [li.text.strip() for li in outcomes_list.find_all('li')]
                elif soup.find('p', string=re.compile(r"Upon completion of this certificate, students will be able to:")):
                    outcomes_section = soup.find('p', string=re.compile(r"Upon completion of this certificate, students will be able to:"))
                    outcomes_list = outcomes_section.find_next_sibling('ul')
                    if outcomes_list:
                        outcomes = [li.text.strip() for li in outcomes_list.find_all('li')]
                elif soup.find('p', string=re.compile(r"Students who complete the program will be able to:")):
                    outcomes_section = soup.find('p', string=re.compile(r"Students who complete the program will be able to:"))
                    outcomes_list = outcomes_section.find_next_sibling('ol')
                    if outcomes_list:
                        outcomes = [li.text.strip() for li in outcomes_list.find_all('li')]
                elif soup.find('strong', string=re.compile(r"Upon completion of the certificate, students will be able to:")):
                    outcomes_section = soup.find('strong', string=re.compile(r"Upon completion of the certificate, students will be able to:"))
                    if outcomes_section:
                        # Navigate to the parent 'p' and find the next sibling 'ul'
                        parent_p = outcomes_section.parent.parent  # Going up twice to reach the 'p' tag
                        outcomes_list = parent_p.find_next_sibling('ul')
                        if outcomes_list:
                            #outcomes = [li.text.strip() for li in outcomes_list.find_all('li')]
                            outcomes = []
                            for li in outcomes_list.find_all('li'):
                                # Process each li individually
                                text_parts = []
                                for element in li.children:
                                    if element.name == 'br':  # Stop processing further if a <br> tag is encountered
                                        break
                                    if isinstance(element, str):  # Check if the element is a NavigableString (text)
                                        text_parts.append(element.strip())
                                    elif element.name in ['span', 'strong', 'em']:  # You might want to include other tags you expect to contain important text
                                        text_parts.append(element.get_text().strip())

                                # Join all parts of text collected from this li, before a <br> tag
                                outcome_text = " ".join(text_parts)
                                outcomes.append(outcome_text)
                elif soup.find('p', string=re.compile(r"Upon completion of the certificate, students will be able to:")):
                    outcomes_section = soup.find('p', string=re.compile(r"Upon completion of the certificate, students will be able to:"))
                    outcomes_list = outcomes_section.find_next_sibling('ul')
                    if outcomes_list:
                        outcomes = [li.text.strip() for li in outcomes_list.find_all('li')]
                elif credential_name_tag and credential_name_tag.find_next('p'):
                    p_tag = credential_name_tag.find_next('p')
                    ol_tag = p_tag.find_next('ol')
                    ul_tag = p_tag.find_next('ul')
                    if ol_tag:
                        #outcomes = [li.text.strip() for li in ol_tag.find_all('li')]
                        outcomes = []
                        for li in outcomes_list.find_all('li'):
                            # Process each li individually
                            text_parts = []
                            for element in li.children:
                                if element.name == 'br':  # Stop processing further if a <br> tag is encountered
                                    break
                                if isinstance(element, str):  # Check if the element is a NavigableString (text)
                                    text_parts.append(element.strip())
                                elif element.name in ['span', 'strong', 'em']:  # You might want to include other tags you expect to contain important text
                                    text_parts.append(element.get_text().strip())

                            # Join all parts of text collected from this li, before a <br> tag
                            outcome_text = " ".join(text_parts)
                            outcomes.append(outcome_text)
                    if ul_tag:
                        #outcomes = [li.text.strip() for li in ul_tag.find_all('li')]
                        outcomes = []
                        for li in outcomes_list.find_all('li'):
                            # Process each li individually
                            text_parts = []
                            for element in li.children:
                                if element.name == 'br':  # Stop processing further if a <br> tag is encountered
                                    break
                                if isinstance(element, str):  # Check if the element is a NavigableString (text)
                                    text_parts.append(element.strip())
                                elif element.name in ['span', 'strong', 'em']:  # You might want to include other tags you expect to contain important text
                                    text_parts.append(element.get_text().strip())

                            # Join all parts of text collected from this li, before a <br> tag
                            outcome_text = " ".join(text_parts)
                            outcomes.append(outcome_text)

                # Find total credits
                total_credits = soup.find(string=re.compile('Total Credits'))
                #print(total_credits)
                MaxCredit = None
                if total_credits:
                    total_credits = total_credits.find_next('span')
                    if total_credits:
                        total_credits = total_credits.text.strip()
                        # Check if a dash is present in the string
                        if "-" in total_credits:
                            total_credits, MaxCredit = total_credits.split("-", 1)  # Split into two parts
                    else:
                        total_credits = 'Credits Not Found'
                else:
                    total_credits = 'Credits Not Found'
                #URL from filename
                url = "https://catalog.pccc.edu/program/" + re.search(r'_(\d+)\.html$', filename).group(1)
                #Framework ID
                framework_id = ""
                if outcomes:
                    framework_id = 'ce-' + str(uuid.uuid4())

                data.append({
                    'Filename': filename,
                    'Credential Type': credential_type,
                    'Type': type_,
                    'Credential Name': credential_name,
                    'Name': credential_name+": "+credential_type,
                    'Description': description,
                    'URL': url,
                    'Outcomes': framework_id,
                    'Hours': total_credits,
                    'MaxCredit': MaxCredit,
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
    competency_csv = r"C:\text\NJ\Passaic\credentials\Review\Passaic_BU_Credit_Credential_Competencies.csv"
    df_competency.to_csv(competency_csv, index=False, encoding="utf-8-sig")
    print(f"Competency data successfully saved to {competency_csv}")
    

# Specify the directory containing HTML files
directory_path = r"C:\text\NJ\Passaic\credentials\CredentialHTML"
parse_html(directory_path)
