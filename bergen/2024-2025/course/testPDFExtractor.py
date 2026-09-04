from PyPDF2 import PdfReader

file_path = r"C:\text\NJ\Bergen\course\syllabus\ACC-100.pdf"  # Replace with your PDF file path

reader = PdfReader(file_path)
text = ""
for page in reader.pages:
    text += page.extract_text()

print(text)
