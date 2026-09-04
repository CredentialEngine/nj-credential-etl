from bs4 import BeautifulSoup
import pandas as pd
import os

# Define the path to the HTML file
file_path = r"C:\text\NJ\Atlantic Cape\credentials\Degrees and Certificates _ Atlantic Cape Community College.html"
#Define type mappings to CTDL
type_mapping= {
    'Associate in Applied Science': 'AssociateOfAppliedScienceDegree',
    'Associate in Arts': 'AssociateOfArtsDegree',
    'Associate in Fine Arts': 'AssociateOfArtsDegree',
    'Associate in Science': 'AssociateOfScienceDegree',
    'Certificate': 'Certificate',
    'Professional Series': 'Certificate',
    'Program': 'Certificate',
}

# Read the HTML file
if os.path.exists(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    data = []

    # Extract credentials information
    credentials = soup.find_all("div", class_="views-row")
    for credential in credentials:
        title_element = credential.find("h2", class_="course-teaser-table-title")
        title = title_element.get_text(strip=True) if title_element else "No Title Found"

        program_element = credential.find("div", class_="course-teaser-table-program")
        program = program_element.a.get_text(strip=True) if program_element and program_element.a else "No Program Found"
        program_url = program_element.a['href'] if program_element and program_element.a else "No URL Found"

        type_element = credential.find("div", class_="course-teaser-table-type")
        type_ = type_element.div.get_text(strip=True) if type_element and type_element.div else "No Type Found"
        type_url = type_element.a['href'] if type_element and type_element.a else "No URL Found"
        
        CE_type = type_mapping.get(type_, 'Unknown')

        data.append({
            "Title": title,
            "Program": program,
            "Program URL": program_url,
            "Type": type_,
            "Type URL": type_url,
            "CE Type": CE_type,
        })

    # Convert data to a DataFrame and save to CSV
    df = pd.DataFrame(data)
    output_csv_path = r"C:\text\NJ\Atlantic Cape\credentials\credentials_output.csv"
    df.to_csv(output_csv_path, index=False)

    print(f"Data successfully extracted and saved to {output_csv_path}")
else:
    print("File does not exist. Please check the path and try again.")
