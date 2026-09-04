import os
import pandas as pd
from bs4 import BeautifulSoup
import re

def filename_to_url(filename):
    # Remove the leading 'https___' and '.html' extension from the filename
    clean_filename = filename.replace("https___", "").replace(".html", "")

    # Replace underscores with slashes to form the path part of the URL
    path_parts = clean_filename.split('_')
    
    # Extract the domain part and add 'https://' prefix
    domain = 'https://' + path_parts[0]

    # Construct the rest of the URL
    rest_of_url = '/' + '/'.join(path_parts[1:])

    # Replace 'certificate' with 'course' and 'index.cfm' with 'course/index.cfm' in the URL
    #rest_of_url = rest_of_url.replace("certificate/index.cfm", "course/index.cfm")

    # Final URL construction
    full_url = domain + rest_of_url

    return full_url

# Directory containing the HTML files
directory_path = r'C:\text\NJ\Union\noncredit\ugotclass\CourseCertHTML'

# Prepare to collect data
data = []

# Iterate over each file in the directory
for filename in os.listdir(directory_path):
    if filename.endswith(".html"):
        file_path = os.path.join(directory_path, filename)

        # Open and read the HTML file
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            html_content = file.read()

        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract the title (usually found in the head of the HTML)
        title = soup.title.text if soup.title else 'No Title'

        # Extract h2 text if available
        h2_text = soup.h2.text if soup.h2 else 'No Heading'

        # Extract description from specific structure
        description_content = soup.find('div', class_="content-block")
        if description_content:
            description = description_content.text.strip()
            ceu_index = description.find('CEUs:')
            if ceu_index != -1:
                description = description[:ceu_index].strip()
        else:
            description = 'No Description'
        # Remove excessive whitespaces, line feeds, and non-breaking spaces
        description = re.sub(r'\s+', ' ', description)  # Replace all whitespace characters with a single space
        description = description.replace('\xa0', ' ').strip()  # Replace non-breaking spaces
        
        '''# Extract other elements like CEUs, length, price based on structure
        p_text = soup.find('p').text if soup.find('p') else ''
        
        # Initialize variables
        ceus, length, price_usd = None, None, None

        # Find specific information in the p element
        for line in p_text.split('\n'):
            if 'CEUs:' in line:
                ceus = line.split(':')[-1].strip()
            if 'Length' in line:
                length = line.split(':')[-1].strip().split(' ')[0]  # Get only the number
            if 'Price in USD' in line:
                price_usd = line.split('$')[-1].strip()  # Get only the number'''
        # Extract the <p> tag, replace <br> tags with new lines, and get the text
        p_tag = soup.find('p')
        p_text = ''
        if p_tag:
            for br in p_tag.find_all('br'):
                br.replace_with('\n')
            p_text = p_tag.text.strip()

        # Initialize variables
        ceus, length, price_usd = None, None, None

        # Find specific information in the modified p_text
        for line in p_text.split('\n'):
            if 'CEUs:' in line:
                ceus = line.split(':')[-1].strip()
            if 'Length (in hours):' in line:
                length = line.split(':')[-1].strip().split(' ')[0]  # Get only the number
            if 'Price in USD' in line:
                price_usd = line.split('$')[-1].strip()  # Get only the number

        url = filename_to_url(filename)
        #Find type
        if 'certificate' in filename.lower():
            type_ = "Certificate"
        else:
            type_ = "Course"

        # Append data to list
        data.append({
            'Title': title,
            'Heading': h2_text,
            'Description': description,
            'Type': type_,
            'CEUs': ceus,
            'Length (hours)': length,
            'Price in USD': price_usd,
            'Filename': filename,
            'Subject Webpage': url
        })

# Create a DataFrame from the data
df = pd.DataFrame(data)

# Output CSV file path
output_csv_path = r'C:\text\NJ\Union\noncredit\ugotclass\CourseCertInfo.csv'

# Save the DataFrame to a CSV file
df.to_csv(output_csv_path, index=False)

print("Data extraction complete. Data saved to:", output_csv_path)
