import pandas as pd
import os
import json
import uuid

# Generate a unique CTID
def generate_ctid():
    return f"ce-{uuid.uuid4()}"

import re

def update_variable_code(old_value):
    # Regular expression to capture the alphanumeric course code before the space
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

                        if 'FormattedMeetingTimes' in section:
                            for meeting in section['FormattedMeetingTimes']:
                                details_data = {
                                    "DaysOfWeek": meeting.get('DaysOfWeekDisplay', ''),
                                    "StartTime": meeting.get('StartTimeDisplay', ''),
                                    "EndTime": meeting.get('EndTimeDisplay', ''),
                                    "InstructionMethod": meeting.get('InstructionalMethodDisplay', ''),
                                    "Building": meeting.get('BuildingDisplay', ''),
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
                                    "Location": location
                                    online = ""
                                    delivery = "In-Person"
                                    if meeting.get('BuildingDisplay', '') == "Online":
                                        delivery ="Online Only"
                                    if meeting.get('BuildingDisplay', '') == "Online" and "CENG" in code:
                                        online = "https://workforce.atlanticcape.edu/personal-enrichment/health-wellness.php"
                                    if meeting.get('BuildingDisplay', '') == "Online" and "PENG" in code:
                                        online = "https://workforce.atlanticcape.edu/professional-development/cannabis.php"
                                }
                                all_details_data.append(details_data)

                        # Mapping bulk upload CSV fields
                        bulk_data = {
                            "CTID": generate_ctid(),
                            "Internal Identifier": section_name,
                            "External Identifier": section_name,
                            "Learning Type": "Course",
                            "Available Online At": online,
                            "Delivery Type": "In-Person",
                            "Delivery Type Description": "On-Campus Learning",
                            "Learning Opportunity Name": code +" - "+ section_title,
                            "Description": course_description,
                            "Subject Webpage": "https://workforce.atlanticcape.edu",
                            "Life Cycle Status Type": "Active",
                            "Language": "English",
                            "Coded Notation": code,
                            "Is Non-Credit": "TRUE",
                            "Keywords": "",
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
bulk_csv_path = r"C:\text\NJ\Atlantic Cape\noncredit\noncreditBulkUpload2.csv"

# Run the function
process_json_files(directory_path, details_csv_path, bulk_csv_path)
