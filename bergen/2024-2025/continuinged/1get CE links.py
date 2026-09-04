import pandas as pd
from bs4 import BeautifulSoup

# Load the HTML file
with open(r"C:\text\NJ\Bergen\ContinuingEd\Courses and Programs _ Bergen Community College.html", "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

# Find all div tags with class 'card-body pt-5'
divs = soup.find_all("ul", class_="subpage")

# Extract links and link names
links = []
for div in divs:
    for a_tag in div.find_all("a", href=True):
        link = a_tag["href"]
        link_name = a_tag.get_text(strip=True)
        links.append({"Link Name": link_name, "URL": link})

# Convert to DataFrame
df_links = pd.DataFrame(links)

# Option 1: Print the DataFrame to the console
print(df_links)

# Option 2: Save the DataFrame to a CSV file
output_csv = r"C:\text\NJ\Bergen\ContinuingEd\extracted_CE_links.csv"
df_links.to_csv(output_csv, index=False, encoding="utf-8")
print(f"Data saved to {output_csv}")
