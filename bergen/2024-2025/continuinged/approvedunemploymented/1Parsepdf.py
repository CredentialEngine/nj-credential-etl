import csv
import os
from PyPDF2 import PdfReader

# Define the input PDF and output CSV paths
input_pdf_path = r"C:\text\NJ\Bergen\ContinuingEd\ApprovedUnemploymentEd\Unemployment-Chart-April-11.pdf"
output_csv_path = r"C:\text\NJ\Bergen\ContinuingEd\ApprovedUnemploymentEd\unemployment_courses.csv"

# Define the headers for the CSV file
headers = [
    "Course Name",
    "In Demand",
    "Virtual Option",
    "Classroom Hours",
    "Timeframe",
    "Cost",
    "Prerequisite"
]

# Function to clean and split the data
def clean_and_split_line(line):
    return [item.strip() for item in line.split("  ") if item.strip()]

# Parse the PDF
def parse_pdf_to_csv(pdf_path, csv_path):
    reader = PdfReader(pdf_path)
    data_rows = []
    
    # Extract text from each page of the PDF
    for page in reader.pages:
        text = page.extract_text()
        lines = text.split("\n")
        
        for line in lines:
            # Skip headers and irrelevant lines
            if line.startswith(("COURSE NAME", "Bergen Community College")) or not line.strip():
                continue
            
            # Clean and parse line
            row = clean_and_split_line(line)
            if len(row) >= 6:  # Ensure minimum required columns
                data_rows.append(row)
    
    # Save to CSV
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)  # Write headers
        writer.writerows(data_rows)  # Write data rows

    print(f"Data has been extracted and saved to {csv_path}")

# Call the function to parse and save the data
parse_pdf_to_csv(input_pdf_path, output_csv_path)
