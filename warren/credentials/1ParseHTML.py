import pandas as pd
from bs4 import BeautifulSoup
import re

def remove_numbers_and_periods(text):
    return re.sub(r'[\d\.]+', '', text)

    
def map_type(type_):
    type_mapping = {
        "AA": "AssociateofArtsDegree",
        "AAS": "AssociateofAppliedScienceDegree",
        "AFA": "AssociateofArtsDegree",
        "AS": "AssociateofScienceDegree",
        "Certificate": "Certificate",
    }
    # Default to original type if not in dictionary
    return type_mapping.get(type_.strip(), type_)

# Function to parse HTML and extract program details
def parse_html(filename):
    # Open and read the HTML file
    with open(filename, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')
    
    # List to hold all credential details
    credential_details = []

    # Find all <ul> elements under each <h3> within the 'singlepost' div
    for h3_tag in soup.select('.singlepost h3'):
        # Ensure there is a following <ul> sibling
        ul_tag = h3_tag.find_next_sibling('ul')
        if ul_tag:
            # Loop through each <li> in the <ul>
            for li in ul_tag.find_all('li'):
                a_tag = li.find('a')
                if a_tag and 'href' in a_tag.attrs:
                    # Extract the credential name and link
                    credential_name = a_tag.text.strip()
                    credential_type = a_tag['href'].split('-')[0].replace("http://www.warren.edu/uploads/","").replace("https://www.warren.edu/uploads/","").strip()
                    type_ = map_type(credential_type)
                    credential_link = a_tag['href'].strip()
                    # Split the filename on dash to isolate components
                    parts = credential_link.split('-')
                    # The version is expected to be before the last period and after the last dash
                    version = parts[-1].split('.pdf')[0]
                    if credential_name == "Certificate":
                        part2 = credential_link.split("/")
                        credential_name = part2[-1].split('.pdf')[0]
                        credential_name = credential_name[:-4].replace("-"," ").strip()
                        credential_name = remove_numbers_and_periods(credential_name)
                    
                    # Append to list
                    credential_details.append({
                        'Credential Name': credential_name,
                        'Credential Type': credential_type,
                        'Type': type_,
                        'Credential Link': credential_link,
                        'Version': version
                    })
    
    # Convert list to DataFrame
    df = pd.DataFrame(credential_details)

    # Save to CSV
    output_csv_path = 'credentials.csv'
    df.to_csv(output_csv_path, index=False)
    print(f'Data saved to {output_csv_path}')

# Replace 'your_html_file_path.html' with your actual file path
file_path = "C:\\text\\NJ\\Warren\\credentials\\Programs Of Study _ Warren County Community College.html"
parse_html(file_path)
