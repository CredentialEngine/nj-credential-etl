import os
import csv
from bs4 import BeautifulSoup

def main():
    # Get the current working directory
    current_dir = os.getcwd()
    # Define the relative subdirectory
    input_folder = os.path.join(current_dir, "CredentialHTML")
    output_csv = os.path.join(current_dir, "parsed_credentials.csv")

    # Prepare CSV for writing
    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f_out:
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

            # Extract program title
            title_tag = section.find("div", class_="pr-2")
            if title_tag:
                program_title = title_tag.get_text(strip=True)

            # Extract program description
            desc_label = section.find("label", text="Description")
            if desc_label:
                desc_div = desc_label.find_next("div")
                if desc_div:
                    program_desc = desc_div.get_text(separator=" ", strip=True)

            # Extract program outcomes
            outcomes_label = section.find("p", string="PROGRAM OUTCOMES")
            if outcomes_label:
                outcomes = []
                for outcome in outcomes_label.find_next_siblings("p"):
                    outcome_text = outcome.get_text(strip=True)
                    # Clean up outcomes by removing leading bullets or inconsistent punctuation
                    outcome_text = outcome_text.lstrip("• ").rstrip(";.")
                    if outcome_text:
                        outcomes.append(outcome_text)
                program_outcomes = " | ".join(outcomes)

            # Write the row to CSV
            writer.writerow([filename, program_title, program_code, program_desc, program_outcomes])
            print(f"[OK] Processed {filename}")

    print(f"\nDone. CSV saved to: {output_csv}")

if __name__ == "__main__":
    main()
