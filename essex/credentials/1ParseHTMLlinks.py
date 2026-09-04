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

    # Locate the specific div with class 'az_sitemap'
    sitemap_div = soup.find('div', class_='az_sitemap')
    if not sitemap_div:
        print("Sitemap section not found in the HTML.")
        return

    data = []
    # Iterate over each anchor tag directly within any <ul> inside 'az_sitemap'
    program_links = sitemap_div.find_all('a')
    
    for link in program_links:
        if link and 'href' in link.attrs:
            program_name = link.text.strip()
            # Skip the row if the Program Name is just one letter
            if len(program_name) == 1:
                continue
            program_url = link['href']
            data.append({'Program Name': program_name, 'Program Link': program_url})
        else:
            print("No href found in one of the links or link is invalid.")

    if not data:
        print("No program data found.")
        return

    # Convert the list to a DataFrame
    df = pd.DataFrame(data)

    # Save the DataFrame to a CSV file
    df.to_csv(output_csv_path, index=False)
    print(f"Data successfully parsed and saved to {output_csv_path}")

# Define the HTML file path and output CSV file path
html_file_path = r"C:\text\NJ\Essex\credentials\Programs A-Z Index _ Essex County College.html"
output_csv_path = r"C:\text\NJ\Essex\credentials\credentials_parsed.csv"

# Call the function to parse HTML and save to CSV
parse_html_to_csv(html_file_path, output_csv_path)
