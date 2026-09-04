import re
import csv
import PyPDF2

# Define file path
pdf_path = r"C:\text\NJ\Warren\course\2024-25-Academic-Catalog.pdf"

# Define start and end pages
start_page = 77  # Actual page in document
end_page = 104   # Actual page in document

# Open and read the PDF
with open(pdf_path, "rb") as file:
    reader = PyPDF2.PdfReader(file)
    extracted_text = ""

    # Extract text from the specified pages
    for page_num in range(start_page - 1, end_page):  # Convert to zero-based index
        extracted_text += reader.pages[page_num].extract_text() + "\n"

# Save extracted text to a file (for debugging if needed)
text_output_path = r"C:\text\NJ\Warren\course\extracted_course_info.txt"
with open(text_output_path, "w", encoding="utf-8") as output_file:
    output_file.write(extracted_text)

print(f"Extracted text saved to: {text_output_path}")

# Regex pattern for identifying a course title (e.g., ACC 101 Principles of Accounting I)
course_pattern = re.compile(r"^([A-Z]{3} \d{3}) (.+)$")

# Updated regex pattern for identifying credits (matches "3 cr." and "3 cr .")
credits_pattern = re.compile(r"(\d+ cr\s?\.)")

# Regex pattern for instruction method (e.g., LEC 3 hrs.)
instruction_pattern = re.compile(r"(LEC|LEC/LAB|LAB) \d+ hrs\.")

# Regex pattern for prerequisites (e.g., Prerequisite: ACC 101)
prerequisite_pattern = re.compile(r"Prerequisite[s]?: (.+)")

# Output data storage
courses = []
current_course = None  # Ensure no uninitialized course

# Process each line
lines = extracted_text.split("\n")
for i, line in enumerate(lines):
    course_match = course_pattern.match(line.strip())
    
    if course_match:
        # Store the previous course before moving to a new one
        if current_course:
            courses.append(current_course)

        # Start a new course entry
        current_course = {
            "Coded Notation": course_match.group(1),
            #"Title": course_match.group(2).replace("3 cr .","").replace("4 cr .","").strip(),
            "Learning Opportunity Name": course_match.group(1)+" - "+re.sub(r"\d+\s*(eq\.\s*)?cr\s?\.", "", course_match.group(2)).strip(),
            #"Credits": "",
            #"Instruction": "",
            #"Prerequisites": "",
            "Description": "",
            "Language": "English",
            "Learning Type": "Course",
            "Life Cycle Status Type": "Active",
            "In Catalog": "https://www.warren.edu/wp-content/uploads/2024/10/2024-25-Academic-Catalog.pdf",
            "Version Identifier": "2024-2025 Catalog",
            #"DescriptionTest": ""
        }
    
    elif current_course:  # Only process details if a course has been identified
        if credits_pattern.match(line.strip()):
            continue
            #current_course["Credits"] = line.strip()
        #elif instruction_pattern.match(line.strip()):
        #    current_course["Instruction"] = line.strip()
        #elif prerequisite_pattern.match(line.strip()):
        #    current_course["Prerequisites"] = prerequisite_pattern.match(line.strip()).group(1)
        elif line.strip():  # Append to description only if a course is found
            cleaned_line = re.sub(r"\d+\s*(eq\.\s*)?cr\s?\.", "", line).strip()
            sentences = re.findall(r"(.*?[.])(?:\s+[A-Z]|\Z)", cleaned_line)  # Extract all full sentences
            if sentences:
                #current_course["DescriptionTest"] = sentences
                if sentences[0].startswith("*Special topics"):  # Skip this sentence
                    current_course["Description"] = sentences[1] if len(sentences) > 1 else ""  # Take next sentence if available
                else:
                    current_course["Description"] = sentences[0]  # Use first valid sentence

            #current_course["Description"] += line.replace(" 3 cr .","").replace(" Lec. 3 hours","") + " "
            #current_course["Description"] += re.sub(r"\d+\s*(eq\.\s*)?cr\s?\.", "", line).strip() + " "

# Add last course if it exists
if current_course:
    courses.append(current_course)

# Save to CSV file
csv_filename = r"C:\text\NJ\Warren\course\Warren_BU_Credit_Courses.csv"

with open(csv_filename, "w", newline="", encoding="utf-8-sig") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
    "Coded Notation", 
    "Learning Opportunity Name", 
    "Description", 
    "Language", 
    "Learning Type", 
    "Life Cycle Status Type", 
    "In Catalog", 
    "Version Identifier"
])

    writer.writeheader()
    writer.writerows(courses)

print(f"Course data saved to: {csv_filename}")
