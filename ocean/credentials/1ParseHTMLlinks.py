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
    # Locate each 'h2' with class 'letternav-head' and iterate over each sibling 'ul' to find 'a' tags
    for h2 in soup.find_all('h2', class_='letternav-head'):
        for ul in h2.find_next_siblings('ul', limit=1):  # Consider only the first ul following each h2
            for link in ul.find_all('a'):
                program_name = link.text.strip()
                program_url = link['href']
                data.append({'Program Name': program_name, 'Program Link': program_url})

    if not data:
        print("No program data found.")
        return

    # Convert the list to a DataFrame
    df = pd.DataFrame(data)

    # Save the DataFrame to a CSV file
    df.to_csv(output_csv_path, index=False)
    print(f"Data successfully parsed and saved to {output_csv_path}")

# Define the HTML file path and output CSV file path
html_file_path = r"C:\text\NJ\Ocean\credentials\Areas of Study _ Ocean County College Academic Catalog.html"
output_csv_path = r"C:\text\NJ\Ocean\credentials\credentials_parsed.csv"

# Call the function to parse HTML and save to CSV
parse_html_to_csv(html_file_path, output_csv_path)
