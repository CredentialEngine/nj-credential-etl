import pandas as pd
import json
import re
from bs4 import BeautifulSoup
import csv
import uuid
from datetime import datetime


# https://coursedogcurriculum.docs.apiary.io/#reference/programs/get-all-programs
# Save this JSON first:
# https://app.coursedog.com/api/v1/cm/mercercounty_colleague/programs?list=&includeDependents=&formatDependents=&includePending=false&ignoreEffectiveDating=false&effectiveDatesRange=&limit=&skip=&orderBy=&orderDirection=ascending

def map_type(type_):
    type_mapping = {
        "Asociate in Applied Science": "AssociateOfAppliedScienceDegree",
        "Associate in Applied Science": "AssociateOfAppliedScienceDegree",
        "Associate in Applied Science ": "AssociateOfAppliedScienceDegree",
        "Associate in Arts": "AssociateOfArtsDegree",
        "Associate in Arts - Communication": "AssociateOfArtsDegree",
        "Associate in Arts - Liberal Arts": "AssociateOfArtsDegree",
        "Associate in Fine Arts": "AssociateOfArtsDegree",
        "Associate in Fine Arts ": "AssociateOfArtsDegree",
        "Associate in Fine Arts - Visual Arts": "AssociateOfArtsDegree",
        "Associate in Fine Arts-Visual Arts": "AssociateOfArtsDegree",
        "Associate in Science": "AssociateOfScienceDegree",
        "Associate in Science ": "AssociateOfScienceDegree",
        "Cert of Achievement": "Certificate",
        "Certificate of Achievement": "Certificate",
        "Certificate of Achievement ": "Certificate",
        "Certificate of Proficency": "Certificate",
        "Certificate of Proficiency": "Certificate",
        "Certificate of Proficiency ": "Certificate",
        "Certificate of Proficiency - 24": "Certificate",
        "Certificate of Proficiency - 26": "Certificate",
        "Certificate of Proficiency - 26": "Certificate",
        "CRIM": "AssociateOfScienceDegree",
        "HLTH": "AssociateOfAppliedScienceDegree",
        "NC": "Certificate",
        "NONDEG": "Certificate",
    }
    # Default to original type if not in dictionary
    return type_mapping.get(type_.strip(), type_)


def json_to_csv(json_file, csv_file):
    try:
        # Open and load the JSON file
        with open(json_file, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
            competency_data = [] # List for competency framework and competencies
        
        # Flatten the JSON data into a list of dictionaries
        rows = []
        for key, program in data.items():
            # Skip inactive programs
            if program.get('status', '') == "Inactive":
                continue

            # Safely access degreeMaps and related fields
            degree_maps = program.get('degreeMaps', [])
            degree_map_narrative = degree_maps[0].get('degreeMapNarrative', '') if degree_maps else ''
            
            custom = program.get('customFields',[])
            estimatedMonths = str(custom.get('acpgCmplMonths', ''))+" Months"
            approvalDate = custom.get('acpgApprovalDates', '')
            academicDegree = custom.get('academicDegree', '')
            statusDate = custom.get('acpgStatusDate', '')
            # Convert to datetime object
            statusDate = datetime.strptime(statusDate, "%Y-%m-%d").strftime("%m-%d-%Y")
            hours = custom.get('lVPZO', '')

            
            # Get the full program code from the JSON
            program_code_full = program.get('code', '')
            # Extract the text up to the first period for the Type column
            first_type_value = program_code_full.split('.')[0] if '.' in program_code_full else program_code_full
            # Extract the text after the last period for the Type column
            last_type_value = program_code_full.rsplit('.', 1)[-1] if '.' in program_code_full else program_code_full
            if last_type_value == "ONLINE":
                online = "OnlineOnly"
            #Type logi
            if program.get('catalogDescription', '') == '':
                type_ = map_type(first_type_value)
            else:
                type_ = map_type(program.get('catalogDescription', ''))
            
            # Parse the HTML content.
            soup = BeautifulSoup(degree_map_narrative, 'html.parser')
            # Find the <strong> tag containing "PROGRAM OUTCOMES" (case-insensitive).
            strong_tag = soup.find('strong', string=lambda text: text and "PROGRAM OUTCOMES" in text.upper())

            outcomes = []
            framework_id = ''
            online =''

            if strong_tag:
                # Iterate over all tags after the <strong> tag
                for tag in strong_tag.find_all_next():
                    if tag.name == 'p':
                        text = tag.get_text()
                        # Remove any leading whitespace
                        stripped_text = text.lstrip()
                        # Only include the outcome if it starts with a bullet
                        if stripped_text.startswith('•'):
                            # Remove the bullet and extra whitespace
                            cleaned = stripped_text.lstrip('•').strip()
                            if cleaned:
                                # Ensure the statement begins with a capital letter
                                cleaned = cleaned[0].upper() + cleaned[1:]
                                # Remove any trailing semicolon or comma
                                cleaned = cleaned.rstrip(';, ')
                                # Ensure the statement ends with a period
                                if not cleaned.endswith('.'):
                                    cleaned += '.'
                                outcomes.append(cleaned)
                        else:
                            break
            #Assign the name here.
            if program.get('catalogDisplayName', '') == '':
                name = program.get('name', '')
            else:
                name = program.get('catalogDisplayName', '') + ": " + program.get('catalogDescription', '')
            # Generate a unique framework ID for this program's competencies
            if outcomes:
                framework_id = 'ce-' + str(uuid.uuid4())
            
            description = program.get('description', '')
            # Remove everything after "PROGRAM OUTCOMES"
            #description = description.split("PROGRAM OUTCOMES")[0].strip()
            description = re.split(r'(?i)PROGRAM OUTCOMES', description)[0].strip()
            # Replace multiple consecutive newlines with a single newline
            description = re.sub(r'\n+', '\n', description)
            if description == '':
                description = "Mercer County Community College " + program.get('name', '') + " program."

            if program.get('catalogDisplayName', '') == '':
                # In this branch, Program Code is taken as the text after the last period.
                code_value = program_code_full.rsplit('.', 1)[1] if '.' in program_code_full else program_code_full
                row = {
                    'ID': program.get('_id', ''),
                    'Program Title': program.get('name', ''),
                    'catalogDisplayName': program.get('catalogDisplayName', ''),
                    'catalogDescription': program.get('catalogDescription', ''),
                    'Program Code': code_value,
                    'URL': 'https://catalog.mccc.edu/programs/' + code_value,
                    'Type': type_,
                    'Online': online,
                    'CIP': program.get('cipCode', ''),
                    'Version': program.get('version', ''),
                    'Approval Date': approvalDate,
                    'Status Date': statusDate,
                    'Academic Degree': academicDegree,
                    'EstimatedMonths': estimatedMonths,
                    'Name': program.get('name', ''),
                    'Description': description,
                    'Program Outcomes': outcomes,
                    'Outcomes': framework_id,
                    'Hours': hours,
                    'Status': program.get('status', ''),
                    'Start Date': program.get('effectiveStartDate', ''),
                    'End Date': program.get('effectiveEndDate', ''),
                }
                rows.append(row)
                #Do the outcome work here.
                if outcomes:
                    # ----- Build competency data for this file -----
                    # Competency framework entry
                    competency_framework_entry = {
                        "ceasn:comment": name,
                        "@id": framework_id,
                        "@type": "ceasn:CompetencyFramework",
                        "ceasn:description": "Upon completion of this program students will be able to:",
                        "ceasn:inLanguage": "en",
                        "ceasn:name": f"{name}'s Program Learning Outcomes",
                        "ceasn:publicationStatusType": "http://credreg.net/ctdlasn/vocabs/publicationStatus/Published",
                        "ceasn:source": 'https://catalog.mccc.edu/programs/' + code_value
                    }
                    competency_data.append(competency_framework_entry)

                    # Append each outcome as a separate competency entry
                    for outcome in outcomes:
                        competency_entry = {
                            "@id": 'ce-' + str(uuid.uuid4()),
                            "@type": "ceasn:Competency",
                            "ceasn:inLanguage": "en",
                            "ceasn:competencyLabel": "Program Learning Outcome",
                            "ceasn:competencyText": outcome,
                            "ceasn:isPartOf": framework_id
                        }
                        competency_data.append(competency_entry)
            else:
                # In this branch, the full Program Code is used.
                row = {
                    'ID': program.get('_id', ''),
                    'Program Title': program.get('name', ''),
                    'catalogDisplayName': program.get('catalogDisplayName', ''),
                    'catalogDescription': program.get('catalogDescription', ''),
                    'Program Code': program_code_full,
                    'URL': 'https://catalog.mccc.edu/programs/' + program_code_full,
                    'Type': type_,
                    'Online': online,
                    'CIP': program.get('cipCode', ''),
                    'Version':program.get('version', ''),
                    'Approval Date': approvalDate,
                    'Status Date': statusDate,
                    'Academic Degree': academicDegree,
                    'EstimatedMonths': estimatedMonths,
                    'Name': program.get('catalogDisplayName', '') + ": " + program.get('catalogDescription', ''),
                    'Description': description,
                    'Program Outcomes': outcomes,
                    'Outcomes': framework_id,
                    'Hours': hours,
                    'Status': program.get('status', ''),
                    'Start Date': program.get('effectiveStartDate', ''),
                    'End Date': program.get('effectiveEndDate', ''),
                }
                rows.append(row)
                #Do the outcome work here.
                if outcomes:
                    # ----- Build competency data for this file -----
                    # Competency framework entry
                    competency_framework_entry = {
                        "ceasn:comment": name,
                        "@id": framework_id,
                        "@type": "ceasn:CompetencyFramework",
                        "ceasn:description": "Upon completion of this program students will be able to:",
                        "ceasn:inLanguage": "en",
                        "ceasn:name": f"{name}'s Program Learning Outcomes",
                        "ceasn:publicationStatusType": "http://credreg.net/ctdlasn/vocabs/publicationStatus/Published",
                        "ceasn:source": 'https://catalog.mccc.edu/programs/' + program_code_full
                    }
                    competency_data.append(competency_framework_entry)

                    # Append each outcome as a separate competency entry
                    for outcome in outcomes:
                        competency_entry = {
                            "@id": 'ce-' + str(uuid.uuid4()),
                            "@type": "ceasn:Competency",
                            "ceasn:inLanguage": "en",
                            "ceasn:competencyLabel": "Program Learning Outcome",
                            "ceasn:competencyText": outcome,
                            "ceasn:isPartOf": framework_id
                        }
                        competency_data.append(competency_entry)
        
        # Write the rows to CSV
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = rows[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        # Save the competency data to CSV
        df_competency = pd.DataFrame(competency_data)
        competency_csv = r"C:\text\NJ\Mercer\credentials\Review\Mercer_BU_Credit_Credential_Competencies.csv"
        df_competency.to_csv(competency_csv, index=False, encoding="utf-8-sig")
        print(f"Competency data successfully saved to {competency_csv}")
        
        print(f"CSV file '{csv_file}' created successfully.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# File paths
json_file = 'programs.json'  # Update with the correct path if necessary
csv_file = 'programs_output.csv'

# Convert JSON to CSV
json_to_csv(json_file, csv_file)
