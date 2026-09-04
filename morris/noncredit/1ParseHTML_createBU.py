import os
import pandas as pd
import uuid
import re
from bs4 import BeautifulSoup

# Generate a unique CTID
def generate_ctid():
    return "ce-" + str(uuid.uuid4())

# Function to extract price from fee text
def extract_price(fee_text):
    match = re.search(r"\$[\s]*([\d,]+\.?\d*)", fee_text)
    return match.group(1).replace(",", "") if match else "Unknown"

# Directory containing HTML course files
input_directory = r"C:\text\NJ\Morris\noncredit\Course"
output_csv = r"C:\text\NJ\Morris\noncredit\Morris_BU_NonCredit_Courses.csv"

# Define CSV headers
output_columns = [
    "CTID", "External Identifier", "Coded Notation", "Learning Type", "Learning Opportunity Name",
    "Description", "Language", "Life Cycle Status Type", "Subject Webpage", "Is Non-Credit", 
    "Version Identifier", "Cost: External Identifier", "Cost: Description", "Cost: Currency Type",
    "Cost: Types List", "Cost: Details Url", "Delivery Type", #"Learning Method Type",
    #"Start Date", "End Date", "Location"
]

# List to store extracted course data
output_data = []

# Process each HTML file in the directory
for filename in os.listdir(input_directory):
    if filename.endswith(".html"):
        file_path = os.path.join(input_directory, filename)

        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

            # Find all course containers in the HTML file
            course_containers = soup.find_all("div", class_="wc_container")

            for course in course_containers:
                # Extract title (course name and ID)
                title_element = course.find("h4", class_="wc_title")
                title = title_element.get_text(strip=True) if title_element else "Unknown"

                # Extract course ID from title
                course_id_match = re.search(r"\((.*?)\)", title)
                course_id = course_id_match.group(1) if course_id_match else "Unknown"

                # Extract description
                #description_element = course.find("div", class_="wc_paragraph wc_truncate")
                #description = description_element.get_text(" ", strip=True) if description_element else "No description available"
                # Extract description element
                description_element = course.find("div", class_="wc_paragraph wc_truncate")

                # Get raw HTML content if available
                if description_element:
                    description_html = str(description_element)

                    # Find the last occurrence of "</i></p><p>"
                    split_point = description_html.rfind("</i></p><p>")
                    
                    if split_point != -1:
                        # Extract text after the last occurrence
                        description_html = description_html[split_point + len("</i></p><p>"):]
                    
                    # Convert HTML to plain text using BeautifulSoup
                    description = BeautifulSoup(description_html, "html.parser").get_text(" ", strip=True)
                else:
                    description = "No description available"

                

                # Extract start date
                start_date_element = course.find("b", string="Start date")
                start_date = start_date_element.find_next("p").get_text(strip=True) if start_date_element else "Unknown"

                # Extract end date
                end_date_element = course.find("b", string="End date")
                end_date = end_date_element.find_next("p").get_text(strip=True) if end_date_element else "Unknown"

                # Extract location
                location_element = course.find("b", string="Location")
                location = location_element.find_next("p").get_text(strip=True) if location_element else "Unknown"

                # Extract cost (fee)
                fee_element = course.find("h3", class_="wc_fee")
                cost = extract_price(fee_element.get_text(strip=True)) if fee_element else "Unknown"

                # Extract subject webpage (enrollment link)
                buy_link_element = course.find("a", class_="wc_buy_button")
                subject_webpage = "https://www.ccm.edu/?s=" + course_id

                # Set default values
                #delivery_type = "In-Person" if location != "Remote" or location != "Remote Live" or location != "Online Hybrid Course" else "OnlineOnly"
                delivery_type = "OnlineOnly" if location in ["Remote", "Remote Live", "Online Hybrid Course"] else "In-Person"
                #learning_method_type = "Lecture"
                version_identifier = "2024-2025 Catalog"
                noncredit = "TRUE"

                # Append extracted data to output list
                output_data.append([
                    generate_ctid(), course_id, course_id, "Course", title,
                    description, "English", "Active", subject_webpage, noncredit,
                    version_identifier, course_id, f"Tuition for {title}", "USD",
                    cost, "https://www.ccm.edu/workforce-development/", delivery_type, #learning_method_type,
                    #start_date, end_date, location
                ])

# Convert list to DataFrame and save as CSV
output_df = pd.DataFrame(output_data, columns=output_columns)
output_df.to_csv(output_csv, index=False, encoding="utf-8-sig")

print(f"Parsing complete. Output saved to {output_csv}")
