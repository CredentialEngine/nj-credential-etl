import os
import csv
import uuid
from bs4 import BeautifulSoup

# Directory containing HTML files
html_dir = r"C:\text\NJ\Rowan College at Burlington\noncredit\ed2go\coursesHTML"

# Output CSV file paths
courses_csv_path = r"C:\text\NJ\Rowan College at Burlington\noncredit\ed2go\rcbcenrich_ed2go_course_BU.csv"
competencies_csv_path = r"C:\text\NJ\Rowan College at Burlington\noncredit\ed2go\rcbcenrich_ed2go_competency_BU.csv"

# Generate a unique CTID
def generate_ctid():
    return f"ce-{uuid.uuid4()}"

# Create CSV files with headers
courses_headers = [
    "CTID", "Internal Identifier", "External Identifier", "Learning Type",
    "Available Online At", "Delivery Type", "Delivery Type Description", "Learning Opportunity Name", "Description", "Subject Webpage",
    "Life Cycle Status Type", "Language", "Credit Unit Type", "Credit Unit Value",
    "Coded Notation", "Teaches Competency Framework", "Is Non-Credit", "Keywords", "bundle","Cost: External Identifier", "Cost: Currency Type", "Cost: Types List",
    "Financial Assistance: External Identifier", "Financial Assistance: Name", "Financial Assistance: Description", "Financial Assistance: Subject Webpage",
    "Financial Assistance: Type", "Estimated Duration", "Learning Method Type"
    
]

competencies_headers = [
    "@id", "@type", "ceasn:description", "ceasn:inLanguage",
    "ceasn:name", "ceasn:publicationStatusType", "ceasn:source",
    "ceasn:codedNotation", "ceasn:competencyCategory",
    "ceasn:competencyText", "ceasn:isTopChildOf", "ceasn:listID"
]

with open(courses_csv_path, 'w', newline='', encoding='utf-8-sig') as courses_file, \
     open(competencies_csv_path, 'w', newline='', encoding='utf-8-sig') as competencies_file:

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

                # Extract course information with defaults for missing values
                course_name_tag = soup.find("h1", class_='ed-text-blue h_one ed-margin')
                course_name = course_name_tag.text.strip() if course_name_tag else "Unknown Course Name"

                description_Overview = soup.find("div", class_='wrapper_overview')
                description = description_Overview.text.replace("Overview", "").strip() if description_Overview else "No description available"

                keywords_meta = soup.find("meta", {"name": "keywords"})
                keywords = keywords_meta.get("content", "").strip().replace(", ", "|") if keywords_meta else ""

                canonical_link = soup.find("link", {"rel": "canonical"})
                subject_webpage = canonical_link.get("href", "").strip() if canonical_link else "Unknown URL"

                bundle = soup.find("div", {"id": "ctrlPrograms_divBundleInfo"})
                price = soup.find("div", {"id": "ctrlPrograms_divPriceDisplay"})
                hours = soup.find("div", {"id": "ctrlPrograms_divHours"})
                code = soup.find("div", {"id": "ctrlPrograms_divProgramCode"})
                voucher = soup.find("div", {"id": "ctrlPrograms_divVoucher"})
                access = soup.find("div", {"id": "ctrlPrograms_divAccess"})
                openenroll = soup.find("div", {"id": "ctrlPrograms_openEnrollment"})
                selfpaced = soup.find("div", {"id": "ctrlPrograms_selfPaced"})
                requirements = soup.find("div", class_='wrapper_requirements')
                
                # Generate IDs
                course_ctid = generate_ctid()
                framework_ctid = generate_ctid()

                # Safely handle missing values
                course_row = {
                    "CTID": course_ctid,
                    "Internal Identifier": code.text.replace("Code","").strip() if code else "",
                    "External Identifier": code.text.replace("Code","").strip() if code else "",
                    "Learning Type": "Course",
                    "Learning Opportunity Name": course_name,
                    "Description": description,
                    "Subject Webpage": subject_webpage,
                    "Available Online At": subject_webpage,
                    "Delivery Type": "OnlineOnly",
                    "Delivery Type Description": requirements.text.replace("Requirements\n\nRequirements:","").replace(":\n",":").strip() if requirements else "",
                    "Life Cycle Status Type": "Active",
                    "Language": "en",
                    "Credit Unit Type": "ContactHour",
                    "Credit Unit Value": hours.text.replace("schedule","").replace("Course Hrs","").strip() if hours else "",
                    "Coded Notation": code.text.replace("Code","").strip() if code else "",
                    "Teaches Competency Framework": framework_ctid,
                    #"Date Effective": "Unknown",
                    #"Version Identifier": "Unknown",
                    #"CIP List": "Unknown",
                    "Is Non-Credit": "Yes",
                    "Keywords": keywords,
                    #"bundle": bundle.text.replace("info","").strip() if bundle else "",
                    #Remove cost rows if blank.
                    "Cost: External Identifier": generate_ctid(),
                    "Cost: Currency Type": "USD",
                    "Cost: Types List": "tuition~" + price.text.replace('$','').replace(',','').replace('(USD)','').strip() if price else "",
                    #"price": price.text.replace('(USD)','').strip() if price else "",
                    #IDK what this voucher means, so I'm leaving it out.
                    "Financial Assistance: External Identifier": generate_ctid(),
                    "Financial Assistance: Name": course_name + " Financial Assistance",
                    "Financial Assistance: Description": voucher.text.strip() + ". The voucher is prepaid access to sit for the certifying exam upon eligibility." if voucher else "",
                    "Financial Assistance: Subject Webpage": "https://careertraining.ed2go.com/rcbcenrich/financial-assistance/",
                    "Financial Assistance: Type": "Institutional Grant",
                    #"voucher": voucher.text.strip() if voucher else "",
                    "Estimated Duration": access.text.replace('calendar_today','').strip() if access else "",
                    #"openenroll": openenroll.text.replace('grid_on','').strip() if openenroll else "Unknown",
                    "Learning Method Type": selfpaced.text.replace('speed','').strip() if selfpaced else ""
                }
                courses_writer.writerow(course_row)

                # Extract and write competencies
                competencies_section = soup.find("div", {"id": "tab_objectives"})
                if competencies_section:
                    ul_tag = competencies_section.find("ul")
                    competency_texts = ul_tag.find_all("li") if ul_tag else []
                    competencies_writer.writerow({
                        "@id": framework_ctid,
                        "@type": "ceasn:CompetencyFramework",
                        "ceasn:description": "What you will learn from the course.",
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
