import os
import PyPDF2
import pandas as pd
import re

'''def clean_extracted_text(text):
    #print("Raw extracted text:", text[:500])  # Print first 500 characters of the raw text for debugging

    # Adjust regex to account for potential variations in how line feeds and spaces are used
    #pattern = r'\n{2,}\s*([A-Z ]+)\s*\n{2,}([\s\S]+?)\n{3,}'
    pattern = r'^\n{2,}\s*([A-Z ]+)'
    match = re.search(pattern, text)

    if match:
        description = match.group(2)
        # Normalize space characters
        description = description.replace('\n', ' ').strip()
        description = re.sub(r'\s{2,}', ' ', description)
        return description
    else:
        return "Description not found."'''
def clean_extracted_text(text):
    # Regex to find the description starting after a word in uppercase followed by 3 line feeds
    #pattern = r'\n{3,}[A-Z]+\s+\n{2,}([\s\S]+?)\n{3,}'
    pattern = r'^\s*\n{2,}\s*([A-Z ]+)\s*\n{2,}([\s\S]+?)\s*\n{3,}'
    match = re.search(pattern, text)
    if match:
        description = match.group(1)
        description = description.replace('\n', ' ')  # Remove all single newlines
        description = re.sub(r'\s{2,}', ' ', description)  # Replace multiple spaces with a single space
        return description.strip()  # Trim whitespace
    else:
        return "Description not found."

def extract_pdf_description(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if len(reader.pages) > 1:  # Check if there is at least a second page
                page = reader.pages[1]  # Page indexing starts at 0; 1 is the second page
                text = page.extract_text()
                if text:
                    text = text.replace('\n', ' ')  # Remove all single newlines
                    text = re.sub(r'\s{2,}', ' ', text)  # Replace multiple spaces with a single space
                    # Regex to remove all text following the first occurrence of "Elective Categories"
                    text = re.sub(r'Elective Cat.*', '', text, flags=re.S)
                    text = re.sub(r'^.*?\bThe\b', 'The', text, flags=re.S)
                    text = re.sub(r'^.*?\bThis\b', 'This', text, flags=re.S)
                    return text, clean_extracted_text(text)
                else:
                    return "No text found on page 2", "No text found on page 2"
            else:
                return "No Description found.","No second page"
    except Exception as e:
        return f"Error reading PDF: {e}"

def extract_pdf_C_description(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if len(reader.pages) > 0:  # Check if there is at least a page
                page = reader.pages[0]  # Page indexing starts at 0; 1 is the second page
                text = page.extract_text()
                if text:
                    text = text.replace('\n', ' ')  # Remove all single newlines
                    text = re.sub(r'\s{2,}', ' ', text)  # Replace multiple spaces with a single space
                    # Regex to remove all text following the first occurrence of "Elective Categories"
                    text = re.sub(r'Curriculum.*', '', text, flags=re.S)
                    text = re.sub(r'General Education.*', '', text, flags=re.S)
                    text = re.sub(r'^.*?\bThe\b', 'The', text, flags=re.S)
                    text = re.sub(r'^.*?\bThis\b', 'This', text, flags=re.S)
                    return text, clean_extracted_text(text)
                else:
                    return "No text found on page 1", "No text found on page 2"
            else:
                return "No Description found.","No second page"
    except Exception as e:
        return f"Error reading PDF: {e}"

def parse_pdfs_in_folder(folder_path):
    descriptions = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf') and filename.startswith('A'):
            pdf_path = os.path.join(folder_path, filename)
            rawtext, description = extract_pdf_description(pdf_path)
            descriptions.append({
                'Filename': filename,
                'Description': rawtext
            })
        elif filename.endswith('.pdf') and filename.startswith('C'):
            pdf_path = os.path.join(folder_path, filename)
            rawtext, description = extract_pdf_C_description(pdf_path)
            descriptions.append({
                'Filename': filename,
                'Description': rawtext
            })
    
    df = pd.DataFrame(descriptions)
    output_csv_path = os.path.join('pdf_descriptions.csv')
    df.to_csv(output_csv_path, index=False)
    print(f'Data saved to {output_csv_path}')

# Define the folder path containing the PDF files
pdf_folder_path = r"C:\text\NJ\Warren\credentials\CredentialPDF"

# Run the function
parse_pdfs_in_folder(pdf_folder_path)
