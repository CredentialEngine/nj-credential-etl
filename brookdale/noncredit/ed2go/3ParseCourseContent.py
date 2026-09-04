import os
import csv
import uuid
from bs4 import BeautifulSoup

# Directory containing HTML files
html_dir = r"C:\text\NJ\Brookdale\noncredit\ed2go\coursesHTMLCourse"

# Output CSV file path
courses_csv_path = r"C:\text\NJ\Brookdale\noncredit\ed2go\Brookdale_BU_Noncredit_ed2go_Courses.csv"

# Generate a unique CTID
def generate_ctid():
    return f"ce-{uuid.uuid4()}"

# Mapping function for learning methods
def map_learning_methods(methods):
    mapping = {
        "Self-Guided": "SelfPaced",
        "Instructor-Moderated": "Cohort-Based"
    }
    return "|".join([mapping[method] for method in methods if method in mapping])

# Extract the code from label tags containing 'rb|Self-Guided|'
def extract_self_guided_code(soup):
    label_tag = soup.find("label", attrs={"for": lambda x: x and x.startswith("rb|Self-Guided|")})
    label_tag2 = soup.find("label", attrs={"for": lambda x: x and x.startswith("rb|Instructor-Moderated|")})
    if label_tag:
        return label_tag["for"].split("|")[-1]  # Extract the last part of the 'for' attribute
    if label_tag2:
        return label_tag2["for"].split("|")[-1]  # Extract the last part of the 'for' attribute
    return ""

# Create CSV file with headers
courses_headers = [
    "CTID", "Internal Identifier", "External Identifier", "Learning Type",
    "Available Online At", "Delivery Type", "Learning Opportunity Name", "Description", "Subject Webpage",
    "Life Cycle Status Type", "Language", "Credit Unit Type", "Credit Unit Value",
    "Coded Notation", "Is Non-Credit", "Cost: External Identifier", "Cost: Currency Type", "Cost: Types List",
    "Financial Assistance: External Identifier", "Financial Assistance: Name", "Financial Assistance: Description", "Financial Assistance: Subject Webpage",
    "Financial Assistance: Type", "Estimated Duration", "Learning Method Type"
]

with open(courses_csv_path, 'w', newline='', encoding='utf-8-sig') as courses_file:
    courses_writer = csv.DictWriter(courses_file, fieldnames=courses_headers)
    courses_writer.writeheader()

    # Process each HTML file
    for html_file in os.listdir(html_dir):
        file_path = os.path.join(html_dir, html_file)

        if os.path.isfile(file_path) and html_file.endswith(".html"):
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                soup = BeautifulSoup(file, 'html.parser')

                # Extract course information
                course_name_tag = soup.find("h1", class_='cd-det-title')
                course_name = course_name_tag.text.strip() if course_name_tag else "Unknown Course Name"

                description_tag = soup.find("div", class_='collapsible')
                description = description_tag.text.strip() if description_tag else "No description available"

                keywords_meta = soup.find("meta", {"name": "keywords"})
                keywords = keywords_meta.get("content", "").strip().replace(", ", "|") if keywords_meta else ""

                canonical_link = soup.find("link", {"rel": "canonical"})
                subject_webpage = canonical_link.get("href", "").strip() if canonical_link else "Unknown URL"

                price_tag = soup.find("div", class_='e2g-hosted-details-enrollments-price')
                price = price_tag.text.replace('$', '').strip() if price_tag else "Unknown Price"

                duration_tag = soup.find("span", class_='responsive-product-banner-course-hours')
                estimated_duration = duration_tag.text.strip() if duration_tag else "Unknown Duration"

                learning_method_tags = soup.find_all("div", class_='e2g-hosted-details-enrollments-item-content-type')
                #learning_methods = "|".join([tag.text.strip() for tag in learning_method_tags]) if learning_method_tags else "Unknown Method"
                learning_methods_raw = [tag.text.strip() for tag in learning_method_tags]
                learning_methods = map_learning_methods(learning_methods_raw)
                
                # Extract Self-Guided Code
                code = extract_self_guided_code(soup)

                # Generate IDs
                course_ctid = generate_ctid()

                # Create course row
                course_row = {
                    "CTID": course_ctid,
                    "Internal Identifier": "",
                    "External Identifier": "",
                    "Learning Type": "Course",
                    "Learning Opportunity Name": course_name,
                    "Description": description,
                    "Subject Webpage": subject_webpage,
                    "Available Online At": subject_webpage,
                    "Delivery Type": "OnlineOnly",
                    #"Delivery Type Description": "",
                    "Life Cycle Status Type": "Active",
                    "Language": "en",
                    "Credit Unit Type": "ContactHour",
                    "Credit Unit Value": estimated_duration,
                    "Coded Notation": code,
                    "Is Non-Credit": "Yes",
                    #"Keywords": keywords,
                    "Cost: External Identifier": generate_ctid(),
                    "Cost: Currency Type": "USD",
                    "Cost: Types List": f"tuition~{price}",
                    "Financial Assistance: External Identifier": generate_ctid(),
                    "Financial Assistance: Name": f"{course_name} Financial Assistance",
                    "Financial Assistance: Description": "Financial assistance may be available.",
                    "Financial Assistance: Subject Webpage": "https://www.brookdalecc.edu/continuinged/careerdevelopment/financial-aid-scholarship-opportunities/",
                    "Financial Assistance: Type": "Institutional Grant",
                    "Estimated Duration": estimated_duration,
                    "Learning Method Type": learning_methods,
                }
                courses_writer.writerow(course_row)

print("Processing complete. CSV file generated.")
