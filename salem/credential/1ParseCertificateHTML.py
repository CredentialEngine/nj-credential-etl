import os
import pandas as pd
from bs4 import BeautifulSoup
import csv

# Load the HTML content from the file
with open("Certificate Programs _ Salem Community College.html", "r") as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Find the table containing the program details
table = soup.find_all('tr')[3:]  # Skipping header rows

# List to hold each row of data
data = []

# Parse each row in the table
for row in table:
    columns = row.find_all('td')
    if len(columns) >= 3:
        program_name = columns[0].find('a').text if columns[0].find('a') else ""
        program_url = columns[0].find('a')['href'] if columns[0].find('a') else ""
        degree_type = columns[1].text.strip()
        career_options_url = columns[2].find('a')['href'] if columns[2].find('a') else ""
        
        # Append the extracted data to the list
        data.append([program_name, program_url, degree_type, career_options_url])

# Create a DataFrame
df = pd.DataFrame(data, columns=['Program Name', 'Program URL', 'Degree Type', 'Career Options URL'])

# Save to CSV
csv_file_path = "Salem_Community_College_Cert.csv"
df.to_csv(csv_file_path, index=False)

csv_file_path
