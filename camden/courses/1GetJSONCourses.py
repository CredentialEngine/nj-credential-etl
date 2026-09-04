import requests
import json

"""
Below is an updated version of the Python script that more closely mimics your browser’s request. In this version you’ll need to supply the current cookie string and the current value for the __RequestVerificationToken (they may expire, so you may need to update them from your browser’s network inspector):

Notes
Cookie and Verification Token:
The script now uses a header that includes the full cookie string and the __RequestVerificationToken exactly as in your browser’s debug tool. If you still receive errors, double-check that these values are up to date. They may change with each session.

Content-Length:
You don’t need to specify Content-Length in the script; the requests library will handle that automatically.

Debug Output:
The script prints the first 500 characters of the response from page 1. This can help you inspect whether you’re getting a valid JSON response or an error page (for example, an HTML login page).

If you continue to experience issues, it’s likely that additional session handling (such as first performing a GET to establish a session and collect cookies/tokens) may be required. Let me know if you need further adjustments or assistance!
"""


# URL for the course search asynchronous endpoint
BASE_URL = "https://selfservice.camdencc.edu/Student/Courses/SearchAsync"

def get_payload(page_number):
    # Build the searchParameters object. Adjust if needed.
    search_parameters = {
        "keyword": None,
        "terms": [],
        "requirement": None,
        "subrequirement": None,
        "courseIds": None,
        "sectionIds": None,
        "requirementText": None,
        "subrequirementText": "",
        "group": None,
        "startTime": None,
        "endTime": None,
        "openSections": None,
        "subjects": [],
        "academicLevels": [],
        "courseLevels": [],
        "synonyms": [],
        "courseTypes": [],
        "topicCodes": [],
        "days": [],
        "locations": [],
        "faculty": [],
        "onlineCategories": None,
        "keywordComponents": [],
        "startDate": None,
        "endDate": None,
        "startsAtTime": None,
        "endsByTime": None,
        "pageNumber": page_number,
        "sortOn": "None",
        "sortDirection": "Ascending",
        "subjectsBadge": [],
        "locationsBadge": [],
        "termFiltersBadge": [],
        "daysBadge": [],
        "facultyBadge": [],
        "academicLevelsBadge": [],
        "courseLevelsBadge": [],
        "courseTypesBadge": [],
        "topicCodesBadge": [],
        "onlineCategoriesBadge": [],
        "openSectionsBadge": "",
        "openAndWaitlistedSectionsBadge": "",
        "subRequirementText": None,
        "quantityPerPage": 30,
        "openAndWaitlistedSections": None,
        "searchResultsView": "CatalogListing"
    }
    # The API expects searchParameters as a JSON string.
    payload = {
        "searchParameters": json.dumps(search_parameters)
    }
    return payload

def main():
    # Replace the following cookie and token values with your own current session values.
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json, charset=UTF-8",
        # Insert your full cookie string from your browser here:
        "Cookie": ("sbjs_migrations=1418474375998%3D1; sbjs_first_add=fd%3D2025-01-21%2016%3A30%3A53%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.camdencc.edu%2Facademics-1%2Fcatalog%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.google.com%2F; sbjs_first=typ%3Dorganic%7C%7C%7Csrc%3Dgoogle%7C%7C%7Cmdm%3Dorganic%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29; _gcl_au=1.1.1013763805.1737477054; _ga=GA1.1.211054455.1737477054; _fbp=fb.1.1737477053857.26845227914425905; __RequestVerificationToken_L1N0dWRlbnQ1=9-kYwMYJCakvs-O-pYIwUc6lGqKBCPBflVENAyOWbyaJ5MnTO6m6M9m2BbbZpv9UUSKYe1j3KTQotfGj2_zAFbk3f21vW6Zxag1Taf192881; sbjs_current_add=fd%3D2025-02-05%2020%3A55%3A44%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.camdencc.edu%2Fabout-1%2Fcontact-ccc%2F%3Futm_campaign%3Dfooter_button%26utm_medium%3DText_Link%26utm_source%3DInternal_Webpage%26utm_term%3Dcontact_us%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.camdencc.edu%2Fabout-1%2F; sbjs_current=typ%3Dutm%7C%7C%7Csrc%3DInternal_Webpage%7C%7C%7Cmdm%3DText_Link%7C%7C%7Ccmp%3Dfooter_button%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3Dcontact_us%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29; sbjs_udata=vst%3D14%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F133.0.0.0%20Safari%2F537.36; sbjs_session=pgs%3D1%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fwww.camdencc.edu%2Fprogram%2Fautomotive-technology-apprentice%2F; _ga_NHFP9MZ3FS=GS1.1.1739458267.17.0.1739458273.0.0.0; _ga_28WFVF378N=GS1.1.1739458267.17.0.1739458273.0.0.0; _ga_PWBL09091X=GS1.1.1739458267.17.0.1739458273.0.0.0"),
        "Origin": "https://selfservice.camdencc.edu",
        "Referer": "https://selfservice.camdencc.edu/Student/Courses/Search?keyword=",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/133.0.0.0 Safari/537.36"),
        "X-Requested-With": "XMLHttpRequest",
        # Include the verification token as seen in your browser.
        "__RequestVerificationToken": "tap576GS7lJikpNPtXs9yeoLcYURrPv4XtTUERq84TkMdkGuhhjX0nKVWmHhDfKHe3xvV0Sic_wSrFZV501F_4FnPt4S_IzbEpC71qvV4V01"
    }
    
    session = requests.Session()

    # Request the first page to determine total pages.
    print("Requesting first page to determine total pages...")
    payload = get_payload(1)
    response = session.post(BASE_URL, headers=headers, json=payload)
    
    # Debug: print first few hundred characters of the response.
    print("Response text (first 500 characters):")
    print(response.text[:500])
    
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        print("Error decoding JSON. Check if your cookies and token are valid.")
        return

    total_pages = data.get("TotalPages", 1)
    print(f"Total pages to download: {total_pages}")
    
    all_courses = []

    for page in range(1, total_pages + 1):
        print(f"Downloading page {page} of {total_pages}...")
        payload = get_payload(page)
        resp = session.post(BASE_URL, headers=headers, json=payload)
        if resp.status_code == 200:
            try:
                page_data = resp.json()
                courses = page_data.get("Courses", [])
                all_courses.extend(courses)
            except json.JSONDecodeError:
                print(f"JSON decode error on page {page}. Response:")
                print(resp.text)
        else:
            print(f"Error on page {page}: Status code {resp.status_code}")
    
    output_filename = "all_courses.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(all_courses, f, indent=2)
    
    print(f"Downloaded {len(all_courses)} courses. Data saved to '{output_filename}'.")

if __name__ == "__main__":
    main()
