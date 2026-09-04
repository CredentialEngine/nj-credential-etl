import requests
import math
import json
import csv

def main():
    print("Starting script...")

    # Base URL with a placeholder `{skip}` that we'll format in the loop
    url_template = (
        "https://app.coursedog.com/api/v1/cm/mercercounty_colleague/courses/search/%24filters"
        "?catalogId=uactPpmWkUJ3jsgXArnH"
        "&skip={skip}"
        "&limit=20"
        "&orderBy=catalogDisplayName%2CtranscriptDescription%2ClongName%2Cname"
        "&formatDependents=false"
        "&effectiveDatesRange=2024-09-03%2C2025-08-20"
        "&columns=customFields.rawCourseId%2CcustomFields.crseOfferNbr%2CcustomFields.catalogAttributes"
        "%2CdisplayName%2Cdepartment%2Cdescription%2Cname%2CcourseNumber%2CsubjectCode%2Ccode%2CcourseGroupId"
        "%2Ccareer%2Ccollege%2ClongName%2Cstatus%2Cinstitution%2CinstitutionId%2Ccredits"
    )

    all_data = []

    # 1) First call: fetch the JSON, retrieve total listLength
    print("Fetching initial data...")
    initial_url = url_template.format(skip=0)
    response = requests.get(initial_url)
    response.raise_for_status()  # raise an error if the request failed
    response_json = response.json()

    # The JSON structure has 'listLength' and 'data'
    list_length = response_json['listLength']
    all_data.extend(response_json['data'])

    print(f"Total courses found: {list_length}")

    # 2) Determine how many calls are needed
    limit = 20
    num_calls = math.ceil(list_length / limit)

    # Start looping from page 2 (since we already did skip=0)
    for i in range(1, num_calls):
        skip_value = i * limit
        page_url = url_template.format(skip=skip_value)
        print(f"Fetching data for skip={skip_value} ({i + 1}/{num_calls})...")
        r = requests.get(page_url)
        r.raise_for_status()
        page_json = r.json()
        # Add these data items to our master list
        all_data.extend(page_json['data'])

    print("All data fetched successfully.")

    # 3) Save combined data to a single JSON file
    print("Saving data to all_courses.json...")
    with open("all_courses.json", "w", encoding="utf-8") as f_json:
        json.dump(all_data, f_json, ensure_ascii=False, indent=2)

    print("Data saved to all_courses.json.")

    # 4) Convert combined data to CSV
    print("Converting data to CSV format...")
    # Collect all possible fieldnames (keys) that appear in the data
    fieldnames = set()
    for item in all_data:
        fieldnames.update(item.keys())
    fieldnames = sorted(fieldnames)  # optional: sort them

    with open("all_courses.csv", "w", encoding="utf-8", newline="") as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
        writer.writeheader()
        for item in all_data:
            writer.writerow(item)

    print("Data saved to all_courses.csv.")
    print("Script completed successfully.")

if __name__ == "__main__":
    main()
