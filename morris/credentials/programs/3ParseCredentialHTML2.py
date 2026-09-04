from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import uuid

# 📌 Utility function to map credential types
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

# 📌 Function to extract credential title, type, and internal code
def extract_title_and_type(soup, filename):
    h1 = soup.find('h1')
    title_text = h1.get_text(strip=True) if h1 else soup.find('title').get_text(strip=True) if soup.find('title') else "No Title"
    
    # Clean institution-specific text
    title_text = title_text.replace(" Degrees | Programs Near Me | County College of Morris (CCM)", "").strip()

    # Extract type from parentheses or filename
    paren_match = re.search(r'\((.*?)\)', title_text)
    internal_code = re.search(r'\(([^)]*)\)', filename)
    internal_code = internal_code.group(1) if internal_code else None
    credential_type = map_type(paren_match.group(1).strip()) if paren_match else map_type(os.path.splitext(filename)[0].split("(")[0].strip())

    return title_text, credential_type, internal_code

# 📌 Function to extract outcomes from HTML
def extract_outcomes(soup):
    outcomes = []

    # Match learning outcome headings
    keywords = ["students learn to", "students learn how to", "graduates will be able to", "learn how to:"]
    outcome_intro = soup.find(lambda tag: tag.name == "p" and any(keyword in tag.get_text(strip=True).lower() for keyword in keywords))
    studentoutcomes_section = soup.find(lambda tag: tag.name in ["h2", "h3"] and "outcomes" in tag.get_text(strip=True).lower())

    for section in [outcome_intro, studentoutcomes_section]:
        if section:
            ul_tag = section.find_next_sibling("ul")
            if ul_tag:
                for li in ul_tag.find_all("li"):
                    text = re.sub(r'^\d+\.\s*', '', li.get_text(strip=True))  # Remove numbering
                    text = text.rstrip(";").rstrip("; and")  # Remove trailing semicolons
                    if text and not text.endswith('.'):
                        text += '.'
                    outcomes.append(text.capitalize())

    return outcomes

# 📌 Function to parse HTML directory
def parse_html(directory):
    data = []

    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                name, credential_type, internal_code = extract_title_and_type(soup, filename)
                outcomes = extract_outcomes(soup)
                framework_id = f'ce-{uuid.uuid4()}' if outcomes else ""

                # Extract URL and meta description
                canonical_url = soup.find("link", rel="canonical")["href"] if soup.find("link", rel="canonical") else "No URL"
                meta_description = soup.find("meta", attrs={"name": "description"})["content"] if soup.find("meta", attrs={"name": "description"}) else "No description"

                # Store extracted data
                data.append({
                    'Filename': filename,
                    'Credential Name': name,
                    'Credential Type': credential_type,
                    'Outcomes': framework_id,
                    "URL": canonical_url,
                    "Description": meta_description.strip()
                })

    return pd.DataFrame(data)

# 📌 Function to merge additional CSV data
def merge_csv_data(df, file1, output_file):
    df1 = pd.read_csv(file1)
    merged_df = df.merge(df1[['Program Link', 'Credential Type']], left_on='URL', right_on='Program Link', how='left').drop(columns=['Program Link'])
    
    merged_df['Credential Type_y'].fillna("Unknown", inplace=True)
    merged_df['Type'] = merged_df['Credential Type_y'].apply(map_type)
    merged_df['Name'] = merged_df['Credential Name'] + ": " + merged_df['Credential Type_y'].str.replace(r"[()]", "", regex=True)
    merged_df['Name'] = merged_df['Name'].str.replace("Certificates", "Certificate")

    merged_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"Updated CSV saved to: {output_file}")

# 📌 Main execution
directory_path = r"C:\text\NJ\Morris\credentials\programs\CredentialHTML"
file1 = r"C:\text\NJ\Morris\credentials\programs\credentials_parsed.csv"
output_file = r"C:\text\NJ\Morris\credentials\programs\parsed_credentials_updated.csv"

df = parse_html(directory_path)
merge_csv_data(df, file1, output_file)
