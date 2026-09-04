import pandas as pd
import uuid
import re
import json

def generate_ctid():
    return "ce-" + str(uuid.uuid4())

def extract_cost_variant(onclick_data):
    """Extracts cost and variant info from Onclick Data column using regex."""
    try:
        # Extract the JSON-like object inside publishAnalyticsEvent({...})
        json_match = re.search(r'publishAnalyticsEvent\((\{.*\})\)\.catch', onclick_data, re.DOTALL)
        if json_match:
            json_data = json_match.group(1)
            # Convert JSON-like string to dictionary
            json_dict = json.loads(json_data)
            
            # Navigate to the "products" list
            products = json_dict.get("ecommerce", {}).get("click", {}).get("products", [])
            if products and isinstance(products, list):
                product = products[0]  # Assuming first product entry
                cost = "tuition~" + str(product.get("price", None))
                variant = product.get("variant", None)
                code = product.get("id", None)
                return cost, variant, code
    except Exception as e:
        print(f"Error extracting from Onclick Data: {e}")
    return None, None, None

# Load CSV file
input_file = r"C:\text\NJ\Hudson County\noncredit\ed2go\course_details.csv"
df = pd.read_csv(input_file, delimiter=",", encoding="utf-8")

# Strip column names to remove unwanted spaces
df.columns = df.columns.str.strip()

# Debug: Print available columns
print("Available Columns:", df.columns.tolist())

# Define output CSV columns
output_columns = [
    "CTID", "External Identifier", "Coded Notation", "Learning Type", "Learning Opportunity Name",
    "Description", "Language", "Life Cycle Status Type", "Subject Webpage", "Is Non-Credit", "Version Identifier", 
    "Cost: External Identifier", "Cost: Description", "Cost: Currency Type", "Cost: Types List", "Cost: Details Url",
    "Delivery Type", "Learning Method Type"
]

# Initialize output data storage
output_data = []

# Process each row
for _, row in df.iterrows():
    external_identifier = row["Course URL"].split("/")[-2] if pd.notna(row["Course URL"]) else ""
    coded_notation = row["Course Name"] if pd.notna(row["Course Name"]) else ""
    learning_opportunity_name = f"{row['Course Name']}" if pd.notna(coded_notation) else row["Course Name"]
    description = row["Description"] if pd.notna(row["Description"]) else ""
    language = "English"  # Default assumption
    life_cycle_status_type = "Active"
    subject_webpage = row["Course URL"] if pd.notna(row["Course URL"]) else ""
    noncredit = "TRUE"
    version_identifier = "2024-2025 Catalog"
    delivery_type = "OnlineOnly"  # Ed2Go courses are assumed online by default

    # Extract cost and variant from Onclick Data column
    cost, variant, code = extract_cost_variant(row["Onclick Data"]) if pd.notna(row["Onclick Data"]) else (None, None)
    if variant == "Instructor-led":
        variant = "Cohort-Based"
    if variant == "Self-paced":
        variant = "SelfPaced"

    # Append row to output
    output_data.append([
        generate_ctid(), external_identifier, code, "Course", learning_opportunity_name,
        description, language, life_cycle_status_type, subject_webpage, noncredit, version_identifier, 
        code,"Tuition for " +str(learning_opportunity_name), "USD", cost if cost else "Unknown", subject_webpage,
        delivery_type, variant
    ])

# Convert output data to DataFrame
output_df = pd.DataFrame(output_data, columns=output_columns)

# Save output CSV
output_file = r"C:\text\NJ\Hudson County\noncredit\ed2go\Hudson_BU_NonCredit_ed2go_Courses.csv"
output_df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"Conversion complete. Output saved to {output_file}")
