import os
import csv
import requests

# File paths
csv_file_path = r"C:\text\NJ\Salem\course\SCC_Course_Links.csv"
output_directory = r"C:\text\NJ\Salem\course\CoursePDF"

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Define headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "Accept": "application/pdf",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# Read CSV and download PDF files
with open(csv_file_path, newline="", encoding="utf-8-sig") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        course_name = row["Course Name"].replace(" ", "_").replace("/", "-")  # Sanitize filename
        url = row["URL"]
        
        if url:
            print(f"Downloading: {course_name} from {url}")
            
            try:
                response = requests.get(url, headers=headers, timeout=15, stream=True)
                response.raise_for_status()  # Raise error for HTTP failures
                
                # Define the PDF file path
                file_path = os.path.join(output_directory, f"{course_name}.pdf")
                
                # Save PDF content
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                
                print(f"Saved: {file_path}")
            
            except requests.exceptions.RequestException as e:
                print(f"Failed to download {url}: {e}")

print("Download process completed.")
