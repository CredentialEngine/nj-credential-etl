import os
import csv
import re
from bs4 import BeautifulSoup
import uuid
import pandas as pd

def format_outcome(text):
    """
    Format an outcome statement by stripping extra whitespace and numbering,
    ensuring the first letter is capitalized, and that it ends with a period.
    """
    text = text.strip()
    # Remove any leading numbering such as "1. " or "10. "
    text = re.sub(r'^\d+\.\s+', '', text)
    if text:
        text = text[0].upper() + text[1:]
        if not text.endswith('.'):
            text += '.'
    return text


# Define type mappings to CTDL
type_mapping = {
    "A.A.": "AssociateOfArtsDegree",
    "A.A. Online": "AssociateOfArtsDegree",
    "A.A.S": "AssociateOfAppliedScienceDegree",
    "A.A.S.": "AssociateOfAppliedScienceDegree",
    "A.S.": "AssociateOfScienceDegree",
    "A.S. Online": "AssociateOfScienceDegree",
    "Academic Credit Certificate": "Certificate",
    "Academic Credit Certificate of Achievement": "Certificate",
    "Addiction Studies Option, A.S.": "AssociateOfScienceDegree",
    "Anthropology Option, A.A.": "AssociateOfArtsDegree",
    "Art Option, A.A.": "AssociateOfArtsDegree",
    "Audio Production Option, A.A.S": "AssociateOfAppliedScienceDegree",
    "Auto Engineering Tech Option, A.A.S.": "AssociateOfAppliedScienceDegree",
    "Auto Tech Option, A.A.S.": "AssociateOfAppliedScienceDegree",
    "Bcd Pg": "Certificate",
    "BCD Program": "Certificate",
    "Biology Option, A.S.": "AssociateOfScienceDegree",
    "Business Management Option, A.A.S": "AssociateOfAppliedScienceDegree",
    "Cert of Achievement": "Certificate",
    "Certificate of Achievement": "Certificate",
    "Chemistry Option, A.S.": "AssociateOfScienceDegree",
    "Corrections Option, A.S.": "AssociateOfScienceDegree",
    "CPS Program": "Certificate",
    "Creative Writing Option, A.A.": "AssociateOfArtsDegree",
    "Criminal Justice Option, A.A.": "AssociateOfArtsDegree",
    "Data Science Option, A.S.": "AssociateOfScienceDegree",
    "Early Childhood Education Option, A.A.": "AssociateOfArtsDegree",
    "Elect Engin Tech Option, A.A.S.": "AssociateOfAppliedScienceDegree",
    "Elect/Computer Tech Option, A.A.S": "AssociateOfAppliedScienceDegree",
    "Elem, Middle School & Second Ed Option, A.A.": "AssociateOfArtsDegree",
    "English Option, A.A.": "AssociateOfArtsDegree",
    "English Option, A.A. Online": "AssociateOfArtsDegree",
    "Generalist Option, A.S.": "AssociateOfScienceDegree",
    "GMASEP, A.A.S.": "AssociateOfAppliedScienceDegree",
    "Graphic Design Option, A.A.": "AssociateOfArtsDegree",
    "Health Science Option, A.A.": "AssociateOfArtsDegree",
    "History Option, A.A.": "AssociateOfArtsDegree",
    "History Option, A.A. Online": "AssociateOfArtsDegree",
    "Journalism Option, A.A.": "AssociateOfArtsDegree",
    "Liberal Arts Option, A.A.": "AssociateOfArtsDegree",
    "Liberal Arts Undecided Track": "Certificate",
    "Liberal Arts, A.A. Online": "AssociateOfArtsDegree",
    "Liberal Education Option, A.A.": "AssociateOfArtsDegree",
    "Liberal Education Option, A.A. Online": "AssociateOfArtsDegree",
    "Mathematics Option, A.S.": "AssociateOfScienceDegree",
    "Media Studies Option, A.A.": "AssociateOfArtsDegree",
    "Multimedia Production Option, A.A.": "AssociateOfArtsDegree",
    "Music Option, A.A.": "AssociateOfArtsDegree",
    "Philosophy Option, A.A.": "AssociateOfArtsDegree",
    "Photography Option, A.A.": "AssociateOfArtsDegree",
    "Physics Option, A.S.": "AssociateOfScienceDegree",
    "Political Science Option, A.A.": "AssociateOfArtsDegree",
    "Pre-Social Work Option, A.S.": "AssociateOfScienceDegree",
    "Programming Option, A.A.S.": "AssociateOfAppliedScienceDegree",
    "Psychology Option, A.A.": "AssociateOfArtsDegree",
    "Psychology Option, A.A. Online": "AssociateOfArtsDegree",
    "Public Relations Option, A.A.": "AssociateOfArtsDegree",
    "Science Option, A.S.": "AssociateOfScienceDegree",
    "Sociology Option, A.A.": "AssociateOfArtsDegree",
    "Sociology Option, A.A. Online": "AssociateOfArtsDegree",
    "Studo Art Option, A.F.A.": "AssociateOfArtsDegree",
    "Theater Option, A.A.": "AssociateOfArtsDegree",
    "Video Production Option, A.A.S": "AssociateOfAppliedScienceDegree",
    "Web Site Development Option, A.A.S": "AssociateOfAppliedScienceDegree",
    "Women's & Gender Studies Option, A.A.": "AssociateOfArtsDegree",
}

def main():
    # Set input and output paths (adjust as needed)
    input_folder = r"C:\text\NJ\Brookdale\credentials\CredentialHTML"
    output_csv = r"C:\text\NJ\Brookdale\credentials\parsed_credentials.csv"
    output_competency_csv = r"C:\text\NJ\Brookdale\credentials\Review\Brookdale_BU_Credit_Credential_Competencies.csv"

    # Open the credentials CSV for writing
    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["Filename", "Program Title", "Type", "Credits", "Program Code", "Program Description", "Outcomes"])

        # Create an empty list to store competency data (both frameworks and individual outcomes)
        competency_data = []

        # Process each HTML file in the input folder
        for filename in os.listdir(input_folder):
            if not filename.lower().endswith(".html"):
                continue  # skip non-HTML files

            full_path = os.path.join(input_folder, filename)
            try:
                with open(full_path, "r", encoding="utf-8") as f_in:
                    html = f_in.read()
            except (UnicodeDecodeError, OSError) as e:
                print(f"[ERROR] Cannot read {filename}: {e}")
                continue

            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(html, "lxml")

            # (Optionally) extract a canonical URL if available
            canonical_link = soup.find('link', rel='canonical')
            url = canonical_link['href'] if canonical_link and canonical_link.has_attr('href') else ""

            # Look for the specific section that holds credential data
            section = soup.find("section", {"id": "aoYksTabContent"})
            if not section:
                print(f"[SKIP] No <section id='aoYksTabContent'> in {filename}")
                continue

            # Initialize variables for the credential fields
            program_title = ""
            program_code = ""
            program_desc = ""
            program_outcomes = ""
            framework_id = ""
            outcomes_list = []  # to store outcomes as a list for competencies

            # Loop over each label in the section
            for label_tag in section.find_all("h3", class_="field-label"):
                label_text = label_tag.get_text(strip=True)
                value_div = label_tag.find_next_sibling("div", class_="field-value")
                if not value_div:
                    continue

                # Get the text from the value div (preserving line breaks)
                value_text = value_div.get_text(separator="\n", strip=True)

                if "Program Title" in label_text:
                    program_title = value_text
                elif "Program Code" in label_text:
                    program_code = value_text
                elif "Program Description" in label_text:
                    program_desc = value_text
                elif "Graduates of this program will be able to:" in label_text:
                    # Generate a unique framework ID (for linking the outcomes)
                    framework_id = 'ce-' + str(uuid.uuid4())
                    # Process the outcomes (one per line; remove any leading dashes)
                    for line in value_text.splitlines():
                        line = line.strip()
                        if line.startswith("-"):
                            line = line[1:].strip()
                        if line:
                            line = format_outcome(line)
                        if line:
                            outcomes_list.append(line)
                    # Also create a pipe-delimited string for the credentials CSV
                    program_outcomes = "|".join(outcomes_list)

            # Determine credential type from program title (based on the text after a comma)
            if "," in program_title:
                type_ = program_title.split(",", 1)[1].strip()
            else:
                type_ = ""
            CE_type = type_mapping.get(type_, 'Certificate')

            # Extract credits from the entire HTML text using a regex
            pattern = r"(total credits required for degree|<strong>total credits|total credits|credit required for degree):\s*(\d+)"
            match = re.search(pattern, soup.text, re.IGNORECASE)
            credits_ = match.group(2) if match else ""

            # Write the credentials row to the CSV
            writer.writerow([filename, program_title, CE_type, credits_, program_code, program_desc, framework_id])
            print(f"[OK] Processed {filename}")

            # --- Build the competency framework and competency entries ---

            # Create a competency framework entry (similar to Script #2)
            if framework_id:
                competency_framework_entry = {
                    "ceasn:comment": program_title,
                    "@id": framework_id,
                    "@type": "ceasn:CompetencyFramework",
                    "ceasn:description": "Upon completion of this program students will be able to:",
                    "ceasn:inLanguage": "en",
                    "ceasn:name": f"{program_title}'s Program Learning Outcomes",
                    "ceasn:publicationStatusType": "http://credreg.net/ctdlasn/vocabs/publicationStatus/Published",
                    "ceasn:source": url
                }
                competency_data.append(competency_framework_entry)

                # For each outcome in the list, create a separate competency entry
                for outcome in outcomes_list:
                    competency_entry = {
                        "@id": 'ce-' + str(uuid.uuid4()),
                        "@type": "ceasn:Competency",
                        "ceasn:inLanguage": "en",
                        "ceasn:competencyLabel": "Program Learning Outcome",
                        "ceasn:competencyText": outcome,
                        "ceasn:isPartOf": framework_id
                    }
                    competency_data.append(competency_entry)

    print(f"\nDone. Credentials CSV saved to: {output_csv}")

    # Convert the competency data list into a DataFrame and save it as CSV.
    # (Note: Because the competency rows use slightly different keys, missing values will appear as empty cells.)
    df_competency = pd.DataFrame(competency_data)
    df_competency.to_csv(output_competency_csv, index=False, encoding="utf-8-sig")
    print(f"Competency CSV saved to: {output_competency_csv}")

if __name__ == "__main__":
    main()
