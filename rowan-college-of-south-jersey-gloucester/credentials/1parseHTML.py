from bs4 import BeautifulSoup
import pandas as pd

# Example HTML content
html_content = r"C:\text\NJ\Rowan College of South Jersey - Gloucester\credentials\Degrees.htm"

# Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')
cards = soup.find_all('div', class_='card program')

data = []

# Extract data from each card
for card in cards:
    program_name = card.find('h3').text.strip()
    description = card.find('p').text.strip()
    campuses = [li.text.strip() for li in card.select('.program__campuses li')]
    interests = [li.text.strip() for li in card.select('.program__interests-list li')]
    
    metadata = {
        'threeplusone': card.get('data-threeplusone'),
        'interests': card.get('data-interests'),
        'campuses': card.get('data-campuses'),
        'credits': card.get('data-credits')
    }
    
    data.append({
        'Program Name': program_name,
        'Description': description,
        'Campuses': campuses,
        'Interests': interests,
        'Metadata': metadata
    })

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to CSV
csv_file_path = 'programs_info.csv'
df.to_csv(csv_file_path, index=False)

print(f'Data saved to {csv_file_path}')
