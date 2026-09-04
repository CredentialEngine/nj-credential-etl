import os
import csv
from bs4 import BeautifulSoup

# Define file paths
input_file = r"C:\text\NJ\Salem\course\SCC Course Outlines _ Salem Community College.html"
output_file = r"C:\text\NJ\Salem\course\SCC_Course_Links.csv"

# Read the HTML file
with open(input_file, "r", encoding="utf-8-sig") as file:
    soup = BeautifulSoup(file, "html.parser")

# Find all matching links inside <li><a> elements
course_links = []
for li in soup.find_all("li"):
    a_tag = li.find("a", href=True, title="View Course Syllabus")  # Match specific pattern
    if a_tag:
        course_name = a_tag.text.strip()
        course_url = a_tag["href"]
        course_links.append([course_name, course_url])

# Save to CSV
with open(output_file, "w", newline="", encoding="utf-8-sig") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Course Name", "URL"])  # Header row
    writer.writerows(course_links)  # Data rows

print(f"Extraction complete. Output saved to {output_file}")
