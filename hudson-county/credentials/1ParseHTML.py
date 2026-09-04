import os
import csv
from bs4 import BeautifulSoup

def main():
    input_html = r"C:\text\NJ\Hudson County\Credentials\Explore All Programs _ Programs and Courses _ Hudson County Community College.html"
    output_csv = r"C:\text\NJ\Hudson County\Credentials\parsed_programs.csv"

    # Prepare CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        # Write header row
        writer.writerow([
            "Credential Title",   # from <a title="...">
            "Subject Webpage",    # from <a href="...">
            "Last Word",          # from <span class="last-word">
            "Credential Type"     # from <div class="program-list__type">
        ])

        # Check if the input HTML file exists
        if not os.path.exists(input_html):
            print(f"[ERROR] File not found: {input_html}")
            return

        # Read/parse the HTML
        with open(input_html, "r", encoding="utf-8") as f_in:
            html_data = f_in.read()

        soup = BeautifulSoup(html_data, "lxml")

        # Find all <div class="program-list__item">
        items = soup.find_all("div", class_="program-list__item")

        for item in items:
            # 1) The <a> inside <div class="program-list__program">
            a_block = item.find("div", class_="program-list__program")
            if not a_block:
                continue

            link = a_block.find("a")
            if not link:
                continue

            credential_title = link.get("title", "").strip()    # e.g. "Business Administration Fully Online"
            subject_webpage = link.get("href", "").strip()      # e.g. "https://www.hccc.edu/programs-courses/..."
            
            # 2) The <span class="last-word"> if present
            last_word_span = link.find("span", class_="last-word")
            last_word = last_word_span.get_text(strip=True) if last_word_span else ""

            # 3) The credential type from <div class="program-list__type">
            cred_type_div = item.find("div", class_="program-list__type")
            credential_type = cred_type_div.get_text(strip=True) if cred_type_div else ""

            # Write row to CSV
            writer.writerow([credential_title, subject_webpage, last_word, credential_type])

    print(f"Done. Results written to: {output_csv}")

if __name__ == "__main__":
    main()
