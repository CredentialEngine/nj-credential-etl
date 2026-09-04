import pandas as pd
import uuid

# Generate a unique CTID
def generate_ctid():
    return f"ce-{uuid.uuid4()}"

def process_course_details(input_csv, output_csv):
    # Read the input CSV file
    df = pd.read_csv(input_csv, encoding="utf-8-sig")

    # Mapping headers from course_details.csv to bulk upload format
    mapped_data = []
    for _, row in df.iterrows():
        online = ""
        delivery = "In-Person"
        if "online" in row.get("Type", "Lecture").lower():
            online = "https://www.brookdalecc.edu/continuinged/"
            delivery = "OnlineOnly"
        bulk_data = {
            "CTID": generate_ctid(),
            "External Identifier": row.get("Course ID", ""),
            "Learning Type": "Course",
            "Available Online At": online,
            "Delivery Type": delivery,  # Default to in-person
            "Learning Opportunity Name": row.get("Title", ""),
            #"Learning Opportunity Name": row.get("Title", "")[5:] if len(row.get("Title", "")) > 5 else row.get("Title", ""),
            "Description": row.get("Description", ""),
            "Subject Webpage": "https://ce.brookdalecc.edu/search/publicCourseSearchDetails.do?method=load&courseId="+str(row.get("Course ID", "")),
            "Life Cycle Status Type": "Active",
            "Language": "English",
            "Coded Notation": row.get("Title", "")[:4],
            "Is Non-Credit": "TRUE",
            "Version Identifier": "2024-2025 Catalog",
            #"Learning Method Type": row.get("Type", "Lecture"),  # Default to "Lecture"
            "Cost: External Identifier": row.get("Course ID", ""),
            "Cost: Description": "Tuition for Brookdale continuing education course.",
            "Cost: Currency Type": "USD",
            "Cost: Types List": "tuition~"+row.get("Fee", "").replace("$",""),
            "Cost: Details Url": "https://ce.brookdalecc.edu/search/publicCourseSearchDetails.do?method=load&courseId="+str(row.get("Course ID", "")),
            #"Location": row.get("Location", ""),
            "Credit Unit Type": "ContactHour",
            #"Credit Unit Value": row.get("CEUs", ""),
            "Credit Unit Value": row.get("Contact Hours", ""),
            #"Credential Connections": row.get("Credential Connections", ""),
        }
        mapped_data.append(bulk_data)

    # Convert the list to a DataFrame and save as CSV
    bulk_df = pd.DataFrame(mapped_data)
    bulk_df.to_csv(output_csv, index=False, encoding="utf-8-sig")

    print(f"Bulk upload CSV saved to {output_csv}")

# Define file paths
input_csv = r"C:\text\NJ\Brookdale\noncredit\course\course_details.csv"
output_csv = r"C:\text\NJ\Brookdale\noncredit\course\Brookdale_BU_Noncredit_Courses.csv"

# Run the function
process_course_details(input_csv, output_csv)
