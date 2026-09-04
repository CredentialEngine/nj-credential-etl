import os
import csv
import requests

# Define file paths
input_csv = r"C:\text\NJ\Bergen\course\Bergen_courses.csv"
output_folder = r"C:\text\NJ\Bergen\course\syllabus"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

def download_pdf(url, output_path):
    """Download a PDF from a given URL and save it to the specified path."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    }
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()  # Raise an error for bad HTTP status
        with open(output_path, 'wb') as pdf_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    pdf_file.write(chunk)
        print(f"Downloaded: {url}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")

# Open and read the CSV
with open(input_csv, 'r', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        syllabus_url = row.get('Syllabus')
        if syllabus_url and syllabus_url.endswith('.pdf'):
            # Determine output file name
            file_name = os.path.basename(syllabus_url)
            output_path = os.path.join(output_folder, file_name)
            # Download the PDF
            download_pdf(syllabus_url, output_path)

print("All downloads complete.")
