import os
import csv
import pdfplumber

#Nov 22, 2024 The information in this table doesn't match the credit credentials, course, or non-credit courses for Bergen.

def extract_table_from_pdf(pdf_path):
    """Extract table data from a PDF file."""
    data = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        data.append(row)
    except Exception as e:
        print(f"Error extracting table from {pdf_path}: {e}")
    return data

def save_to_csv(data, output_file):
    """Save extracted data to a CSV file."""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

def process_pdfs(input_folder, output_csv):
    """Process all PDFs in the input folder and save extracted table data to a CSV file."""
    all_data = []
    for filename in os.listdir(input_folder):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(input_folder, filename)
            print(f"Processing {filename}...")
            extracted_data = extract_table_from_pdf(pdf_path)
            all_data.extend(extracted_data)

    save_to_csv(all_data, output_csv)

if __name__ == "__main__":
# Define the input PDF and output CSV paths
    INPUT_FOLDER = r"C:\text\NJ\Bergen\ContinuingEd\ApprovedUnemploymentEd"  # Replace with the path to your PDF folder
    OUTPUT_FILE = "extracted_data.csv"  # Replace with the desired CSV file path
    process_pdfs(INPUT_FOLDER, OUTPUT_FILE)
    print(f"Data extraction complete. Saved to {OUTPUT_FILE}.")
