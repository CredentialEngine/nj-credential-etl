import os
import csv
from bs4 import BeautifulSoup

def parse_course_html():
    # Get the current working directory
    current_dir = os.getcwd()
    input_folder = os.path.join(current_dir, "CoursesHTML")
    output_csv = os.path.join(current_dir, "parsed_course_details.csv")

    # Prepare CSV for writing
    with open(output_csv, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        # Write header row
        writer.writerow([
            "Filename", "Course Code", "Course Title", "Course Description",
            "Instruction Methods", "Prerequisite", "Corequisites", "Subject Webpage"
        ])

        # Process each HTML file
        for filename in os.listdir(input_folder):
            if not filename.endswith(".html"):
                continue

            file_path = os.path.join(input_folder, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f_in:
                    html = f_in.read()

                # Parse the HTML using BeautifulSoup
                soup = BeautifulSoup(html, "html.parser")

                # Extract data fields
                course_code = soup.find("div", class_="course-code-val")
                course_title = soup.find("h1")
                course_description = soup.find("div", class_="course-desc-val")
                instruction_methods = soup.find("div", class_="course-instruction-methods")
                prerequisites = soup.find("div", class_="course-prerequisites-val")
                corequisites = soup.find("div", class_="course-corequisites-val")
                data_url = soup.find("a", class_="add-this-page")

                # Clean and extract text
                course_code = course_code.get_text(strip=True) if course_code else ""
                course_title = course_title.get_text(strip=True) if course_title else ""
                course_description = course_description.get_text(strip=True) if course_description else ""
                instruction_methods = instruction_methods.get_text(strip=True) if instruction_methods else ""
                #prerequisites = prerequisites.get_text(strip=True) if prerequisites else ""
                prerequisites = " ".join(prerequisites.stripped_strings) if prerequisites else ""
                #corequisites = corequisites.get_text(strip=True) if corequisites else ""
                corequisites = " ".join(corequisites.stripped_strings) if corequisites else ""
                data_url = "https://www.course-catalog.com"+data_url["data-url"] if data_url else ""

                # Write to CSV
                writer.writerow([
                    filename, course_code, course_title, course_description,
                    instruction_methods, prerequisites, corequisites, data_url
                ])

                print(f"[OK] Parsed {filename}")

            except Exception as e:
                print(f"[ERROR] Failed to process {filename}: {e}")

    print(f"\nParsing complete. Results saved to: {output_csv}")

if __name__ == "__main__":
    parse_course_html()
