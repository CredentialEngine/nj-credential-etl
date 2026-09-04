import os
import csv
from PyPDF2 import PdfReader

def parse_pdf(file_path):
    """Parse the PDF and extract relevant information."""
    data = {"Course Title": "", "Course Description": "", "Student Learning Objectives": "", "Main Topics": ""}
    
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        lines = text.split("\n")
        
        # Extract Course Title
        for line in lines:
            if line.strip().startswith("ACC-100"):
                data["Course Title"] = line.strip()
                break

        # Extract Course Description
        description_start = "Course:"
        description_end = "Course Materials:"
        description_lines = []
        in_description = False
        for line in lines:
            if description_start in line:
                in_description = True
            elif description_end in line:
                in_description = False
            if in_description:
                description_lines.append(line.strip())
        data["Course Description"] = " ".join(description_lines).replace(description_start, "").strip()

        # Extract Student Learning Objectives
        objectives_start = "Student Learning Objectives:"
        objectives_end = "Course Content:"
        objectives_lines = []
        in_objectives = False
        for line in lines:
            if objectives_start in line:
                in_objectives = True
            elif objectives_end in line:
                in_objectives = False
            if in_objectives:
                objectives_lines.append(line.strip())
        data["Student Learning Objectives"] = " ".join(objectives_lines).replace(objectives_start, "").strip()

        # Extract Main Topics
        topics_start = "Course Content:"
        topics_lines = []
        in_topics = False
        for line in lines:
            if topics_start in line:
                in_topics = True
            elif line.strip().startswith("Course Requirements"):
                in_topics = False
            if in_topics and not line.startswith("Course Content:"):
                topics_lines.append(line.strip())
        data["Main Topics"] = " | ".join(topics_lines)
    
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    
    return data

def process_pdfs(input_folder, output_file):
    """Process all PDFs in the input folder and save extracted data to a CSV file."""
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["Course Title", "Course Description", "Student Learning Objectives", "Main Topics"])
        writer.writeheader()
        
        for filename in os.listdir(input_folder):
            if filename.endswith(".pdf"):
                file_path = os.path.join(input_folder, filename)
                parsed_data = parse_pdf(file_path)
                writer.writerow(parsed_data)

if __name__ == "__main__":
    INPUT_FOLDER = r"C:\text\NJ\Bergen\course\syllabus"  # Replace with the path to your PDF folder
    OUTPUT_FILE = "syllabus_data.csv"  # Path for the output CSV file
    process_pdfs(INPUT_FOLDER, OUTPUT_FILE)
