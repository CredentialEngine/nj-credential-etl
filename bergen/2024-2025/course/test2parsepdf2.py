import os
import csv
import fitz  # PyMuPDF

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    text = ""
    try:
        pdf_document = fitz.open(file_path)
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text += page.get_text()
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
    return text

def parse_pdf(file_path, text):
    """Parse the PDF text to extract relevant information."""
    lines = text.split("\n")
    data = {"File": "", "Course Title": "", "Course Description": "", "Student Learning Objectives": "", "Main Topics": ""}

    # Assign Filename
    data["File"] = file_path

    # Extract Course Title
    for line in lines:
        if line.strip().startswith("ACC-100"):  # Adjust the condition as needed
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

    return data

def process_pdfs(input_folder, output_file, text_output_folder):
    """Process all PDFs in the input folder, save extracted text to files, and save data to a CSV."""
    os.makedirs(text_output_folder, exist_ok=True)  # Create the directory if it doesn't exist

    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["File", "Course Title", "Course Description", "Student Learning Objectives", "Main Topics"])
        writer.writeheader()
        
        for filename in os.listdir(input_folder):
            if filename.endswith(".pdf"):
                file_path = os.path.join(input_folder, filename)

                # Extract text from the PDF
                text = extract_text_from_pdf(file_path)

                # Save the extracted text to a .txt file
                text_file_name = os.path.splitext(filename)[0] + ".txt"
                text_file_path = os.path.join(text_output_folder, text_file_name)
                with open(text_file_path, 'w', encoding='utf-8') as text_file:
                    text_file.write(text)

                # Parse the extracted text
                parsed_data = parse_pdf(file_path, text)
                writer.writerow(parsed_data)

if __name__ == "__main__":
    INPUT_FOLDER = r"C:\text\NJ\Bergen\course\syllabus"  # Path to your PDF folder
    OUTPUT_FILE = "syllabus_data.csv"  # Path for the output CSV file
    TEXT_OUTPUT_FOLDER = r"C:\text\NJ\Bergen\course\syllabus\text_files"  # Directory for text files
    process_pdfs(INPUT_FOLDER, OUTPUT_FILE, TEXT_OUTPUT_FOLDER)
