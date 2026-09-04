import pandas as pd
import uuid
import re

def generate_ctid():
    return "ce-"+str(uuid.uuid4())
    

def clean_prerequisite(text):
    # Remove leading 's:' or ':'
    text = re.sub(r'^\s*s:\s*|\s*:\s*', '', text)
    # Remove trailing ')' if present
    text = re.sub(r'\)$', '', text)
    return text.strip()

# Load CSV with proper delimiter & encoding
input_file = r"C:\text\NJ\Rowan College at Burlington\2026\credit\rcbc_courses_all.csv"  # Change to your actual file path
df = pd.read_csv(input_file, delimiter=",", encoding="utf-8")

# Debug: Print available columns
print("Available Columns:", df.columns.tolist())

# Strip column names of extra spaces
df.columns = df.columns.str.strip()

# Verify if 'courseGroupId' exists after cleaning
if "courseGroupId" not in df.columns:
    raise KeyError("Column 'courseGroupId' not found. Please check the input file formatting.")


# Define the output columns
output_columns = [
    "CTID","External Identifier", "Coded Notation", "Learning Type", "Learning Opportunity Name",
    "Description", "Language", "Life Cycle Status Type", "Subject Webpage", "Credit Unit Value",
    "Credit Unit Max Value", "Credit Unit Type", "Credit Unit Type Description", "Is Non-Credit", "Date Effective", 
    "Version Identifier", "Prerequisite"
]

# Initialize output DataFrame
output_data = []

# Process each row
for _, row in df.iterrows():
    external_identifier = row["id"]
    coded_notation = row["courseGroupId"] if pd.notna(row["courseGroupId"]) else "Unknown"
    learning_opportunity_name = f"{row['courseGroupId']} - {row['longName']}" if pd.notna(row['courseGroupId']) and pd.notna(row['longName']) else row['longName']
    description = row["description"] if pd.notna(row["description"]) else "No description available"
    language = "English"  # Assuming English as default language
    life_cycle_status_type = row["status"] if pd.notna(row["status"]) else "Unknown"
    linkcourseGroupId = row['courseGroupId'].replace("/","%2F")
    in_catalog = f"https://catalog.rcbc.edu/courses/{linkcourseGroupId}" if pd.notna(row["courseGroupId"]) else "N/A"
    date_effective = row["effectiveStartDate"]


    # Extract credit values from flattened columns
    credit_unit_value = ""
    credit_unit_max_value = ""
    credit_unit_type_description = ""
    noncredit = ""
    credit_unit_type = "Unknown"

    def clean_cell(value):
        if pd.isna(value) or value == "":
            return ""
        return str(value).strip()

    def to_number(value):
        if value == "":
            return ""
        try:
            num = float(value)
            return int(num) if num.is_integer() else num
        except (TypeError, ValueError):
            return value

    credit_min_raw = clean_cell(row.get("credits.creditHours.min", ""))
    credit_max_raw = clean_cell(row.get("credits.creditHours.max", ""))
    credit_operator = clean_cell(row.get("credits.creditHours.operator", ""))

    credit_min = to_number(credit_min_raw)
    credit_max = to_number(credit_max_raw)

    if credit_min != "":
        credit_unit_type_description = "SemesterHour"
        credit_unit_value = credit_min

    if credit_max != "":
        credit_unit_max_value = credit_max

    if credit_min != "" or credit_max != "":
        credit_unit_type = "Credit Hours" if credit_operator == "" else "Variable Credit"

    if credit_unit_value in [0, "0"]:
        credit_unit_value = ""
        credit_unit_max_value = ""
        credit_unit_type = ""
        credit_unit_type_description = ""
        noncredit = "TRUE"
    
    # Text Verification details (Assumption: all required fields are present)
    text_verification_details = """course_id: Present
course_name: Present
course_credits_max: Present
course_credits_min: Present
course_description: Present
course_prerequisites: Present"""

    condition_profile_external_identifier = ""
    condition_profile_type = ""
    condition_profile_name = ""
    condition_profile_description = ""
    # Condition Profile (Placeholder, need actual prerequisites data)
    if "(Prerequisite" in description:
        condition_profile_external_identifier = coded_notation
        condition_profile_type = "Requires"
        condition_profile_name = "Prerequisites"
        condition_profile_description = description.split("(Prerequisite")[1]
        condition_profile_description = clean_prerequisite(condition_profile_description)

    
    # Append row to output
    output_data.append([
        generate_ctid(), external_identifier, coded_notation, "Course", learning_opportunity_name, description, language,
        life_cycle_status_type, in_catalog, credit_unit_value, credit_unit_max_value, credit_unit_type, 
        credit_unit_type_description, noncredit, date_effective, "2025-2026 Catalog",
        condition_profile_description
    ])

# Convert output data to DataFrame
output_df = pd.DataFrame(output_data, columns=output_columns)

# Save to CSV
output_file = "RCBC_BU_Credit_Courses_2026.csv"
output_df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"Conversion complete. Output saved to {output_file}")
