import pandas as pd
import json
import uuid
import re

def generate_ctid():
    return "ce-" + str(uuid.uuid4())

def clean_prerequisite(text):
    # Remove any leading "s:" or ":" and trailing ")" from the prerequisite text.
    text = re.sub(r'^\s*s:\s*|\s*:\s*', '', text)
    text = re.sub(r'\)$', '', text)
    
    # Split text by commas and attach the base URL to each requirement
    base_url = "https://selfservice.camdencc.edu/Student/Courses/Search?requirement="
    prerequisites = [f"{base_url}{req.strip()}" for req in text.split(",") if req.strip()]
    
    # Join them back with a pipe "|"
    return "|".join(prerequisites)


# Load the JSON file (assumes the file contains a JSON array of course objects)
input_file = r"C:\text\NJ\Camden\courses\all_courses.json"
with open(input_file, "r", encoding="utf-8") as f:
    courses = json.load(f)

# Create a DataFrame from the JSON list.
df = pd.DataFrame(courses)
print("Available Columns:", df.columns.tolist())

# Define the output CSV columns.
output_columns = [
    "CTID", "External Identifier", "Coded Notation", "Learning Type", "Learning Opportunity Name",
    "Description", "Language", "Life Cycle Status Type", "Subject Webpage", "Credit Unit Value",
    "Credit Unit Max Value", "Credit Unit Type", "Credit Unit Type Description", "Is Non-Credit", "Date Effective", 
    "Version Identifier", "Prerequisite"
]

output_data = []

for index, row in df.iterrows():
    # Use the course "Id" as the external identifier.
    external_identifier = row.get("Id", "")
    
    # Construct "Coded Notation" from SubjectCode and Number.
    subject_code = row.get("SubjectCode", "").strip() if pd.notna(row.get("SubjectCode", "")) else ""
    if subject_code =="PSE":
        continue
    number = str(row.get("Number", "")).strip() if pd.notna(row.get("Number", "")) else ""
    coded_notation = f"{subject_code}-{number}" if subject_code and number else ""
    
    # Learning Opportunity Name: combine the coded notation and the Title.
    title = row.get("Title", "").strip() if pd.notna(row.get("Title", "")) else ""
    learning_opportunity_name = f"{coded_notation} {title}".strip() if coded_notation else title
    
    # Use the Description field if available.
    description = row.get("Description", "").strip() if pd.notna(row.get("Description", "")) else "No description available"
    
    # Assume courses are in English.
    language = "English"
    
    # Default Life Cycle Status; adjust if you have specific data.
    life_cycle_status_type = "Active"
    
    # Build a link that uses the SubjectCode and Number.
    in_catalog = f"https://selfservice.camdencc.edu/Student/Courses/Search?keyword={subject_code}-{number}" if subject_code and number else ""
    
    # Process credit values.
    credit_unit_value = row.get("MinimumCredits")
    credit_unit_max_value = row.get("MaximumCredits")
    
    if pd.notna(credit_unit_value) and credit_unit_value != 0:
        credit_unit_type = "Credit Hours"
        credit_unit_type_description = "SemesterHour"
        noncredit = ""
    else:
        credit_unit_value = ""
        credit_unit_max_value = ""
        credit_unit_type = ""
        credit_unit_type_description = ""
        noncredit = "TRUE"
    
    # "Date Effective" is not provided in the JSON; leave it blank.
    date_effective = ""
    
    # Version Identifier as specified.
    version_identifier = "2024-2025 Catalog"
    
    # Process prerequisites from the "Requisites" field.
    prereqs = row.get("Requisites", [])
    if isinstance(prereqs, list) and len(prereqs) > 0:
        prereq_list = []
        for req in prereqs:
            if isinstance(req, dict):
                # Use "DisplayText" if available; otherwise, use "RequirementCode".
                if "DisplayText" in req and req["DisplayText"]:
                    prereq_list.append(req["DisplayText"])
                elif "RequirementCode" in req and req["RequirementCode"]:
                    prereq_list.append(req["RequirementCode"])
        prerequisite = ", ".join(prereq_list)
        prerequisite = clean_prerequisite(prerequisite)
    else:
        prerequisite = ""

    # Append the processed row to the output list.
    output_data.append([
        generate_ctid(),
        external_identifier,
        coded_notation,
        "Course",
        learning_opportunity_name,
        description,
        language,
        life_cycle_status_type,
        in_catalog,
        credit_unit_value,
        credit_unit_max_value,
        credit_unit_type,
        credit_unit_type_description,
        noncredit,
        date_effective,
        version_identifier,
        prerequisite
    ])

# Convert the output list to a DataFrame.
output_df = pd.DataFrame(output_data, columns=output_columns)

# Save the DataFrame to a CSV file.
output_file = "Camden_BU_Credit_Courses.csv"
output_df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"Conversion complete. Output saved to {output_file}")
