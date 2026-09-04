import os
import csv
import re
from bs4 import BeautifulSoup

#Define type mappings to CTDL
type_mapping= {
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
    input_folder = r"C:\text\NJ\Brookdale\credentials\CredentialHTML"
    output_csv = r"C:\text\NJ\Brookdale\credentials\parsed_credentials.csv"

    # Prepare CSV for writing
    with open(output_csv, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        # Write header row (now with "Outcomes" too)
        writer.writerow(["Filename", "Program Title", "Type", "Credits", "Program Code", "Program Description", "Outcomes"])

        # Loop over every HTML file in the directory
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

            # Try to find the <section> with id="aoYksTabContent"
            section = soup.find("section", {"id": "aoYksTabContent"})
            if not section:
                # If not found, skip
                print(f"[SKIP] No <section id='aoYksTabContent'> in {filename}")
                continue

            # Extract Program Title, Code, and Description from that section
            program_title = ""
            program_code = ""
            program_desc = ""
            program_outcomes = ""  # new field for outcomes

            # For each <h3 class="field-label"> in the section
            for label_tag in section.find_all("h3", class_="field-label"):
                label_text = label_tag.get_text(strip=True)

                # The matching <div class="field-value"> is the next sibling
                value_div = label_tag.find_next_sibling("div", class_="field-value")
                if not value_div:
                    continue

                # Get its text (with possible line breaks)
                # 'separator="\n"' ensures that <br> or other tags become line breaks
                value_text = value_div.get_text(separator="\n", strip=True)

                # Match labels to known fields
                if "Program Title" in label_text:
                    program_title = value_text
                elif "Program Code" in label_text:
                    program_code = value_text
                elif "Program Description" in label_text:
                    program_desc = value_text
                elif "Graduates of this program will be able to:" in label_text:
                    # We have outcomes lines
                    # We'll split on new lines, strip dashes, and rejoin with '|'
                    lines = []
                    for line in value_text.splitlines():
                        line = line.strip()
                        # If the line starts with a dash, remove it
                        if line.startswith("-"):
                            line = line[1:].strip()
                        if line:
                            lines.append(line)
                    # Join with pipe
                    program_outcomes = "|".join(lines)
                
                #Figure out credential type
                #Extract text after the first comma
                type_ = program_title.split(",", 1)[1].strip() if "," in program_title else ""
                #If the mapping isn't sufficient, just assign the credential to type Certificate.
                CE_type = type_mapping.get(type_, 'Certificate')
                
                # Extract the text content and search for the credits value using case-insensitive regex
                pattern = r"(total credits required for degree|credit required for degree):\s*(\d+)"
                match = re.search(pattern, soup.text, re.IGNORECASE)
                # Assign the extracted credits value to the variable 'credits'
                credits_ = match.group(2) if match else None

            # Write the row to CSV (including outcomes)
            writer.writerow([filename, program_title, CE_type, credits_, program_code, program_desc, program_outcomes])
            print(f"[OK] Processed {filename}")

    print(f"\nDone. CSV saved to: {output_csv}")


if __name__ == "__main__":
    main()
