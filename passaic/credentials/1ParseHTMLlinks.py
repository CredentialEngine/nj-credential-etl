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

    data = []
    # Locate the div with id 'programList' and find all 'a' tags within it
    program_list = soup.find('div', id='programList')
    if program_list:
        links = program_list.find_all('a')
        current_credential_type = None
        for link in links:
            if link['href'] == "https://catalog.pccc.edu/programs/#":
                # This link denotes a new credential type
                current_credential_type = link.text.strip()
            elif link['href'] != "https://catalog.pccc.edu/programs/#":
                # This is a valid program link, capture it
                program_name = link.text.strip()
                program_url = link['href']
                if current_credential_type:
                    data.append({
                        'Program Name': program_name,
                        'Credential Type': current_credential_type,
                        'Program Link': program_url
                    })
    else:
        print("No program list found.")

    if not data:
        print("No program data found.")
        return

    # Convert the list to a DataFrame
    df = pd.DataFrame(data)

    # Save the DataFrame to a CSV file
    df.to_csv(output_csv_path, index=False)
    print(f"Data successfully parsed and saved to {output_csv_path}")

# Define the HTML file path and output CSV file path
html_file_path = r"C:\text\NJ\Passaic\credentials\Passaic County Community College.html"
output_csv_path = r"C:\text\NJ\Passaic\credentials\credentials_parsed.csv"

# Call the function to parse HTML and save to CSV
parse_html_to_csv(html_file_path, output_csv_path)
