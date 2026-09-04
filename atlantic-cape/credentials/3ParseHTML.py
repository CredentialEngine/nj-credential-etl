from bs4 import BeautifulSoup
import pandas as pd
import os

def parse_html_files(directory):
    # Create an empty list to store the data
    data = []
    
    # Iterate over each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            file_path = os.path.join(directory, filename)
            
            # Read the HTML content
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                
                # Extract the canonical URL
                canonical_link = soup.find('link', rel='canonical')
                url = canonical_link['href'] if canonical_link else "No URL found"
                
                # Extract the credential title
                title_elem = soup.find('h1')
                title = title_elem.get_text(strip=True) if title_elem else "No Title Found"
                
                # Extract credential description
                description_elem = soup.find('div', class_='field field--name-body field--type-text-with-summary field--label-hidden field__item')
                description = description_elem.get_text(separator=' ', strip=True) if description_elem else "No description available"
                
                #Get Credits
                # Find the div that contains "Total Credits"
                total_credits_div = soup.find('div', class_='col-10', string=lambda text: text and "Total Credits" in text)

                if total_credits_div:
                    # Get the next sibling div
                    next_div = total_credits_div.find_next_sibling('div')
                    if next_div:
                        credits_ = next_div.get_text(strip=True)
                
                # Extract program outcomes
                outcomes_elem = soup.find('div', class_='field field--name-field-program-outcomes field--type-text-with-summary field--label-above')
                if outcomes_elem:
                    outcomes_items = outcomes_elem.find_all('li')  # Directly find <li> tags within the element
                    formatted_outcomes = []
                    for item in outcomes_items:
                        outcome = item.get_text(separator=' ', strip=True)
                        # Ensure the outcome starts with a capital letter
                        outcome = outcome[0].upper() + outcome[1:] if outcome else outcome
                        # Remove any trailing semicolon
                        if outcome.endswith(';'):
                            outcome = outcome[:-1]
                        # Ensure the outcome ends with a period
                        if outcome and not outcome.endswith('.'):
                            outcome += '.'
                        formatted_outcomes.append(outcome)
                    outcomes = " | ".join(formatted_outcomes)
                else:
                    outcomes = "No outcomes listed"

                
                # Append data to the list
                data.append({
                    "Filename": filename,
                    "URL": url,
                    "Title": title,
                    "Description": description,
                    "Program Outcomes": outcomes,
                    "Credits": credits_,
                })
    
    # Convert the list to a DataFrame
    df = pd.DataFrame(data)
    
    # Save DataFrame to CSV
    output_csv_path = os.path.join("credentials_extracted.csv")
    df.to_csv(output_csv_path, index=False)
    print(f"Data successfully extracted and saved to {output_csv_path}")

# Define the directory path
directory_path = r"C:\text\NJ\Atlantic Cape\credentials\CredentialsHTML"

# Call the function to parse HTML files and save data
parse_html_files(directory_path)
