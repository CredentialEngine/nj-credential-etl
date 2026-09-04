import pandas as pd
import uuid
import re

def generate_ctid():
    return "ce-" + str(uuid.uuid4())

def clean_prerequisite(text):
    """
    Remove leading 's:' or ':' and trailing ')' from each prerequisite,
    split by commas, prepend a base URL to each, and join them with a pipe.
    """
    #text = re.sub(r'^\s*s:\s*|\s*:\s*', '', text)
    #text = re.sub(r'\)$', '', text)
    #base_url = " "
    #prerequisites = [f"{base_url}{req.strip()}" for req in text.split(",") if req.strip()]
    #prerequisites = [f"{base_url}{req.strip()}" for req in text.split("and") if req.strip()]
    #return " | ".join(prerequisites)
    return text

def clean_method(text):
    method_list = []

    if "field experience" in text.lower():
        method_list.append("Applied")
    if "lecture" in text.lower():
        method_list.append("Lecture")
    if "lab" in text.lower():
        method_list.append("Laboratory")
    if "studio" in text.lower():
        method_list.append("Work Based")

    return "|".join(method_list) if method_list else ""

# Input file (merged CSV)
input_file = r"C:\text\NJ\Middlesex\courses\merged_courses.csv"
df = pd.read_csv(input_file, delimiter=",", encoding="utf-8-sig")

# Debug: Print available columns
print("Available Columns:", df.columns.tolist())

# Strip extra spaces from column names
df.columns = df.columns.str.strip()

# Verify that expected column(s) exist (using 'Course Code_x' as our primary identifier)
if "Course Code_x" not in df.columns:
    raise KeyError("Column 'Course Code_x' not found. Please check the input file formatting.")

# Define the BU output columns
output_columns = [
    "CTID", "External Identifier", "Coded Notation", "Learning Type", "Learning Opportunity Name",
    "Description", "Language", "Life Cycle Status Type", "Subject Webpage", "Credit Unit Value",
    "Credit Unit Type", "Credit Unit Type Description", "Is Non-Credit",
    "Version Identifier", "Prerequisite", "Learning Method Type"
]

output_data = []

for _, row in df.iterrows():
    # Map external identifier and coded notation from "Course Code_x"
    external_identifier = row["Course Code_x"].strip() if pd.notna(row["Course Code_x"]) else ""
    coded_notation = external_identifier

    # Build the Learning Opportunity Name from "Course Code_x" and "Course Title"
    course_title = row["Course Title"].strip() if pd.notna(row["Course Title"]) else ""
    learning_opportunity_name = f"{external_identifier} - {course_title}" if external_identifier else course_title

    # Use the "Course Description" column for Description
    description = row["Course Description"].strip() if pd.notna(row["Course Description"]) else "No description available"

    # Set Language and Life Cycle Status
    language = "English"
    life_cycle_status_type = "Active"

    # In Catalog: use the "URL" column
    in_catalog = row["URL"].strip() if pd.notna(row["URL"]) else ""
    
    #Method
    method = clean_method(row["Instruction Methods"].strip() if pd.notna(row["Instruction Methods"]) else "")

    # Process Credits from the "Credits" column.
    # Example: "4 Credits" => extract numeric value 4
    credit_text = str(row["Credits"]).strip() if pd.notna(row["Credits"]) else ""
    credit_match = re.search(r'(\d+(\.\d+)?)', credit_text)
    if credit_match:
        credit_unit_value = float(credit_match.group(1))
        credit_unit_max_value = credit_unit_value
        credit_unit_type = "Credit Hours"
        credit_unit_type_description = "SemesterHour"
        noncredit = ""
    else:
        credit_unit_value = ""
        credit_unit_max_value = ""
        credit_unit_type = ""
        credit_unit_type_description = ""
        noncredit = "TRUE"

    # Date Effective is not provided; leave empty.
    date_effective = ""

    # Version Identifier hardcoded.
    version_identifier = "2024-2025 Catalog"

    # Process the Prerequisite column using our clean_prerequisite function if present.
    if pd.notna(row.get("Prerequisite", "")) and row["Prerequisite"].strip() != "":
        prerequisite = clean_prerequisite(row["Prerequisite"].strip())
    else:
        prerequisite = ""

    # Append a new row of mapped data.
    output_data.append([
        generate_ctid(), external_identifier, coded_notation, "Course", learning_opportunity_name,
        description, language, life_cycle_status_type, in_catalog, credit_unit_value,
        credit_unit_type, credit_unit_type_description, noncredit,
        version_identifier, prerequisite, method
    ])

# Convert output data into a DataFrame with the specified headers.
output_df = pd.DataFrame(output_data, columns=output_columns)

# Save the output DataFrame to a CSV file in the desired folder.
output_file = r"C:\text\NJ\Middlesex\courses\Middlesex_BU_Credit_Courses.csv"
output_df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"Conversion complete. Output saved to {output_file}")
