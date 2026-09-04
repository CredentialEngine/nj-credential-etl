from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import uuid

def map_type(type_):
    type_mapping = {
        "A.A.": "Associate of Arts Degree",
        "A.A. - Liberal Arts": "Associate of Arts Degree",
        "A.A.S.": "Associate of Applied Science Degree",
        "A.A.S": "Associate of Applied Science Degree",
        "A.A.S. - Business Management": "Associate of Applied Science Degree",
        "A.A.S. - Computer Information Systems": "Associate of Applied Science Degree",
        "A.A.S. - Graphic Design": "Associate of Applied Science Degree",
        "A.A.S. - Technical Studies": "Associate of Applied Science Degree",
        "A.F.A.": "Associate of Arts Degree",
        "A.F.A. - Studio Arts": "Associate of Arts Degree",
        "A.S.": "Associate of Science Degree",
        "A.S. - Science/Mathematics": "Associate of Science Degree",
        "C.O.A.": "Certificate",
        "Certificate": "Certificate",
        "CT.": "Certificate",
        "CT.A.": "Certificate",
        "JFK Muhlenberg Harold B. and Dorothy A. Snyder Schools of Nursing and Medical Imaging, A.S.": "Associate of Science Degree",
        "Restaurant, and Tourism Management, A.A.S.": "Associate of Applied Science Degree",
        "Restaurant, and Tourism Management, CT.A.": "Certificate",
        "Suggested Grades 4-12, A.A.": "Associate of Arts Degree",
        "Suggested Grades Pre-K-3, A.A.": "Associate of Arts Degree",
        "Trinitas School of Nursing/RWJ Barnabas Health, A.S.": "Associate of Science Degree",
        "AA": "Associate of Arts Degree",
        "AAS": "Associate of Applied Science Degree",
        "Academic Certificate": "Certificate",
        "AS": "Associate of Science Degree",
        "Certificate of Achievement": "Certificate"
    }
    return type_mapping.get(type_.strip(), type_)

def extract_title_and_type(soup, filename):
    """
    Extracts the credential’s title and type.
    Preference is given to an <h1> element; if not available, <title> is used.
    The type is derived by extracting text within parentheses (if present)
    or else from the filename.
    """
    # Prefer the <h1> tag if available
    h1 = soup.find('h1')
    if h1:
        title_text = h1.get_text(strip=True)
    else:
        title_tag = soup.find('title')
        title_text = title_tag.get_text(strip=True) if title_tag else "No Title"
    
    # Remove any trailing institution text
    title_text = title_text.replace(" < County College of Morris", "").strip()
    
    # Try to get the type from text in parentheses (e.g. "Business Professional (Career Program)")
    type_cleaned = ""
    internal_code = ""
    paren_match = re.search(r'\((.*?)\)', title_text)
    #internal_code = re.search(r'\((.*?)\)', filename)
    internal_code = re.search(r'\(([^)]*)\)', filename)
    internal_code = internal_code.group(1) if internal_code else None

    if paren_match:
        type_cleaned = paren_match.group(1).strip()
    else:
        # Fallback: derive type from the filename (without extension)
        base = os.path.splitext(filename)[0]
        # If the filename contains parentheses, take text before them
        if "(" in base:
            type_cleaned = base.split("(")[0].strip()
        else:
            type_cleaned = base.strip()
    
    credential_type = map_type(type_cleaned)
    return title_text, credential_type, internal_code

def extract_description(soup):
    """
    Extracts a program description.
    This version looks inside the div with id="textcontainer" and
    finds the anchor for either the Associate in Applied Science or
    Associate in Science degree. It then collects <p> tags that begin
    with “This program” or “This career” (you can adjust the filtering).
    If no anchor is found, it falls back to the first paragraph.
    """
    description = ""
    text_container = soup.find('div', id='textcontainer')
    if text_container:
        # Try to find the anchor that identifies the credential section.
        anchor = text_container.find('a', attrs={"name": lambda x: x in ["associateinappliedsciencedegree", "associateinsciencedegree"]})
        if anchor:
            paragraphs = []
            # Look for following <p> tags until a heading is encountered.
            for sibling in anchor.find_all_next():
                if sibling.name and re.match(r'^h\d', sibling.name):  # break at next heading
                    break
                if sibling.name == 'p':
                    text = sibling.get_text(strip=True)
                    # Only include paragraphs that begin with "this program" or "this career"
                    if text.lower().startswith("this program") or text.lower().startswith("this career"):
                        paragraphs.append(text)
            if paragraphs:
                description = "\n".join(paragraphs)
        # Fallback: if no anchor or matching <p> tags, use the first <p> tag.
        if not description:
            first_p = text_container.find('p')
            if first_p:
                description = first_p.get_text(strip=True)
    # Final fallback: try the meta description
    if not description:
        meta = soup.find('meta', attrs={"name": "Description"})
        if meta and meta.get("content"):
            description = meta["content"].strip()
    #Handle Broadcasting
    """
    Extracts a program description.
    This version looks inside the div with id="textcontainer" and
    finds the first meaningful text. It stops collecting when it encounters "Why Study at".
    """
    
    if text_container:
        paragraphs = []
        found_start = False

        for element in text_container.find_all(['p', 'div']):
            text = element.get_text(strip=True)

            # Skip empty elements
            if not text:
                continue

            # Stop collecting when we reach "Why Study at"
            if text.lower().startswith("why study at"):
                break

            # Start collecting once we find relevant text
            if not found_start and re.search(r'\b(Broadcasting|The program|This program|This career|This degree)\b', text, re.IGNORECASE):
                found_start = True
            
            if found_start:
                paragraphs.append(text)

        if paragraphs:
            description = "\n".join(paragraphs)


    return description.strip()

def extract_program_hours(soup):
    """
    Extracts the program hours (total credits).
    First, it looks for a div with class "crd-tot" and extracts
    the number from a span with class "total_numbl". If not found,
    it looks for a table cell that contains 'Total Credits'.
    """
    program_hours = "No program_hours"
    crd_div = soup.find('div', class_='crd-tot')
    if crd_div:
        span = crd_div.find('span', class_='total_numbl')
        if span:
            program_hours = span.get_text(strip=True)
    if program_hours == "No program_hours":
        # Alternative approach: find td with "Total Credits"
        label_td = soup.find('td', string=re.compile(r'Total Credits', re.IGNORECASE))
        if label_td:
            sibling_td = label_td.find_next_sibling('td', class_='hourscol')
            if sibling_td:
                program_hours = sibling_td.get_text(strip=True)
    return program_hours

def extract_outcomes(soup):
    """
    Extracts a list of outcome statements.
    
    First, it attempts to find a dedicated <div class="prog_outcomes"> containing an unordered list.
    If not found, it searches within the main text container (div with id="textcontainer") for any
    ordered list (<ol>) whose preceding paragraph contains outcome-indicating keywords.
    """
    outcomes = []
    
    # Option 1: Check for a dedicated outcomes section (if present)
    outcome_section = soup.find('div', class_='prog_outcomes')
    if outcome_section:
        ul = outcome_section.find('ul')
        if ul:
            for li in ul.find_all('li'):
                text = li.get_text(strip=True)
                text = re.sub(r'^\d+\.\s*', '', text)  # remove leading numbering
                if text and not text.endswith('.'):
                    text += '.'
                outcomes.append(text)
    
    # Option 2: Look in the main text container for outcome lists
    if not outcomes:
        text_container = soup.find('div', id='textcontainer')
        if text_container:
            # Find all ordered lists within the text container
            ol_elements = text_container.find_all('ol')
            for ol in ol_elements:
                # Check the previous sibling <p> for outcome indicator keywords
                prev_p = ol.find_previous_sibling('p')
                if prev_p:
                    prev_text = prev_p.get_text(strip=True).lower()
                    if ("expected to be able to meet the following outcomes" in prev_text or 
                        "program educational objectives" in prev_text):
                        for li in ol.find_all('li'):
                            text = li.get_text(strip=True)
                            text = re.sub(r'^\d+\.\s*', '', text)
                            if text and not text.endswith('.'):
                                text += '.'
                            outcomes.append(text)
    return outcomes

    

def parse_html(directory):
    data = []
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                
                # Extract title and credential type information
                name, credential_type, internal_code = extract_title_and_type(soup, filename)
                
                # Extract description text
                description = extract_description(soup)
                if not description:
                    description = f"County College of Morris's {name} program."
                
                # Extract total program hours (credits)
                program_hours = extract_program_hours(soup)
                
                # Extract outcome statements (if any)
                outcomes = extract_outcomes(soup)
                
                data.append({
                    'Filename': filename,
                    'Credential Name': name,
                    'Credential Type': credential_type,
                    'Internal Code': internal_code,
                    'Description': description,
                    'Total Program Hours': program_hours,
                    'Outcomes': outcomes
                })
    
    df = pd.DataFrame(data)
    output_csv = os.path.join('parsed_credentials.csv')
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"Data successfully parsed and saved to {output_csv}")

# Specify the directory containing your HTML files
directory_path = r"C:\text\NJ\Morris\credentials\CredentialHTML"
parse_html(directory_path)
