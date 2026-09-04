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

    # Find all 'li' elements within 'ul' with class 'program-list'
    program_list_items = soup.find_all('ul', class_='program-list')
    
    # Prepare a list to store parsed data
    data = []
    
    # Loop through each 'ul'
    for ul in program_list_items:
        list_items = ul.find_all('li')
        for li in list_items:
            link_tag = li.find('a')
            if link_tag:
                name = link_tag.get_text(strip=True)
                link = link_tag['href']
                data.append({'Credential Name': name, 'Link': link})
    
    # Convert the list to a DataFrame
    df = pd.DataFrame(data)

    # Save the DataFrame to a CSV file
    df.to_csv(output_csv_path, index=False)
    print(f"Data successfully parsed and saved to {output_csv_path}")

# Define the HTML file path and output CSV file path
html_file_path = r"C:\text\NJ\Sussex\credential\Programs Offered (A to Z) - Sussex County Community College - Modern Campus Catalog™.html"
output_csv_path = r"C:\text\NJ\Sussex\credential\credentials_parsed.csv"

# Call the function to parse HTML and save to CSV
parse_html_to_csv(html_file_path, output_csv_path)
