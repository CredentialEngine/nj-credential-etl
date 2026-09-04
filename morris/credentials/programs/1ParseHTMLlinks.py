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

    # Locate all 'single-program' divs
    program_divs = soup.find_all('div', class_='single-program')
    if not program_divs:
        print("No programs found in the HTML.")
        return

    data = []
    
    # Iterate over each program div
    for program_div in program_divs:
        name_link = program_div.find('a', class_='name')
        tag_link = program_div.find('a', class_='tag')
        
        if name_link and 'href' in name_link.attrs:
            program_name = name_link.text.strip()
            program_url = name_link['href']
        else:
            continue  # Skip if program name or URL is missing

        credential_type = tag_link.text.strip() if tag_link else "Unknown"
        
        data.append({'Program Name': program_name, 'Program Link': program_url, 'Credential Type': credential_type})

    if not data:
        print("No valid program data found.")
        return

    # Convert the list to a DataFrame
    df = pd.DataFrame(data)

    # Save the DataFrame to a CSV file
    df.to_csv(output_csv_path, index=False)
    print(f"Data successfully parsed and saved to {output_csv_path}")

# Define the HTML file path and output CSV file path
html_file_path = r"C:\text\NJ\Morris\credentials\programs\Programs _ County College of Morris (CCM).html"
output_csv_path = r"C:\text\NJ\Morris\credentials\programs\credentials_parsed.csv"

# Call the function to parse HTML and save to CSV
parse_html_to_csv(html_file_path, output_csv_path)
