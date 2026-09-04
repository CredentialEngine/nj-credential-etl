import os
import csv
from bs4 import BeautifulSoup
#Save the HTML from this URL to the directory. Manually make the perpage set to 900
#https://www.course-catalog.com/mcc/C/2024-2025/course-a-z?perpage=900

def main():
    # Get the current working directory
    current_dir = os.getcwd()
    # Define the relative subdirectory
    input_folder = os.path.join(current_dir)
    output_csv = os.path.join(current_dir, "parsed_courses.csv")

    # Prepare CSV for writing
    with open(output_csv, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        # Write header row
        writer.writerow(["Course Code", "Course Name", "URL", "Credits"])

        # Loop over every HTML file in the directory
        for filename in os.listdir(input_folder):
            if not filename.lower().endswith(".html"):
                continue  # Skip non-HTML files

            full_path = os.path.join(input_folder, filename)
            try:
                with open(full_path, "r", encoding="utf-8") as f_in:
                    html = f_in.read()
            except (UnicodeDecodeError, OSError) as e:
                print(f"[ERROR] Cannot read {filename}: {e}")
                continue

            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(html, "lxml")

            # Find all rows in the table
            rows = soup.find_all("tr")
            for row in rows:
                # Extract Course Code
                code_cell = row.find("td", {"data-label": "Program Name"})
                course_code = ""
                course_url = ""
                if code_cell:
                    link = code_cell.find("a")
                    if link:
                        course_code = link.get_text(strip=True)
                        course_url = link.get("href", "")

                # Extract Course Name
                name_cell = row.find("td", {"data-label": "Degree Type"})
                course_name = ""
                if name_cell:
                    div = name_cell.find("div", class_="desktop-cou-title")
                    if div:
                        link = div.find("a")
                        if link:
                            course_name = link.get_text(strip=True)

                # Extract Credits
                credits_cell = row.find("td", class_="program-list-content")
                credits = ""
                if credits_cell:
                    credits = credits_cell.get_text(strip=True)

                # Write to CSV if all required fields are present
                if course_code and course_name and course_url:
                    writer.writerow([course_code, course_name, course_url, credits])

    print(f"\nDone. CSV saved to: {output_csv}")

if __name__ == "__main__":
    main()
