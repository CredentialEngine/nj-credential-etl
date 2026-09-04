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

    # Locate the section by <h3>
    h3_tag = soup.find('h3', string="BUSINESS AND PUBLIC SERVICE")
    if not h3_tag:
        print("Section 'BUSINESS AND PUBLIC SERVICE' not found in the HTML.")
        return

    # Find all <dl> tags within the content
    dls = h3_tag.find_next_siblings('dl', class_='program-link')
    if not dls:
        print("No program links found in the specified section.")
        return

    data = []
    # Iterate over each <dl> to extract <dt> and its <dd> elements
    for dl in dls:
        dt = dl.find('dt')
        if not dt:
            print("No <dt> tag found in one of the <dl> elements.")
            continue  # Skip this <dl> if no <dt> found
        dt_text = dt.get_text(strip=True)  # Program group title

        dds = dl.find_all('dd')  # All program links under this title
        for dd in dds:
            link_tag = dd.find('a')
            if link_tag:
                name = link_tag.get_text(strip=True)
                link = link_tag['href']
                data.append({'Category': dt_text, 'Credential Name': name, 'Link': link})

    if not data:
        print("No credentials were extracted.")
        return  # Exit if no data to process

    # Convert the list to a DataFrame
    df = pd.DataFrame(data)

    # Save the DataFrame to a CSV file
    df.to_csv(output_csv_path, index=False)
    print(f"Data successfully parsed and saved to {output_csv_path}")

# Define the HTML file path and output CSV file path
html_file_path = r"C:\text\NJ\Camden\credentials\Academic Programs - Camden County College.html"
output_csv_path = r"C:\text\NJ\Camden\credentials\credentials_parsed.csv"

# Call the function to parse HTML and save to CSV
parse_html_to_csv(html_file_path, output_csv_path)
