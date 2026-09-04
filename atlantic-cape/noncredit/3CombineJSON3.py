import pandas as pd
import os
import json
import uuid
import re

# Generate a unique CTID
def generate_ctid():
    return f"ce-{uuid.uuid4()}"

# Function to extract course code from section name
def update_variable_code(old_value):
    match = re.match(r"([A-Z]+-\d+)", old_value)
    return match.group(1) if match else old_value  # Return extracted value or original if no match

def process_json_files(directory_path, details_csv_path, bulk_csv_path):
    all_details_data = []
    all_bulk_data = []

    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)

            with open(file_path, 'r', encoding='utf-8-sig') as file:
                data = json.load(file)

                if 'Sections' in data:
                    for section in data['Sections']:
                        course_description = section.get('CourseDescription', '')
                        faculty_display = section.get('FacultyDisplay', '')
                        availability_display = section.get('AvailabilityDisplay', '')
                        full_title = section.get('FullTitleDisplay', '')
                        section_name = section.get('SectionNameDisplay', '')
                        section_title = section.get('SectionTitleDisplay', '')
                        start_date = section.get('StartDateDisplay', '')
                        end_date = section.get('EndDateDisplay', '')
                        location = section.get('LocationDisplay', '')
                        code = update_variable_code(section_name)

                        # Default values for online link and delivery type
                        online = ""
                        delivery = "In-Person"

                        if 'FormattedMeetingTimes' in section:
                            for meeting in section['FormattedMeetingTimes']:
                                building_display = meeting.get('BuildingDisplay', '')

                                # Update delivery type based on building
                                if building_display == "Online":
                                    delivery = "Online Only"

                                    # Update online course link based on course code
                                    if "CEGN" in code:
                                        online = "https://workforce.atlanticcape.edu/personal-enrichment/health-wellness.php"
                                    elif "PDEV" in code:
                                        online = "https://workforce.atlanticcape.edu/professional-development/cannabis.php"

                                # Course details data collection
                                details_data = {
                                    "DaysOfWeek": meeting.get('DaysOfWeekDisplay', ''),
                                    "StartTime": meeting.get('StartTimeDisplay', ''),
                                    "EndTime": meeting.get('EndTimeDisplay', ''),
                                    "InstructionMethod": meeting.get('InstructionalMethodDisplay', ''),
                                    "Building": building_display,
                                    "Room": meeting.get('RoomDisplay', ''),
                                    "Dates": meeting.get('DatesDisplay', ''),
                                    "CourseDescription": course_description,
                                    "Faculty": faculty_display,
                                    "Availability": availability_display,
                                    "FullTitle": full_title,
                                    "SectionName": section_name,
                                    "SectionTitle": section_title,
                                    "StartDate": start_date,
                                    "EndDate": end_date,
                                    "Location": location,
                                    "Delivery": delivery,
                                    "OnlineLink": online
                                }
                                all_details_data.append(details_data)

                        # Mapping bulk upload CSV fields
                        bulk_data = {
                            "CTID": generate_ctid(),
                            "External Identifier": section_name,
                            "Learning Type": "Course",
                            "Available Online At": online,
                            "Delivery Type": delivery,
                            "Learning Opportunity Name": f"{code} - {section_title}",
                            "Description": course_description,
                            "Subject Webpage": "https://workforce.atlanticcape.edu",
                            "Life Cycle Status Type": "Active",
                            "Language": "English",
                            "Coded Notation": code,
                            "Is Non-Credit": "TRUE",
                            "Version Identifier": "2024-2025 Catalog",
                            "Learning Method Type": "Lecture"
                        }
                        all_bulk_data.append(bulk_data)

    # Convert to DataFrame and save CSVs
    details_df = pd.DataFrame(all_details_data)
    bulk_df = pd.DataFrame(all_bulk_data)

    details_df.to_csv(details_csv_path, index=False)
    bulk_df.to_csv(bulk_csv_path, index=False)

    print(f"Course details saved to {details_csv_path}")
    print(f"Bulk course upload saved to {bulk_csv_path}")

# Define file paths
directory_path = r"C:\text\NJ\Atlantic Cape\noncredit\noncreditHTML"
details_csv_path = r"C:\text\NJ\Atlantic Cape\noncredit\noncreditJSON2.csv"
bulk_csv_path = r"C:\text\NJ\Atlantic Cape\noncredit\Atlantic_BU_Noncredit_Courses.csv"

# Run the function
process_json_files(directory_path, details_csv_path, bulk_csv_path)
