from bs4 import BeautifulSoup
import csv

# Load your HTML into 'html_content' variable
file_path = r"C:\text\NJ\Brookdale\noncredit\programs\Programs _ Brookdale Community College.html"

with open(file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, 'html.parser')


# Prepare to write to CSV
with open('programs.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Program Name', 'Program Link'])  # Writing the headers
    
    # Find all 'a' tags and filter by href attribute containing the specified URL pattern
    links = soup.find_all('a', href=True)
    filtered_links = [link for link in links if 'https://ce.brookdalecc.edu/public/category/programStream.do' in link['href']]

    for link in filtered_links:
        program_name = link.get_text(strip=True)
        program_link = link['href']
        
        # Write each program's name and link to the CSV
        writer.writerow([program_name, program_link])


print("Data has been written to 'programs.csv'")
