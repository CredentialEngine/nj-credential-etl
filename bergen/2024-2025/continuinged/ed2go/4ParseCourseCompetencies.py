import uuid
import os
import csv
from bs4 import BeautifulSoup

# Directory containing HTML files
html_dir = r"C:\text\NJ\Bergen\ContinuingEd\ed2go\coursesHTML"

# Output CSV file paths
courses_csv_path = r"C:\text\NJ\Bergen\ContinuingEd\ed2go\courses.csv"
competencies_csv_path = r"C:\text\NJ\Bergen\ContinuingEd\ed2go\competencies.csv"

# Generate a unique CTID
def generate_ctid():
    return f"ce-{uuid.uuid4()}"

# Create CSV files with headers
courses_headers = [
    "CTID", "Internal Identifier", "External Identifier", "Learning Type",
    "Learning Opportunity Name", "Description", "Subject Webpage", 
    "Life Cycle Status Type", "Language", "Credit Unit Type", "Credit Unit Value", 
    "Coded Notation", "Teaches Competency Framework", "Date Effective", 
    "Version Identifier", "CIP List", "Is Non-Credit"
]

competencies_headers = [
    "@id", "@type", "ceasn:description", "ceasn:inLanguage", 
    "ceasn:name", "ceasn:publicationStatusType", "ceasn:source", 
    "ceasn:codedNotation", "ceasn:competencyCategory", 
    "ceasn:competencyText", "ceasn:isTopChildOf", "ceasn:listID"
]

with open(courses_csv_path, 'w', newline='', encoding='utf-8') as courses_file, \
     open(competencies_csv_path, 'w', newline='', encoding='utf-8') as competencies_file:
    
    courses_writer = csv.DictWriter(courses_file, fieldnames=courses_headers)
    competencies_writer = csv.DictWriter(competencies_file, fieldnames=competencies_headers)
    
    courses_writer.writeheader()
    competencies_writer.writeheader()

    # Process each HTML file
    for html_file in os.listdir(html_dir):
        file_path = os.path.join(html_dir, html_file)

        if os.path.isfile(file_path) and html_file.endswith(".html"):
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

                try:
                    # Extract course information
                    course_name = soup.find("h1", {"class": "ed-text-blue h_one"})
                    description = soup.find("meta", {"name": "description"})
                    url = soup.find("link", {"rel": "canonical"})

                    # Check if necessary elements exist
                    if not course_name or not description or not url:
                        print(f"Skipping {html_file}: Missing critical data.")
                        continue

                    # Generate Course CTID and Framework CTID
                    course_ctid = generate_ctid()
                    framework_ctid = generate_ctid()

                    # Write course information
                    course_row = {
                        "CTID": course_ctid,
                        "Internal Identifier": "Unknown",
                        "External Identifier": "Unknown",
                        "Learning Type": "Course",
                        "Learning Opportunity Name": course_name.get_text(strip=True),
                        "Description": description.get("content", "").strip(),
                        "Subject Webpage": url.get("href", "").strip(),
                        "Life Cycle Status Type": "Active",
                        "Language": "en",
                        "Credit Unit Type": "Unknown",
                        "Credit Unit Value": "Unknown",
                        "Coded Notation": "Unknown",
                        "Teaches Competency Framework": framework_ctid,
                        "Date Effective": "Unknown",
                        "Version Identifier": "Unknown",
                        "CIP List": "Unknown",
                        "Is Non-Credit": "Yes"
                    }
                    courses_writer.writerow(course_row)

                    # Extract competency information
                    competencies = soup.find_all("div", class_="competency-section")
                    if competencies:
                        # Write competency framework
                        competencies_writer.writerow({
                            "@id": framework_ctid,
                            "@type": "ceasn:CompetencyFramework",
                            "ceasn:description": "Student learning outcomes and course objectives.",
                            "ceasn:inLanguage": "en",
                            "ceasn:name": f"{course_name.get_text(strip=True)} - Competency Framework",
                            "ceasn:publicationStatusType": "http://credreg.net/ctdlasn/vocabs/publicationStatus/Published",
                            "ceasn:source": url.get("href", "").strip(),
                            "ceasn:codedNotation": "",
                            "ceasn:competencyCategory": "",
                            "ceasn:competencyText": "",
                            "ceasn:isTopChildOf": "",
                            "ceasn:listID": ""
                        })

                        # Write individual competencies
                        for idx, competency in enumerate(competencies, start=1):
                            competencies_writer.writerow({
                                "@id": generate_ctid(),
                                "@type": "ceasn:Competency",
                                "ceasn:description": competency.get_text(strip=True),
                                "ceasn:inLanguage": "en",
                                "ceasn:name": f"Competency {idx}",
                                "ceasn:publicationStatusType": "Published",
                                "ceasn:source": url.get("href", "").strip(),
                                "ceasn:codedNotation": f"Comp-{idx}",
                                "ceasn:competencyCategory": "Student Learning Outcome",
                                "ceasn:competencyText": competency.get_text(strip=True),
                                "ceasn:isTopChildOf": framework_ctid,
                                "ceasn:listID": idx
                            })

                except Exception as e:
                    print(f"Error processing {html_file}: {e}")

print("Processing complete. CSV files generated.")
