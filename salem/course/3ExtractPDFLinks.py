import os
import re
import csv
from bs4 import BeautifulSoup

# Define directory and output file
directory = r"C:\text\NJ\Salem\course\CoursePDF"
output_file = r"C:\text\NJ\Salem\course\CourseDirectNoAuthPDFLinks.csv"

# List to store filename and extracted URLs
data = []

# Regex pattern to locate `.downloadUrlNoAuth` key in JavaScript
download_url_pattern = re.compile(r'"\.downloadUrlNoAuth"\s*:\s*"([^"]+)"')

# Iterate over each file in the directory
for filename in os.listdir(directory):
    if filename.endswith(".pdf"):  # Ensuring we only process mislabeled HTML files
        file_path = os.path.join(directory, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

                # Parse HTML using BeautifulSoup
                soup = BeautifulSoup(content, "html.parser")

                # Find all <script> tags
                script_tags = soup.find_all("script")

                # Search for the pattern in all script contents
                for script in script_tags:
                    match = download_url_pattern.search(script.text)
                    if match:
                        url = match.group(1).encode().decode('unicode_escape')  # Fix Unicode escape sequences
                        data.append([filename, url])
                        break  # Stop after the first match per file

        except (FileNotFoundError, PermissionError) as e:
            print(f"Skipping {filename}: {e}")

# Write results to a CSV file
with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Filename", "DownloadUrlNoAuth"])  # Header row
    writer.writerows(data)

print(f"Extraction complete! CSV saved at {output_file}")
