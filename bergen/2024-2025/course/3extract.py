import os
import csv
from bs4 import BeautifulSoup
import unicodedata

def normalize_text(text):
    # Normalize Unicode data to remove extraneous characters
    return unicodedata.normalize("NFKD", text)

def parse_html_to_csv(input_folder, output_file):
    # Open the CSV file for writing
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Course Title', 'URL'])

        # Iterate over all files in the input folder
        for filename in os.listdir(input_folder):
            if filename.endswith(".html"):
                file_path = os.path.join(input_folder, filename)
                with open(file_path, 'r', encoding='utf-8-sig') as file:
                    soup = BeautifulSoup(file, 'lxml')

                    # Find all <a> tags with href and title attributes
                    for a_tag in soup.find_all('a', href=True, title=True):
                        course_title = normalize_text(a_tag.get_text(strip=True))
                        course_url = a_tag['href']
                        writer.writerow([course_title, course_url])

if __name__ == "__main__":
    # Input folder containing the HTML files
    INPUT_FOLDER = r"C:\text\NJ\Bergen\course\bergen_course_pages"  # Replace with your directory path
    OUTPUT_FILE = "output.csv"  # The output CSV file path

    parse_html_to_csv(INPUT_FOLDER, OUTPUT_FILE)
