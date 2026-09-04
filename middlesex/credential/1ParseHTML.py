import os
import csv
from bs4 import BeautifulSoup

def main():
    # Get the current working directory
    current_dir = os.getcwd()
    # Define the relative subdirectory
    input_folder = os.path.join(current_dir)
    output_csv = os.path.join(current_dir, "parsed_credentials.csv")

    print(f"Input folder: {input_folder}")
    print(f"Output CSV: {output_csv}")

    # Prepare CSV for writing
    with open(output_csv, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        # Write header row
        writer.writerow(["Program Name", "Degree Type", "Department", "Careers URL", "Degree URL"])

        # Loop over every HTML file in the directory
        for filename in os.listdir(input_folder):
            if not filename.lower().endswith(".html"):
                print(f"Skipping non-HTML file: {filename}")
                continue  # Skip non-HTML files

            print(f"Processing file: {filename}")

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
            print(f"Found {len(rows)} rows in {filename}")

            for row in rows:
                # Extract Program Name and Degree URL
                program_name_cell = row.find("td", id=lambda x: x and x.startswith("program"))
                program_name = ""
                degree_url = ""

                if program_name_cell:
                    link = program_name_cell.find("a")
                    if link:
                        program_name = link.get("aria-label", "").split(" - ")[0]  # Extract from aria-label
                        degree_url = link.get("href", "")  # Extract the degree URL

                # Extract Degree Type
                degree_type_cell = row.find_all("td", class_="program-list-content")
                degree_type = degree_type_cell[0].get_text(strip=True) if len(degree_type_cell) > 0 else ""
                department = degree_type_cell[1].get_text(strip=True) if len(degree_type_cell) > 1 else ""

                # Extract Careers URL
                careers_url = ""
                if len(degree_type_cell) > 2:
                    careers_cell = degree_type_cell[2]
                    link = careers_cell.find("a")
                    if link:
                        careers_url = link.get("href", "")

                print(f"Extracted: Program Name={program_name}, Degree Type={degree_type}, "
                      f"Department={department}, Careers URL={careers_url}, Degree URL={degree_url}")

                # Write to CSV if any required fields are present
                if program_name or degree_type or department or careers_url or degree_url:
                    writer.writerow([program_name, degree_type, department, careers_url, degree_url])
                else:
                    print(f"Skipping incomplete row in {filename}")

    print(f"\nDone. CSV saved to: {output_csv}")

if __name__ == "__main__":
    main()
