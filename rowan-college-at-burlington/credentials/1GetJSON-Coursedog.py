import requests
import math
import json
import csv

def main():
    # Base URL with a placeholder `{skip}` that we'll format in the loop #https://app.coursedog.com/api/v1/cm/rcbc_colleague/programs/search/%24filters?catalogId=etXDqB2hWoWGqYM5IjQI&skip=0&limit=20&sortBy=catalogDisplayName%2CtranscriptDescription%2ClongName%2Cname&effectiveDatesRange=2024-07-01%2C2024-07-01&columns=name%2Ctype%2CdegreeDesignation%2Ccontacts%2ClongName%2CcatalogDisplayName%2CtranscriptDescription%2CcatalogDescription%2CcatalogImageUrl%2CcipCode%2Ccampus%2Clevel
    url_template = (
        "https://app.coursedog.com/api/v1/cm/rcbc_colleague/programs/search/%24filters"
        "?catalogId=etXDqB2hWoWGqYM5IjQI"
        "&skip={skip}"
        "&limit=20"
        "&sortBy=catalogDisplayName%2CtranscriptDescription%2ClongName%2Cname"
        "&effectiveDatesRange=2024-07-01%2C2024-07-01"
        "&columns=name%2Ctype%2CdegreeDesignation%2Ccontacts%2ClongName%2CcatalogDisplayName"
        "%2CtranscriptDescription%2CcatalogDescription%2CcatalogImageUrl%2CcipCode%2Ccampus%2Clevel"
    )

    all_data = []

    # 1) First call: fetch the JSON, retrieve total listLength
    initial_url = url_template.format(skip=0)
    response = requests.get(initial_url)
    response.raise_for_status()  # raise an error if the request failed
    response_json = response.json()

    # The JSON structure has 'listLength' and 'data'
    list_length = response_json['listLength']
    all_data.extend(response_json['data'])

    # 2) Determine how many calls are needed
    limit = 20
    num_calls = math.ceil(list_length / limit)

    # Start looping from page 2 (since we already did skip=0)
    for i in range(1, num_calls):
        skip_value = i * limit
        page_url = url_template.format(skip=skip_value)
        r = requests.get(page_url)
        r.raise_for_status()
        page_json = r.json()
        # Add these data items to our master list
        all_data.extend(page_json['data'])

    # 3) Save combined data to a single JSON file
    with open("all_data.json", "w", encoding="utf-8") as f_json:
        json.dump(all_data, f_json, ensure_ascii=False, indent=2)

    # 4) Convert combined data to CSV
    #    Collect all possible fieldnames (keys) that appear in the data
    fieldnames = set()
    for item in all_data:
        fieldnames.update(item.keys())
    fieldnames = sorted(fieldnames)

    with open("all_data.csv", "w", encoding="utf-8", newline="") as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
        writer.writeheader()
        for item in all_data:
            writer.writerow(item)

if __name__ == "__main__":
    main()
