import os
import csv
from bs4 import BeautifulSoup

def main():
    input_folder = r"C:\text\NJ\Rowan College at Burlington\credentials\CredentialHTML"
    output_csv = r"C:\text\NJ\Rowan College at Burlington\credentials\parsed_credentials.csv"

    # Prepare CSV for writing
    with open(output_csv, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        # Write header row (including Outcomes)
        writer.writerow(["Filename", "Program Title", "Program Code", "Program Description", "Outcomes"])

        # Loop over every HTML file in the directory
        for filename in os.listdir(input_folder):
            if not filename.lower().endswith(".html"):
                continue  # Skip non-HTML files

            full_path = os.path.join(input_folder, filename)
            try:
                with open(full_path, "r", encoding="utf-8") as f_in:
                    html = f_in.read()
            except (UnicodeDecodeError, OSError) as e:
                print(f"[ERROR] Cannot read {filename}: {e}")
                continue

            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(html, "lxml")

            # Find the <section> with id="aoYksTabContent"
            section = soup.find("section", {"id": "aoYksTabContent"})
            if not section:
                print(f"[SKIP] No <section id='aoYksTabContent'> in {filename}")
                continue

            # Initialize fields
            program_title = ""
            program_code = ""
            program_desc = ""
            program_outcomes = ""

            # Extract field values
            for label_tag in section.find_all("h3", class_="field-label"):
                label_text = label_tag.get_text(strip=True)
                value_div = label_tag.find_next_sibling("div", class_="field-value")

                if not value_div:
                    continue

                value_text = value_div.get_text(separator="\n", strip=True)

                # Match and assign values
                if "Degree Title" in label_text:
                    program_title = value_text
                elif "Program Description" in label_text:
                    program_desc = value_text
            # Extract outcomes based on the div tag with id="learningOutcomes"
            outcomes_div = section.find("div", {"id": "learningOutcomes"})
            if outcomes_div:
                outcomes = []
                for outcome_div in outcomes_div.find_all("div", class_="field-value"):
                    if outcome_div.get_text(strip=True):
                        outcomes.append(outcome_div.get_text(strip=True))
                program_outcomes = "|".join(outcomes)

            # Write the row to CSV
            writer.writerow([filename, program_title, program_code, program_desc, program_outcomes])
            print(f"[OK] Processed {filename}")

    print(f"\nDone. CSV saved to: {output_csv}")

if __name__ == "__main__":
    main()
