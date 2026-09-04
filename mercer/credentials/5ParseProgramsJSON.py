import json
import csv
#https://coursedogcurriculum.docs.apiary.io/#reference/programs/get-all-programs
#Save this JSON first
#https://app.coursedog.com/api/v1/cm/mercercounty_colleague/programs?list=&includeDependents=&formatDependents=&includePending=false&ignoreEffectiveDating=false&effectiveDatesRange=&limit=&skip=&orderBy=&orderDirection=ascending

def json_to_csv(json_file, csv_file):
    try:
        # Open and load the JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Flatten the JSON data into a list of dictionaries
        rows = []
        for key, program in data.items():
            # Safely access degreeMaps and related fields
            degree_maps = program.get('degreeMaps', [])
            degree_map_narrative = degree_maps[0].get('degreeMapNarrative', '').replace('\n', ' ') if degree_maps else ''
            if program.get('status', '') == "Inactive":
                next
            else:
                if program.get('catalogDisplayName', '') == '':
                    row = {
                        'ID': program.get('_id', ''),
                        'Program Title': program.get('name', ''),
                        'catalogDisplayName': program.get('catalogDisplayName', ''),
                        'catalogDescription': program.get('catalogDescription', ''),
                        'Program Code': program.get('code', '').rsplit('.', 1)[1],
                        'Name': program.get('name', ''),
                        'Program Description': program.get('description', ''),
                        'Program Outcomes': degree_map_narrative,
                        'Status': program.get('status', ''),
                        'Start Date': program.get('effectiveStartDate', ''),
                        'End Date': program.get('effectiveEndDate', ''),
                    }
                    rows.append(row)
                else:
                    '''parts = program.get('code2', '').rsplit('.', 1)
                    code = {'Code': parts[1]}
                    rows.append(code2)'''
                    row = {
                        'ID': program.get('_id', ''),
                        'Program Title': program.get('name', ''),
                        'catalogDisplayName': program.get('catalogDisplayName', ''),
                        'catalogDescription': program.get('catalogDescription', ''),
                        'Program Code': program.get('code', ''),
                        'Name': program.get('catalogDisplayName', '')+": "+program.get('catalogDescription', ''),
                        'Program Description': program.get('description', ''),
                        'Program Outcomes': degree_map_narrative,
                        'Status': program.get('status', ''),
                        'Start Date': program.get('effectiveStartDate', ''),
                        'End Date': program.get('effectiveEndDate', ''),
                    }
                    rows.append(row)
        
        # Write to CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = rows[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"CSV file '{csv_file}' created successfully.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# File paths
json_file = 'programs.json'  # Update with the correct path
csv_file = 'programs_output.csv'

# Convert JSON to CSV
json_to_csv(json_file, csv_file)
