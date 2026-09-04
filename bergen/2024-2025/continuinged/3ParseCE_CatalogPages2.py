import os
import csv
from bs4 import BeautifulSoup

# Directory containing the HTML files
html_folder = r"C:\text\NJ\Bergen\ContinuingEd\CE_CatalogPages"
output_csv = "course_data.csv"

# Function to extract information from a single HTML file
def extract_courses_info(file_path):
    courses = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            
            # Find all course containers
            course_containers = soup.find_all("div", class_="course-container")  # Update selector if necessary
            
            for container in course_containers:
                course_data = {
                    "Course Code": "",
                    "Course Title": "",
                    "Course URL": "",
                    "Course Description": "",
                    "Course Prerequisites": "",
                    "Total Program Hours": "",
                    "Textbooks": ""
                }

                # Extract Course Title and URL
                title_tag = container.find("a", class_="title")
                if title_tag:
                    course_data["Course Title"] = title_tag.text.strip()
                    course_data["Course URL"] = title_tag.get("href", "").strip()
                
                # Extract Course Code (assumed to be in title)
                if " | " in course_data["Course Title"]:
                    course_data["Course Code"] = course_data["Course Title"].split(" | ")[0].strip()
                
                # Extract Course Description
                description_tag = container.find("div", class_="content")
                if description_tag:
                    course_data["Course Description"] = description_tag.text.strip()
                
                # Extract Total Program Hours
                hours_tag = container.find("p", string=lambda text: "Total Program Hours" in text if text else False)
                if hours_tag:
                    course_data["Total Program Hours"] = hours_tag.text.split(":")[-1].strip()
                
                # Extract Textbooks (if any textbook information is available)
                textbooks_tag = container.find("div", class_="textbooks")
                if textbooks_tag:
                    course_data["Textbooks"] = textbooks_tag.text.strip()
                
                # Extract Prerequisites
                prerequisites_tag = container.find("div", class_="prerequisites")
                if prerequisites_tag:
                    course_data["Course Prerequisites"] = prerequisites_tag.text.strip()

                courses.append(course_data)
    
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    
    return courses

# Function to process all HTML files in a folder and append to a CSV
def process_html_files(folder_path, output_file):
    fieldnames = ["Course Code", "Course Title", "Course URL", "Course Description", 
                  "Course Prerequisites", "Total Program Hours", "Textbooks"]
    
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
                courses = extract_courses_info(file_path)
                for course in courses:
                    writer.writerow(course)

# Process the HTML files and append the extracted information to a CSV
process_html_files(html_folder, output_csv)

print(f"Processing complete. Data saved to {output_csv}")
