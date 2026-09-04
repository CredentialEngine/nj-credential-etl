from pathlib import Path
import csv
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote
import os

CSV_PATH = r"C:\text\NJ\Rowan College of South Jersey - Gloucester\2026\RCSJ_SourthJersey_BU_courses.csv"
HTML_PATH = r"C:\text\NJ\Rowan College of South Jersey - Gloucester\2026\Rowan College (Gloucester) Course Syllabi _ Gloucester Syllabi _ Rowan College South Jersey.html"


def normalize_filename(value: str) -> str:
    """Normalize a filename for matching."""
    return os.path.basename(unquote((value or "").strip())).lower()


def build_pdf_url_map(html_path: str) -> dict:
    """
    Read the saved HTML file and build a mapping:
    pdf filename -> full URL
    """
    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "html.parser")

    pdf_map = {}

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href:
            continue

        # Match links that point to PDFs
        if ".pdf" not in href.lower():
            continue

        # Use the filename from the URL path as the lookup key
        parsed = urlparse(href)
        filename_from_url = normalize_filename(parsed.path)

        if filename_from_url:
            pdf_map[filename_from_url] = href

        # Also try the anchor text in case the saved HTML uses odd URL paths
        anchor_text = normalize_filename(a.get_text(" ", strip=True))
        if anchor_text.endswith(".pdf") and href:
            pdf_map[anchor_text] = href

    return pdf_map


def update_csv_subject_webpage(csv_path: str, pdf_map: dict) -> None:
    """
    For each row in the CSV, look up External Identifier as a PDF filename
    and write the matching URL into Subject Webpage.
    """
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    if not fieldnames:
        raise ValueError("CSV appears to have no header row.")

    if "External Identifier" not in fieldnames:
        raise ValueError("CSV is missing required column: External Identifier")

    if "Subject Webpage" not in fieldnames:
        raise ValueError("CSV is missing required column: Subject Webpage")

    updated = 0
    unmatched = []

    for row in rows:
        ext_id = (row.get("External Identifier") or "").strip()
        key = normalize_filename(ext_id)

        if not key:
            continue

        url = pdf_map.get(key)
        if url:
            row["Subject Webpage"] = url
            updated += 1
        else:
            unmatched.append(ext_id)

    backup_path = str(Path(csv_path).with_suffix(".bak.csv"))
    os.replace(csv_path, backup_path)

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated rows: {updated}")
    print(f"Backup created: {backup_path}")

    if unmatched:
        print("\nNo matching URL found for these External Identifier values:")
        for item in unmatched:
            print(f" - {item}")


if __name__ == "__main__":
    pdf_url_map = build_pdf_url_map(HTML_PATH)
    update_csv_subject_webpage(CSV_PATH, pdf_url_map)