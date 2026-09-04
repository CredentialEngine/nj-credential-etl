from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import uuid

# Utility function to map credential types
def map_type(type_):
    type_mapping = {
        "(AA)": "AssociateofArtsDegree",
        "A.A.": "AssociateofArtsDegree",
        "A.A.S.": "AssociateofAppliedScienceDegree",
        "A.S.": "AssociateofScienceDegree",
        "C.C.": "Certificate",
        "C.P.": "Certificate",
        "Unknown": "Certificate",
    }
    return type_mapping.get(str(type_).strip(), type_)

# Function to extract credential title, type, internal code, and credits
def extract_title_type_and_credits(soup, filename):
    h1 = soup.find('h1')
    title_text = h1.get_text(strip=True) if h1 else soup.find('title').get_text(strip=True) if soup.find('title') else "No Title"
    
    # Clean institution-specific text
    title_text = title_text.replace(" Degrees | Programs Near Me | County College of Morris (CCM)", "").strip()

    # Extract type from parentheses or filename
    paren_match = re.search(r'\((.*?)\)', title_text)
    internal_code = re.search(r'\(([^)]*)\)', filename)
    internal_code = internal_code.group(1) if internal_code else None
    
    # Extract credit hours
    credits = None
    return title_text, internal_code, credits

def extract_program_overview(soup, name):
    overview_data = {
        "Program Type": "Associate of Science",
        "Abbreviation": "A.S.",
        "School": None,
        #"Hours": None,
        "Semesters": None,
        "Cost": None,
        "Learning Environment": None,
        "Type": "AssociateofScienceDegree",
        "MaxCredit": None
    }
    
    # Use a CSS selector to reliably locate the overview section
    overview_section = soup.select_one("div.pattern-program-overview")
    if overview_section:
        # Program Type and Abbreviation are in the custom block(s)
        custom_blocks = overview_section.find_all("div", class_="wp-block-custom-block-acf")
        if len(custom_blocks) >= 2:
            overview_data["Program Type"] = custom_blocks[0].get_text(strip=True)
            overview_data["Abbreviation"] = custom_blocks[1].get_text(strip=True)
        
        overview_data["Type"] = map_type(overview_data["Abbreviation"])
        
        # The School information is within a paragraph with the arrow-button style
        school_elem = overview_section.find("p", class_="is-style-arrow-button")
        if school_elem:
            overview_data["School"] = school_elem.get_text(strip=True)
        
        # Loop over all columns (both sets of wp-block-columns are included)
        columns = overview_section.select("div.wp-block-columns > div.wp-block-column")
        for col in columns:
            header = col.find("h3")
            if header:
                header_text = header.get_text(strip=True)
                if header_text == "Length":
                    # In the Length column, there are two paragraphs with large font size:
                    # one for the credit hours and one for the semesters information.
                    paragraphs = col.find_all("p", class_="has-large-font-size")
                    if len(paragraphs) >= 2:
                        overview_data["Hours"] = paragraphs[0].get_text(strip=True).replace(" credit hours","")
                        # Check if a dash is present in the string
                        if "-" in overview_data["Hours"]:
                            overview_data["Hours"], overview_data["MaxCredit"] = overview_data["Hours"].split("-", 1)  # Split into two parts

                        #overview_data["Semesters"] = paragraphs[1].get_text(strip=True)
                        # Assuming paragraphs[1] contains the text that needs to be cleaned
                        text = paragraphs[1].get_text(strip=True)
                        # Define replacement patterns
                        replacements = {
                            r"~1 Year to Complete|1 YearAll Degree Requirements|1 YearAll Requirements|~2 Semesters to Complete|~2 Semesters to CompleteAll Degree Requirements|~2 Semesters to CompleteAll Requirements": "1 Year",
                            r"~2 Years to Complete|~2 years to complete|~2 Years to CompleteAll Degree Requirements|2 YearsAll Degree Requirements|2 YearsDegree Requirements|~4 semesters to complete|~4 Semesters to Complete|~4 semesters to completeDegree Requirements": "2 Years"
                        }
                        # Perform replacements
                        for pattern, replacement in replacements.items():
                            text = re.sub(pattern, replacement, text)
                            text = text.replace("All Degree Requirements","").replace("All Requirements","").strip()
                            text = text.replace("Degree Requirements","").strip()
                        # Assign the cleaned text to the dictionary
                        overview_data["Semesters"] = text

                elif header_text == "Cost":
                    cost_p = col.find("p", class_="has-large-font-size")
                    if cost_p:
                        overview_data["Cost"] = cost_p.get_text(strip=True).replace("$","").replace(" per credit for county residents","").replace("Per credit","").replace("Typically","").replace("per semester","").replace(",","").strip()
                        # Ensure Length is processed correctly
                        length_str = overview_data["Hours"].replace(" credit hours", "")

                        # Extract mincredit from Length
                        if "-" in length_str:
                            mincredit = int(length_str.split("-", 1)[0])  # Take the first (minimum) value
                        else:
                            mincredit = int(length_str)  # Convert directly if it's a single value

                        # Convert cost to a number if needed
                        cost = float(overview_data["Cost"])  # Assuming cost is a float

                        # Compute total cost
                        overview_data["Cost"] = "tuition~" + str(cost * mincredit)
                elif header_text == "Learning Environment":
                    env_p = col.find("p", class_="has-large-font-size")
                    if env_p:
                        overview_data["Learning Environment"] = env_p.get_text(strip=True).replace("In Person & Online","In-Person|OnlineOnly").replace("In Person","In-Person")
    if "online" in name.lower() and not overview_data.get("Learning Environment"):
        overview_data["Learning Environment"] = "OnlineOnly"
    return overview_data


# Function to parse HTML directory
def parse_html(directory):
    data = []

    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                name, internal_code, credits = extract_title_type_and_credits(soup, filename)
                overview_data = extract_program_overview(soup, name)

                canonical_url = soup.find("link", rel="canonical")["href"] if soup.find("link", rel="canonical") else "No URL"
                meta_description = soup.find("meta", attrs={"name": "description"})["content"] if soup.find("meta", attrs={"name": "description"}) else "No description"
                
                entry = {
                    'Filename': filename,
                    'Credential Name': name,
                    'Name': name + ": " + overview_data["Program Type"],
                    #'Credential Type': credential_type,
                    'URL': canonical_url,
                    'Description': meta_description,
                }
                entry.update(overview_data)
                if canonical_url != "https://www.ocean.edu/programs-courses/degrees-certificates/":
                    data.append(entry)
    return pd.DataFrame(data)

# Function to merge additional CSV data
def merge_csv_data(df, file1, output_file):
    #This isn't needed because the credential type is contained in the program overview section and can be integrated to create the name and type.
    '''df1 = pd.read_csv(file1)
    merged_df = df.merge(df1[['Program Link', 'Credential Type']], left_on='URL', right_on='Program Link', how='left').drop(columns=['Program Link'])
    
    merged_df['Credential Type_y'].fillna("Unknown", inplace=True)
    merged_df['Type'] = merged_df['Credential Type_y'].apply(map_type)
    merged_df['Name'] = merged_df['Credential Name'] + ": " + merged_df['Credential Type_y'].str.replace(r"[()]", "", regex=True)
    merged_df['Name'] = merged_df['Name'].str.replace("Certificates", "Certificate")'''
    merged_df = df

    merged_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"Updated CSV saved to: {output_file}")
    
    return merged_df

# Main execution
directory_path = r"C:\\text\\NJ\\Ocean\\credentials\\programs\\CredentialHTML"
file1 = r"C:\\text\\NJ\\Ocean\\credentials\\programs\\credentials_parsed.csv"
output_file = r"C:\\text\\NJ\\Ocean\\credentials\\programs\\parsed_credentials_updated.csv"

# Parse HTML files
df = parse_html(directory_path)

# Merge additional CSV data
merged_df = merge_csv_data(df, file1, output_file)
