import fitz  # PyMuPDF
import csv

def extract_text_from_pdf(pdf_path):
    text_data = []
    with fitz.open(pdf_path) as pdf_document:
        for page_num, page in enumerate(pdf_document, start=1):
            text = page.get_text("text").strip()
            text_data.append([page_num, text])  # Store page number and text

    return text_data

def save_text_to_csv(text_data, csv_path):
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Page Number", "Extracted Text"])  # Header
        writer.writerows(text_data)

pdf_path = r"C:\text\NJ\Warren\course\2024-25-Academic-Catalog.pdf"  # Replace with your file path
csv_path = "extracted_text.csv"  # CSV output file

# Extract text and save to CSV
text_data = extract_text_from_pdf(pdf_path)
save_text_to_csv(text_data, csv_path)

print(f"Extraction complete! CSV saved as {csv_path}")
