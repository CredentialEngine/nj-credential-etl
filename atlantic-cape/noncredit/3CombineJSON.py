import pandas as pd
import os
import json

def combine_json_files_to_csv(directory_path, output_csv_path):
    all_data = []  # List to store data from all JSON files
    
    # Loop through every file in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)
            
            # Load JSON file
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                # Check if 'Sections' key is in the data
                if 'Sections' in data:
                    # Attempt to normalize the 'Sections' part of the JSON
                    try:
                        df = pd.json_normalize(
                            data['Sections'],
                            record_path='FormattedMeetingTimes',
                            meta=[
                                'CourseDescription',
                                'FacultyDisplay',
                                'AvailabilityDisplay',
                                'AvailabilityTooltip',
                                ['FullTitleDisplay'],
                                ['SectionNameDisplay'],
                                ['SectionTitleDisplay'],
                                ['StartDateDisplay'],
                                ['EndDateDisplay'],
                                ['LocationDisplay'],
                                'FormattedMeetingTimes.DaysOfWeekDisplay',
                                'FormattedMeetingTimes.StartTimeDisplay',
                                'FormattedMeetingTimes.EndTimeDisplay',
                                'FormattedMeetingTimes.InstructionalMethodDisplay',
                                'FormattedMeetingTimes.BuildingDisplay',
                                'FormattedMeetingTimes.RoomDisplay',
                                'FormattedMeetingTimes.DatesDisplay'
                            ],
                            errors='ignore'
                        )
                        all_data.append(df)
                    except Exception as e:
                        print(f"Error processing file {filename}: {e}")
    
    # Concatenate all DataFrames into a single DataFrame
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Save the combined DataFrame to a CSV file
    combined_df.to_csv(output_csv_path, index=False)
    print(f"Combined data saved to {output_csv_path}")

# Directory containing the JSON files
directory_path = r"C:\text\NJ\Atlantic Cape\noncredit\noncreditHTML"

# Path for the output CSV file
output_csv_path = r"C:\text\NJ\Atlantic Cape\noncredit\noncreditJSON.csv"

# Call the function
combine_json_files_to_csv(directory_path, output_csv_path)
