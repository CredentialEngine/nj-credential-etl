from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import uuid
    
def map_type(type_):
    type_mapping = {
        "(AA)": "AssociateofArtsDegree",
        "(AAS)": "AssociateofAppliedScienceDegree",
        "(AFA)": "AssociateofArtsDegree",
        "(AS)": "AssociateofScienceDegree",
        "(Certificates)": "Certificate",
        "(Workforce Development)": "Certificate",
        "Unknown": "Certificate",

    }
    return type_mapping.get(str(type_).strip(), type_)

def extract_title_and_type(soup, filename):
    """
    Extracts the credential’s title and type.
    Preference is given to an <h1> element; if not available, <title> is used.
    The type is derived by extracting text within parentheses (if present)
    or else from the filename.
    """
    # Prefer the <h1> tag if available
    h1 = soup.find('h1')
    if h1:
        title_text = h1.get_text(strip=True)
    else:
        title_tag = soup.find('title')
        title_text = title_tag.get_text(strip=True) if title_tag else "No Title"
    
    # Remove any trailing institution text
    title_text = title_text.replace(" Degrees | Programs Near Me | County College of Morris (CCM)", "").strip()
    
    # Try to get the type from text in parentheses (e.g. "Business Professional (Career Program)")
    type_cleaned = ""
    internal_code = ""
    paren_match = re.search(r'\((.*?)\)', title_text)
    #internal_code = re.search(r'\((.*?)\)', filename)
    internal_code = re.search(r'\(([^)]*)\)', filename)
    internal_code = internal_code.group(1) if internal_code else None

    if paren_match:
        type_cleaned = paren_match.group(1).strip()
    else:
        # Fallback: derive type from the filename (without extension)
        base = os.path.splitext(filename)[0]
        # If the filename contains parentheses, take text before them
        if "(" in base:
            type_cleaned = base.split("(")[0].strip()
        else:
            type_cleaned = base.strip()
    
    credential_type = map_type(type_cleaned)
    return title_text, credential_type, internal_code


def extract_outcomes(soup):
    """
    Extracts a list of outcome statements from an unordered list (<ul>)
    that appears after the phrase "students learn to" (or similar).
    
    The function stops extracting when the closing </ul> is encountered.
    """
    outcomes = []
    
    # Look for a phrase that introduces learning outcomes
    keywords = ["students learn to", "students learn how to", "graduates will be able to", "learn how to:"]
    
    # Search for a <p> tag containing one of the keywords
    outcome_intro = soup.find(lambda tag: tag.name == "p" and 
                              any(keyword in tag.get_text(strip=True).lower() for keyword in keywords))
    #Find student Outcomes section
    #studentoutcomes_section = soup.find(lambda tag: tag.name == "h3" and "student outcomes" in tag.get_text(strip=True).lower())
    studentoutcomes_section = soup.find(lambda tag: tag.name in ["h2", "h3"] and "outcomes" in tag.get_text(strip=True).lower())

    
    if outcome_intro:
        # The <ul> following this <p> should contain the outcome statements
        ul_tag = outcome_intro.find_next_sibling("ul")
        
        if ul_tag:
            for li in ul_tag.find_all("li"):
                text = li.get_text(strip=True)
                text = re.sub(r'^\d+\.\s*', '', text)  # Remove leading numbering
                if text.endswith(";"): # Remove trailing semicolon
                    text = text[:-1]
                if text.endswith("; and"): # Remove trailing semicolon followed by the word and
                    text = text[:-5]
                if text and not text.endswith('.'):
                    text += '.'
                outcomes.append(text.capitalize())
    elif studentoutcomes_section:
        # The <ol> following this <p> should contain the outcome statements
        ol_tag = studentoutcomes_section.find_next_sibling("ol")
        
        if ol_tag:
            for li in ol_tag.find_all("li"):
                text = li.get_text(strip=True)
                text = re.sub(r'^\d+\.\s*', '', text)  # Remove leading numbering
                if text.endswith(";"): # Remove trailing semicolon
                    text = text[:-1]
                if text.endswith("; and"): # Remove trailing semicolon followed by the word and
                    text = text[:-5]
                if text and not text.endswith('.'):
                    text += '.'
                outcomes.append(text.capitalize())
    return outcomes


def parse_html(directory):
    data = []
    competency_data = []  # List for competency framework and competency entries

    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                
                # Extract title and credential type information
                name, credential_type, internal_code = extract_title_and_type(soup, filename)
                # Extract total program hours (credits)
                #program_hours = extract_program_hours(soup)
                
                framework_id = ""  # Only generated if outcomes are found
                # Extract outcome statements (if any)
                outcomes = extract_outcomes(soup)
                if outcomes:
                    framework_id = 'ce-' + str(uuid.uuid4())
                
                # Extract the canonical URL
                canonical_tag = soup.find("link", rel="canonical")
                canonical_url = canonical_tag["href"] if canonical_tag else "No canonical URL found"

                # Extract the meta description
                meta_description_tag = soup.find("meta", attrs={"name": "description"})
                meta_description = meta_description_tag["content"] if meta_description_tag else "No meta description found"

                # Extract "What You Will Learn" description
                #description_section = soup.find(string=lambda text: "What You Will Learn" in text if text else False)
                description_section = soup.find(lambda tag: tag.name in ["h2", "h3"] and "what you will learn" in tag.get_text(strip=True).lower())
                #print("Found description_section for ", filename)
                description = ""
                if description_section:
                    # Get the following sibling elements for the actual description
                    parent = description_section.find_parent()
                    #next_elements = parent.find_next_siblings(["p", "ul"]) if parent else []
                    #print ("Next_elements is ", next_elements)
                    for element in parent:
                        if element.name == "p":
                            description += element.get_text(strip=True) + " "
                        elif element.name == "ul":
                            description += " ".join([li.get_text(strip=True) for li in element.find_all("li")]) + " "
                else:
                    description = meta_description

                # Extract "Careers in the Field" as occupations
                careers_section = soup.find(lambda tag: tag.name in ["h2", "h3"] and "careers in the field" in tag.get_text(strip=True).lower())
                occupations = ''
                if careers_section:
                    #print ("Found careers section in ", filename)
                    parent = careers_section.find_parent()
                    #print ("Found parent in ", parent)
                    ul_tag = parent.find("ul") if parent else None
                    if ul_tag:
                        #print ("Found ul", ul_tag)
                        occupations = [li.get_text(strip=True) for li in ul_tag.find_all("li")]
                    else:
                        print ("No ul_tag, bu career_section for file ", filename)
                        #occupations = parent.get_text(strip=True).replace("Careers in the Field","")
                        #occupations.append("No occupation list found")
                
                data.append({
                    'Filename': filename,
                    'Credential Name': name,
                    'Credential Type': credential_type,
                    #'Internal Code': internal_code,
                    #'Total Program Hours': program_hours,
                    'Outcomes': framework_id,
                    "URL": canonical_url,
                    #"Meta Description": meta_description,
                    "Description": description.strip(),
                    #"OccupationsOld": occupations,
                    "Occupation": "|".join(occupations) if isinstance(occupations, list) else occupations
                    })
                
    
    df = pd.DataFrame(data)
    output_csv = os.path.join('parsed_credentials.csv')
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"Data successfully parsed and saved to {output_csv}")

    # Load CSVs into DataFrames
    df1 = pd.read_csv(file1)  # credentials_parsed.csv
    #df2 = pd.read_csv(file2)  # parsed_credentials.csv
    df2 = df

    # Merge based on 'Program Link ' from df1 and 'URL' from df2, keeping all rows from df2
    merged_df = df2.merge(df1[['Program Link', 'Credential Type']], 
                           left_on='URL', right_on='Program Link', 
                           how='left')

    # Drop the 'Program Link ' column after merging (optional)
    merged_df.drop(columns=['Program Link'], inplace=True)

    merged_df['Type'] = merged_df['Credential Type_y'].apply(map_type)

    merged_df['Name'] = merged_df['Credential Name'] + ": " + merged_df['Credential Type_y'].str.replace(r"[()]", "", regex=True).replace(r"Certificates", "Certificate", regex=True)

    merged_df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"Updated CSV saved to: {output_file}")

    print(f"Competency data successfully saved to {competency_csv}")
    # --- Build Competency Data for Outcomes ---
                if outcomes:
                    # Competency framework entry
                    competency_framework_entry = {
                        "ceasn:comment": merged_df['Name'],
                        "@id": framework_id,
                        "@type": "ceasn:CompetencyFramework",
                        "ceasn:description": "Graduates will be able to:",
                        "ceasn:inLanguage": "en",
                        "ceasn:name": f"{name}'s Learning Outcomes",
                        "ceasn:publicationStatusType": "http://credreg.net/ctdlasn/vocabs/publicationStatus/Published",
                        "ceasn:source": canonical_url
                    }
                    competency_data.append(competency_framework_entry)

                    # Append each outcome as a separate competency entry
                    for outcome in outcomes:
                        competency_entry = {
                            "@id": 'ce-' + str(uuid.uuid4()),
                            "@type": "ceasn:Competency",
                            "ceasn:inLanguage": "en",
                            "ceasn:competencyLabel": "Learning Outcome",
                            "ceasn:competencyText": outcome,
                            "ceasn:isPartOf": framework_id
                        }
                        competency_data.append(competency_entry)
    df_competency = pd.DataFrame(competency_data)
    competency_csv = r"C:\text\NJ\Morris\credentials\programs\Review\Morris_BU_Credit_Credential_Competencies.csv"
    df_competency.to_csv(competency_csv, index=False, encoding="utf-8-sig")



# File paths
file1 = r"C:\text\NJ\Morris\credentials\programs\credentials_parsed.csv"

# Save the updated DataFrame back to CSV
output_file = r"C:\text\NJ\Morris\credentials\programs\parsed_credentials_updated.csv"

# Specify the directory containing your HTML files
directory_path = r"C:\text\NJ\Morris\credentials\programs\CredentialHTML"
parse_html(directory_path)

