import os
import csv
from bs4 import BeautifulSoup
import re

def map_type(type_):
    type_mapping = {
        "aa": "AssociateOfArtsDegree",
        "aas": "AssociateOfAppliedScienceDegree",
        "afa": "AssociateOfArtsDegree",
        "as": "AssociateOfScienceDegree",
        "as/index": "AssociateOfScienceDegree",
        "ba": "AssociateOfScienceDegree",
        "billing": "Certificate",
        "bs": "AssociateOfScienceDegree",
        "cert": "Certificate",
        "certificate": "Certificate",
        "computer": "AssociateOfArtsDegree",
        "fully": "Certificate",
        "health": "AssociateOfScienceDegree",
        "homeland": "AssociateOfScienceDegree",
        "innovation": "Certificate",
        "justice": "AssociateOfScienceDegree",
        "option": "AssociateOfScienceDegree",
        "options": "AssociateOfAppliedScienceDegree",
        "pastry": "Certificate",
        "professional": "AssociateOfScienceDegree",
        "proficiency": "Certificate",
        "science/ese": "AssociateOfArtsDegree",
        "science/history": "AssociateOfArtsDegree",
    }
    # Default to original type if not in dictionary
    return type_mapping.get(type_.strip(), type_)

def extract_credential_data(file_path):
    """Extract credential information from an HTML file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Extract data
    credential_title = soup.find('h1').text.strip() if soup.find('h1') else ''
    description_section = soup.find('section', class_='catalog__content')
    description = ''
    major = ''
    degree = ''
    url = ''
    type_ = ''
    online = ''

    if description_section:
        description_tag = description_section.find('p')
        description = description_tag.text.strip() if description_tag else ''
        #Remove newline and carriage return characters
        description = description.replace("\n", " ").replace("\r", " ")
        #Remove double space issues
        description = re.sub(r'\s+', ' ', description).strip()
        if description == '':
            # Find the meta tag with name "Description"
            meta_description = soup.find('meta', attrs={'name': 'Description'})
            if meta_description:
                # Extract the content attribute which contains the description
                description = meta_description.get('content')

        details = description_section.find_all('dd', class_='program-detail')
        if details:
            major = details[0].text.strip() if len(details) > 0 else ''
            degree = details[1].text.strip() if len(details) > 1 else ''
    
    meta_tag = soup.find('meta', property="og:url")
    if meta_tag:
        # Extract the URL from the content attribute
        url = meta_tag.get('content')
    
    #Get type information Split from the right at the last dash
    last_part = url.rsplit('-', 1)[-1]
    # Remove the '.html' suffix
    type_ = last_part.replace('.html', '')
    if type_ == "online":
        online = "OnlineOnly"
        parts = url.rsplit('-', 2)
        type_ = parts[1]
    type_ = map_type(type_.strip())   
    
    #Switching to Meta description2
    description2 = ''
    meta_description2 = soup.find('meta', attrs={'name': 'Description'})
    if meta_description2:
        # Extract the content attribute which contains the description
        description2 = meta_description2.get('content')

    return {
        'Filename': os.path.basename(file_path),
        'Credential Name': credential_title,
        'Description': description2,
        'Major': major,
        'Degree': degree,
        'URL': url,
        'Type': type_,
        'Online': online,
    }

def process_html_directory(input_directory, output_csv):
    """Process all HTML files in a directory and save extracted data to a CSV file."""
    data = []

    # Iterate through all files in the directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.html'):
            file_path = os.path.join(input_directory, filename)
            try:
                record = extract_credential_data(file_path)
                data.append(record)
                print(f"Processed: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    # Write data to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['Filename', 'Credential Name', 'Description', 'Description2', 'Major', 'Degree', 'URL', 'Type', 'Online']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(data)

    print(f"Data saved to {output_csv}")

if __name__ == "__main__":
    input_dir = r"C:\text\NJ\Hudson County\Credentials\CredentialsHTML"
    output_file = r"C:\text\NJ\Hudson County\Credentials\parsed_credentials.csv"
    process_html_directory(input_dir, output_file)
