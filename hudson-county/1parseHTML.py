import os
import csv
from bs4 import BeautifulSoup

def main():
    input_html = r"C:\text\NJ\Hudson County\Courses.html"
    output_csv = r"C:\text\NJ\Hudson County\courses_parsed.csv"

    # Prepare CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        # Write header row
        writer.writerow([
            "data_subject",
            "course_number",       # e.g. "THA-208"
            "course_number_url",   # e.g. "https://www.hccc.edu/catalog/current/courses/tha/tha-208.html"
            "course_title",        # e.g. "Contemporary Drama"
            "course_credits",      # e.g. "3 Credits"
            "course_description"
        ])

        # Read and parse the HTML
        if not os.path.exists(input_html):
            print(f"[ERROR] File not found: {input_html}")
            return

        with open(input_html, "r", encoding="utf-8") as f_in:
            html_data = f_in.read()

        soup = BeautifulSoup(html_data, "lxml")

        # Find all <tr> elements that contain data-subject
        rows = soup.find_all("tr", attrs={"data-subject": True})

        for row in rows:
            # 1) data-subject from row's attribute
            data_subject = row.get("data-subject", "").strip()

            # 2) Inside the row, find the <div class="catalog-course-list__number">
            course_number_div = row.find("div", class_="catalog-course-list__number")
            course_number = ""
            course_number_url = ""
            if course_number_div:
                a_tag = course_number_div.find("a")
                if a_tag:
                    course_number = a_tag.get_text(strip=True)
                    course_number_url = a_tag.get("href", "")

            # 3) Find the <h2> that has the course title + <span> credits
            #    It's typically <h2><a>Title</a><span>3 Credits</span></h2>
            course_title = ""
            course_credits = ""
            prereq = ""
            h2_tag = row.find("h2")
            if h2_tag:
                # The course title is often in the <a> inside <h2>
                a_tag_in_h2 = h2_tag.find("a")
                if a_tag_in_h2:
                    course_title = a_tag_in_h2.get_text(strip=True)

                # The credits might be in <span class="catalog-course-list__credit">
                span_credits = h2_tag.find("span", class_="catalog-course-list__credit")
                if span_credits:
                    course_credits = span_credits.get_text(strip=True)

            # 4) The <p> containing course description
            #    There's likely only one <p> in that <td>.
            course_description = ""
            p_tag = row.find("p")
            if p_tag:
                # Get the text with strip=True to remove leading/trailing whitespace
                text_raw = p_tag.get_text(strip=True)
                # Convert any internal newlines/tabs/multiple spaces into single spaces
                course_description = " ".join(text_raw.split())

            # Write out to CSV
            writer.writerow([
                data_subject,
                course_number,
                course_number_url,
                course_title,
                course_credits,
                course_description
            ])

    print(f"Done. Results written to: {output_csv}")

if __name__ == "__main__":
    main()
