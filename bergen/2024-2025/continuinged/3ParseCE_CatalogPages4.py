import uuid
import os
import csv
from bs4 import BeautifulSoup

# Directory containing the HTML files
html_folder = r"C:\text\NJ\Bergen\ContinuingEd\CE_CatalogPages"
output_csv = "course_data.csv"

# Generate a unique CTID
def generate_ctid():
    return f"ce-{uuid.uuid4()}"

# Function to extract course information from a single HTML file
def extract_courses_from_file(file_path):
    courses = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

            # Find all course listings
            course_items = soup.find_all("div", class_="listing-item")

            for item in course_items:
                course_data = {
                    "CTID": generate_ctid(),
                    "Learning Type": "Course",
                    "Coded Notation": "",
                    "Learning Opportunity Name": "",
                    "Subject Webpage": "",
                    "Description": "",
                    "Life Cycle Status Type": "Active",
                    "Language": "en",
                }

                # Extract course title and URL
                title_tag = item.find("a", class_="title")
                if title_tag:
                    course_data["Learning Opportunity Name"] = title_tag.text.strip()
                    course_data["Subject Webpage"] = title_tag.get("href", "").strip()

                # Extract course code
                if " | " in course_data["Learning Opportunity Name"]:
                    course_data["Coded Notation"] = course_data["Learning Opportunity Name"].split(" | ")[0].strip()
                    course_data["Learning Opportunity Name"] = title_tag.text.replace("|","-").strip()

                # Extract course description
                description_tag = item.find("div", class_="content")
                if description_tag:
                    course_data["Description"] = description_tag.find("p").text.strip()

                '''# Extract course prerequisites
                prerequisites_tag = item.find("p", text=lambda x: x and "Prerequisites:" in x)
                if prerequisites_tag:
                    course_data["Course Prerequisites"] = prerequisites_tag.text.split(":", 1)[-1].strip()

                # Extract total program hours
                hours_tag = item.find("p", text=lambda x: x and "Total Program Hours:" in x)
                if hours_tag:
                    course_data["Total Program Hours"] = hours_tag.text.split(":", 1)[-1].strip()

                # Extract textbooks
                textbooks_tag = item.find("p", text=lambda x: x and "Required Textbook:" in x)
                if textbooks_tag:
                    course_data["Textbooks"] = textbooks_tag.text.split(":", 1)[-1].strip()'''

                # Add to the courses list
                courses.append(course_data)

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    return courses

# Function to process all HTML files in a folder and append to a CSV
def process_html_files(folder_path, output_file):
    #fieldnames = ["Course Code", "Course Title", "Course URL", "Course Description", 
    #              "Course Prerequisites", "Total Program Hours", "Textbooks"]
    fieldnames = ["CTID", "Learning Type", "Coded Notation", "Learning Opportunity Name", "Subject Webpage", "Description", "Life Cycle Status Type", "Language"]

    # Check if the CSV file exists to determine if headers should be written
    file_exists = os.path.isfile(output_file)

    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write headers only if the file doesn't already exist
        if not file_exists:
            writer.writeheader()

        for filename in os.listdir(folder_path):
            if filename.endswith(".html"):
                file_path = os.path.join(folder_path, filename)
                courses = extract_courses_from_file(file_path)
                writer.writerows(courses)

# Process the HTML files and append the extracted information to a CSV
process_html_files(html_folder, output_csv)

print(f"Processing complete. Data saved to {output_csv}")
