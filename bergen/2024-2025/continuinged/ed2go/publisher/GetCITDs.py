import os
import csv
from bs4 import BeautifulSoup

# Define the input directory containing HTML files and the output CSV file
input_dir = r"C:\text\NJ\Bergen\ContinuingEd\ed2go\Publisher"  # Replace with your directory path
output_csv = "ctid_values.csv"

# Open the CSV file for writing
with open(output_csv, mode='w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    # Write the header row
    writer.writerow(["Filename", "CTID"])

    # Process each HTML file in the directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".html"):
            file_path = os.path.join(input_dir, filename)
            
            # Open and parse the HTML file
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                
                # Find all div tags with class "ctid"
                ctid_tags = soup.find_all("div", class_="ctid")
                
                # Extract and write each CTID value to the CSV
                for ctid_tag in ctid_tags:
                    ctid_value = ctid_tag.get_text(strip=True)
                    writer.writerow([filename, ctid_value])
                    print(f"Found CTID: {ctid_value} in file: {filename}")

print(f"All CTID values have been saved to {output_csv}")
