import os
import csv
import uuid
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
    "Version Identifier", "CIP List", "Is Non-Credit", "Keywords", "bundle", "price", "voucher", "access", "openenroll", "selfpaced"
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

                # Extract course information
                #course_name_tag = soup.find("h1", {"class": "ed-text-blue h_one"})
                #Reused this approach from another program. Funny that after pointing out the error the program was still wrong.
                course_name_tag = soup.find("h1", class_='ed-text-blue h_one ed-margin')
                #description_meta = soup.find("meta", {"name": "description"})
                description_Overview = soup.find("div", class_='wrapper_overview')
                keywords_meta = soup.find("meta", {"name": "keywords"})
                canonical_link = soup.find("link", {"rel": "canonical"})
                bundle = soup.find("div", {"id": "ctrlPrograms_divBundleInfo"})
                price = soup.find("div", {"id": "ctrlPrograms_divPriceDisplay"})
                hours = soup.find("div", {"id": "ctrlPrograms_divHours"})
                code = soup.find("div", {"id": "ctrlPrograms_divProgramCode"})
                voucher = soup.find("div", {"id": "ctrlPrograms_divVoucher"})
                access = soup.find("div", {"id": "ctrlPrograms_divAccess"})
                openenroll = soup.find("div", {"id": "ctrlPrograms_openEnrollment"})
                selfpaced = soup.find("div", {"id": "ctrlPrograms_selfPaced"})
                
                if course_name_tag and description_Overview and canonical_link:
                    course_name = course_name_tag.text.strip()
                    description = description_Overview.text.replace("Overview","").strip()
                    keywords = keywords_meta.get("content", "").strip().replace(",", "|") if keywords_meta else ""
                    subject_webpage = canonical_link.get("href", "").strip()

                    # Generate IDs
                    course_ctid = generate_ctid()
                    framework_ctid = generate_ctid()

                    # Write course row
                    course_row = {
                        "CTID": course_ctid,
                        "Internal Identifier": code.text.strip(),
                        "External Identifier": code.text.strip(),
                        "Learning Type": "Course",
                        "Learning Opportunity Name": course_name,
                        "Description": description,
                        "Subject Webpage": subject_webpage,
                        "Life Cycle Status Type": "Active",
                        "Language": "en",
                        "Credit Unit Type": "Unknown",
                        "Credit Unit Value": hours.text.strip(),
                        "Coded Notation": "Unknown",
                        "Teaches Competency Framework": framework_ctid,
                        "Date Effective": "Unknown",
                        "Version Identifier": "Unknown",
                        "CIP List": "Unknown",
                        "Is Non-Credit": "Yes",
                        "Keywords": keywords,
                        "bundle": bundle,
                        "price": price.text.strip(),
                        "voucher": voucher.text.strip(),
                        "access": access.text.strip(),
                        "openenroll": openenroll.text.strip(),
                        "selfpaced": selfpaced.text.strip()
                    }
                    courses_writer.writerow(course_row)

                    # Extract and write competencies
                    competencies_section = soup.find("div", {"id": "tab_objectives"})
                    if competencies_section:
                        # Locate the first <ul> within the competencies section
                        ul_tag = competencies_section.find("ul")
                        if ul_tag:
                            # Extract all <li> elements within this specific <ul>
                            competency_texts = ul_tag.find_all("li")
                        competencies_writer.writerow({
                            "@id": framework_ctid,
                            "@type": "ceasn:CompetencyFramework",
                            "ceasn:description": "Learning objectives from the course.",
                            "ceasn:inLanguage": "en",
                            "ceasn:name": f"{course_name}: Learning Objectives",
                            "ceasn:publicationStatusType": "Published",
                            "ceasn:source": subject_webpage
                        })

                        for idx, text in enumerate(competency_texts, start=1):
                            competencies_writer.writerow({
                                "@id": generate_ctid(),
                                "@type": "ceasn:Competency",
                                "ceasn:inLanguage": "en",
                                "ceasn:competencyCategory": "Learning Objective",
                                "ceasn:competencyText": text.text.strip(),
                                "ceasn:isTopChildOf": framework_ctid,
                                "ceasn:listID": idx
                            })

print("Processing complete. CSV files generated.")
