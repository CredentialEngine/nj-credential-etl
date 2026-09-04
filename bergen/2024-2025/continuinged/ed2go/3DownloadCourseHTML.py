import os
import csv
import requests

# File paths
csv_file_path = r"C:\text\NJ\Bergen\ContinuingEd\ed2go\CEonlinecourses.csv"
output_directory = r"C:\text\NJ\Bergen\ContinuingEd\ed2go\coursesHTML"

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Custom headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.100 Safari/537.36",
    "Referer": "https://onlinecareertraining.bergen.edu/",
    "Accept-Language": "en-US,en;q=0.9"
}

# Read the CSV and download HTML pages
with open(csv_file_path, 'r', encoding='utf-8-sig') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        # Extract the Course Link
        course_link = row.get("Course Link", "").strip()
        if course_link:
            # Generate a safe filename based on the URL or course name
            course_name = row.get("Course Name", "course").strip().replace(" ", "_").replace("/", "_")
            html_file_path = os.path.join(output_directory, f"{course_name}.html")
            
            # Skip download if the file already exists
            if os.path.exists(html_file_path):
                print(f"File already exists, skipping: {course_name}")
                continue

            try:
                # Make a GET request with custom headers and follow redirects
                response = requests.get(course_link, headers=headers, timeout=15, allow_redirects=True)
                
                # Check for non-200 status codes
                if response.status_code != 200:
                    print(f"Non-200 status code for {course_link}: {response.status_code}")
                    continue

                # Inspect the final URL
                final_url = response.url
                print(f"Final URL after redirection: {final_url}")

                # Ensure response content is not empty
                if not response.content.strip():
                    print(f"Blank content for {course_link}")
                    continue

                # Check Content-Type header to verify HTML
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' not in content_type:
                    print(f"Unexpected content type for {course_link}: {content_type}")
                    continue

                # Save the HTML content to the file
                with open(html_file_path, 'w', encoding='utf-8') as html_file:
                    html_file.write(response.text)

                print(f"Downloaded and saved: {course_name}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to download {course_link}: {e}")
        else:
            print("No Course Link found for a row.")

print("Download complete.")
