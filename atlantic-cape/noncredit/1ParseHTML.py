import pandas as pd
from bs4 import BeautifulSoup, Comment

def parse_html(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
        soup = BeautifulSoup(content, 'html.parser')

    link_details = []

    # Find the section between the comments
    start_comment = soup.find(string=lambda text: isinstance(text, Comment) and "BEGIN: Section Links" in text)
    end_comment = soup.find(string=lambda text: isinstance(text, Comment) and "END: Section Links" in text)

    # Collect all <li> tags between these comments
    current_element = start_comment.next_element
    while current_element != end_comment:
        if current_element.name == "li":
            a_tag = current_element.find('a')
            if a_tag and 'href' in a_tag.attrs:
                link_name = a_tag.text.strip()
                link_url = a_tag['href'].strip()
                link_details.append({
                    'Link Name': link_name,
                    'Link URL': link_url
                })
        current_element = current_element.next_element

    # Convert list to DataFrame
    df = pd.DataFrame(link_details)
    output_csv_path = 'noncredit.csv'
    df.to_csv(output_csv_path, index=False)
    print(f'Data saved to {output_csv_path}')

# Replace 'your_html_file_path.html' with your actual file path
file_path = r"C:\text\NJ\Atlantic Cape\noncredit\Atlantic Cape Community College _ Professional Development.html"
parse_html(file_path)
