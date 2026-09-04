import os
import csv
import requests

def download_course_html():
    # Get the current working directory
    current_dir = os.getcwd()
    # Define input CSV and output directory
    input_csv = os.path.join(current_dir, "parsed_courses.csv")
    output_folder = os.path.join(current_dir, "CoursesHTML")

    # Create the output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Read the CSV and download HTML files
    with open(input_csv, "r", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:
            course_code = row.get("Course Code", "").strip()
            url = row.get("URL", "").strip()

            if course_code and url:
                try:
                    print(f"Downloading {course_code} from {url}...")
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()

                    # Save the HTML content to a file
                    output_file = os.path.join(output_folder, f"{course_code}.html")
                    with open(output_file, "w", encoding="utf-8") as f_out:
                        f_out.write(response.text)

                    print(f"Saved {course_code} to {output_file}")
                except requests.RequestException as e:
                    print(f"[ERROR] Failed to download {course_code} from {url}: {e}")

    print(f"\nAll files downloaded to: {output_folder}")

if __name__ == "__main__":
    download_course_html()
