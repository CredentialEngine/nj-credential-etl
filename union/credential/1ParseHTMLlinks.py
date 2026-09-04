from bs4 import BeautifulSoup
import pandas as pd
import os

def parse_html_to_csv(html_file_path, output_csv_path):
    # Check if the HTML file exists
    if not os.path.exists(html_file_path):
        print("HTML file does not exist. Please check the path and try again.")
        return

    # Read the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Locate the section after <h4>Alphabetical Program List</h4>
    h4_tag = soup.find('h4', string="Alphabetical Program List")
    if not h4_tag:
        print("Section 'Alphabetical Program List' not found in the HTML.")
        return
    
    # Find all <p> tags directly following the <h4> tag
    data = []
    next_element = h4_tag.find_next_sibling()
    
    while next_element and next_element.name == 'p':
        link_tag = next_element.find('a')
        if link_tag:
            name = link_tag.get_text(strip=True)
            link = link_tag['href']
            data.append({'Credential Name': name, 'Link': link})
        next_element = next_element.find_next_sibling()

    if not data:
        print("No program links found following the specified heading.")
        return

    # Convert the list to a DataFrame
    df = pd.DataFrame(data)

    # Save the DataFrame to a CSV file
    df.to_csv(output_csv_path, index=False)
    print(f"Data successfully parsed and saved to {output_csv_path}")

# Define the HTML file path and output CSV file path
html_file_path = r"C:\text\NJ\Union\credential\Programs of Study - UCNJ Union College of Union County, NJ - Modern Campus Catalog™.html"
output_csv_path = r"C:\text\NJ\Union\credential\credentials_parsed.csv"

# Call the function to parse HTML and save to CSV
parse_html_to_csv(html_file_path, output_csv_path)
