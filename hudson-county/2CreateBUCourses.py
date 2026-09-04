import pandas as pd
import uuid
import re

def generate_ctid():
    return "ce-" + str(uuid.uuid4())

def clean_prerequisite(text):
    """
    Splits the prerequisite text by commas, strips extra characters,
    prepends the base URL to each item, and then joins them using a pipe.
    """
    # Remove any leading "s:" or ":" and trailing ")" from the entire text.
    text = re.sub(r'^\s*s:\s*|\s*:\s*', '', text)
    text = re.sub(r'\)$', '', text)
    
    base_url = ""
    # Split the text by comma, trim each item, and attach the URL
    prerequisites = [f"{base_url}{req.strip()}" for req in text.split(",") if req.strip()]
    # Join the individual URLs with a pipe separator.
    return " | ".join(prerequisites)

# Input CSV file with the example header
input_file = r"C:\text\NJ\Hudson County\courses_parsed.csv"  # Update to your file path

# Read CSV (assuming comma-delimited; adjust encoding if needed)
df = pd.read_csv(input_file, encoding="utf-8-sig")
print("Available Columns:", df.columns.tolist())

# Define the output columns
output_columns = [
    "CTID", "External Identifier", "Coded Notation", "Learning Type", "Learning Opportunity Name",
    "Description", "Language", "Life Cycle Status Type", "Subject Webpage", "Credit Unit Value",
    "Credit Unit Type", "Credit Unit Type Description", "Version Identifier"
]

output_data = []

for _, row in df.iterrows():
    # Use course_number for both External Identifier and Coded Notation.
    external_identifier = row["course_number"].strip() if pd.notna(row["course_number"]) else ""
    coded_notation = external_identifier
    
    # Learning Opportunity Name: course_number and course_title.
    course_title = row["course_title"].strip() if pd.notna(row["course_title"]) else ""
    learning_opportunity_name = f"{coded_notation} - {course_title}" if coded_notation else course_title

    # Description: use course_description.
    description = row["course_description"].strip() if pd.notna(row["course_description"]) else "No description available"
    
    # Language is assumed to be English.
    language = "English"
    
    # Life Cycle Status Type: default to "Active"
    life_cycle_status_type = "Active"
    
    # In Catalog: use the provided URL.
    in_catalog = row["course_number_url"].strip() if pd.notna(row["course_number_url"]) else ""
    
    # Parse credits from course_credits (e.g., "3 Credits")
    credit_text = row["course_credits"].strip() if pd.notna(row["course_credits"]) else ""
    credit_match = re.search(r'(\d+(\.\d+)?)', credit_text)
    if credit_match:
        credit_value = float(credit_match.group(1))
        credit_unit_value = credit_value
        credit_unit_max_value = credit_value
        credit_unit_type = "Credit Hours"
        credit_unit_type_description = "SemesterHour"
        noncredit = ""
    else:
        credit_unit_value = ""
        credit_unit_max_value = ""
        credit_unit_type = "Unknown"
        credit_unit_type_description = ""
        noncredit = "TRUE"
    
    # Date Effective not provided in the CSV; leave as empty string.
    date_effective = ""
    
    # Version Identifier hardcoded as desired.
    version_identifier = "2024-2025 Catalog"
    
    # Prerequisite: if you have a field you can process it using clean_prerequisite.
    # In this example, prerequisites are not provided so we set it to an empty string.
    prerequisite = ""
    # Example (if the CSV had a 'course_prerequisites' column):
    # if pd.notna(row.get("course_prerequisites", "")):
    #     prerequisite = clean_prerequisite(row["course_prerequisites"])
    
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
        #credit_unit_max_value,
        credit_unit_type,
        credit_unit_type_description,
        #noncredit,
        #date_effective,
        version_identifier
        #prerequisite
    ])

# Convert the output list into a DataFrame with the desired columns.
output_df = pd.DataFrame(output_data, columns=output_columns)

# Save the DataFrame to a CSV file.
output_file = "Hudson_BU_Credit_Courses.csv"
output_df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"Conversion complete. Output saved to {output_file}")
