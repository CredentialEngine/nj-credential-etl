import pdfplumber
import re
import csv
import os
from pathlib import Path

PDF_DIR = r"C:\text\NJ\Rowan College of South Jersey - Gloucester\2026\pdfs"
OUTPUT_CSV = r"C:\text\NJ\Mercer\2026\credit\RCSJ_Gloucester_courses.csv"

HEADERS = [
    "filename", "course_code", "course_title",
    "lecture_hours", "studio_hours", "credit_hours",
    "prerequisites", "catalog_description", "slos", "evaluations"
]

# Matches dept codes with optional space before digits: "BIO 101", "HIS101", "NURS 110"
COURSE_CODE_RE = re.compile(
    r'^\s*([A-Za-z]{2,5}\s*\d{3}[A-Za-z]?)\s*(?:[:\-\.\u2013\u2014]\s*|\s+)(.+)',
    re.MULTILINE
)
# Filename code pattern e.g. "SCI 301 Research Methods..." or "BIO107..."
FILENAME_CODE_RE = re.compile(r'^([A-Za-z]{2,5}\s*\d{3}[A-Za-z]?)\s+(.+?)(?:\s+ADA|\s+MS|\s+Master|\s+Syllabus|\.pdf)', re.IGNORECASE)
# Matches course codes in any context (for prerequisites)
CODE_ANYWHERE = re.compile(r'[A-Z]{2,5}\s*\d{3}[A-Za-z]?', re.IGNORECASE)


def normalize_code(code):
    """Ensure space between dept letters and digits: 'HIS101' -> 'HIS 101'"""
    code = re.sub(r'([A-Za-z]+)\s*(\d)', r'\1 \2', code.strip())
    return re.sub(r'\s+', ' ', code).upper()


def clean(text):
    if text is None:
        return ""
    return re.sub(r'\s+', ' ', str(text)).strip()


def parse_hours(page1_text):
    """Return (lecture_hours, studio_hours, credit_hours) as strings."""

    # ── Pattern 1: slash-separated with colon (standard ADA format) ──────
    # "Lecture Hours/Credits: 3/3"  or  "Lecture Hours/Lab Hours/Credits: 3/3/4"
    # Also handles missing colon: "LECTURE HOURS/CREDITS 1/1"
    # Also handles singular: "Lecture Hour/Credit: 1/1"
    hm = re.search(
        r'(?m)^[^\n]*(Lecture|Lab|Studio|Clinical|Activity)[^\n]*Credits?\s*:?\s*(\d[\d.]*)\s*/\s*(\d[\d.]*)(?:\s*/\s*(\d[\d.]*))?',
        page1_text, re.IGNORECASE
    )
    if hm:
        line_type = hm.group(1).upper()
        n1, n2, n3 = hm.group(2), hm.group(3), hm.group(4)
        if line_type == "LECTURE":
            if n3:
                return n1, n2, n3
            else:
                return n1, "0", n2
        else:
            if n3:
                return n1, n2, n3
            else:
                return "0", n1, n2

    # ── Pattern 2: natural-language "3 lecture hours / 3 credits" ─────────
    hm2 = re.search(
        r'(\d[\d.]*)\s+lecture\s+hours?\s*/\s*(?:(\d[\d.]*)\s+(?:lab|studio|clinical)\s+hours?\s*/\s*)?(\d[\d.]*)\s+credits?',
        page1_text, re.IGNORECASE
    )
    if hm2:
        lec = hm2.group(1)
        stu = hm2.group(2) or "0"
        cred = hm2.group(3)
        return lec, stu, cred

    # ── Pattern 3: comma-separated "2 Lecture Hours, 2 Credits" ──────────
    # Also: "4 Lecture Hours, 180 Clinical Hours, 8 Credits"
    lec_m  = re.search(r'(\d[\d.]*)\s+Lecture\s+Hours?', page1_text, re.IGNORECASE)
    clin_m = re.search(r'(\d[\d.]*)\s+(?:Clinical|Lab|Studio)\s+Hours?', page1_text, re.IGNORECASE)
    cred_m = re.search(r'(\d[\d.]*)\s+Credits?', page1_text, re.IGNORECASE)
    if lec_m and cred_m:
        lec  = lec_m.group(1)
        stu  = clin_m.group(1) if clin_m else "0"
        cred = cred_m.group(1)
        return lec, stu, cred

    return "", "", ""


def extract_course_info(pdf_path):
    filename = os.path.basename(pdf_path)
    full_text = ""
    page1_text = ""
    all_tables = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                if i == 0:
                    page1_text = text
                full_text += text + "\n"
                tables = page.extract_tables()
                if tables:
                    all_tables.extend(tables)
    except Exception as e:
        return {h: "" for h in HEADERS} | {"filename": filename, "catalog_description": f"ERROR: {e}"}

    # ── Course code and title ──────────────────────────────────────────────
    course_code = ""
    course_title = ""
    first_lines = page1_text.split('\n')[:14]
    for line in first_lines:
        m = COURSE_CODE_RE.match(line)
        if m:
            raw_code = m.group(1).strip()
            if re.match(r'^\d', raw_code):
                continue
            course_code = normalize_code(raw_code)
            title = clean(m.group(2))
            # If title starts with more course codes (multi-code file), strip them
            # e.g. "THR112, THR211, THR212: Acting Workshops I, II, III, IV"
            title = re.sub(r'^(?:[A-Za-z]{2,5}\s*\d{3}[,.\s]+)+', '', title)
            title = title.lstrip(':, ').strip()
            # Strip trailing section info like "- 02"
            title = re.sub(r'\s*[-–]\s*\d{2,3}$', '', title)
            title = re.sub(r'\s*[Ss]ection\s*\d+.*$', '', title)
            title = re.sub(r'\s*[Ss][Yy][Ll][Ll][Aa][Bb][Uu][Ss]\s*$', '', title).strip()
            course_title = title
            break

    # Fallback: try to extract code + title from filename
    if not course_code:
        stem = os.path.splitext(filename)[0]
        fm = FILENAME_CODE_RE.match(stem)
        if fm:
            course_code = normalize_code(fm.group(1))
            course_title = clean(fm.group(2))

    # ── Hours / Credits ────────────────────────────────────────────────────
    lecture_hours, studio_hours, credit_hours = parse_hours(page1_text)

    # ── Prerequisites ──────────────────────────────────────────────────────
    prerequisites = ""
    pm = re.search(r'Prerequisite[s]?:\s*(.+)', page1_text, re.IGNORECASE)
    if pm:
        prereq_raw = pm.group(1).strip()
        codes = CODE_ANYWHERE.findall(prereq_raw)
        codes = [normalize_code(c) for c in codes]
        prerequisites = "|".join(codes) if codes else clean(prereq_raw)

    # ── Catalog Description ────────────────────────────────────────────────
    catalog_desc = ""
    cd_m = re.search(
        r'Prerequisite[s]?:.*?\n(.*?)(?=Textbook|Course Materials)',
        page1_text, re.DOTALL | re.IGNORECASE
    )
    if cd_m:
        catalog_desc = clean(cd_m.group(1))
    else:
        cd_m2 = re.search(
            r'(?:Catalog Description|CATALOG DESCRIPTION)\s*\n(.*?)(?=Textbook|Course Materials|TEXTBOOK)',
            page1_text, re.DOTALL | re.IGNORECASE
        )
        if cd_m2:
            catalog_desc = clean(cd_m2.group(1))

    # ── SLOs & Evaluations from the SLO table ─────────────────────────────
    slos = []
    evaluations_raw = []

    for table in all_tables:
        if not table or len(table) < 2:
            continue
        # Only 3-column tables
        col_counts = [len(r) for r in table if r]
        if not col_counts or max(col_counts) != 3:
            continue
        header_row = table[0] or []
        header_text = " ".join(clean(c) for c in header_row if c)
        if not any(kw in header_text for kw in
                   ("Competenc", "Evaluation", "help student", "will help")):
            continue

        for row in table[1:]:
            if not row or len(row) < 3:
                continue
            slo_cell  = row[0]
            eval_cell = row[2]

            if slo_cell and str(slo_cell).strip():
                slos.append(clean(slo_cell))

            if eval_cell and str(eval_cell).strip():
                for line in str(eval_cell).split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    # Lowercase start → continuation of previous item
                    if line[0].islower() and evaluations_raw:
                        evaluations_raw[-1] = evaluations_raw[-1].rstrip(',') + ' ' + line
                        continue
                    if re.search(r',\s+\w', line):
                        for sub in line.split(','):
                            sub = sub.strip()
                            if sub:
                                evaluations_raw.append(sub)
                    else:
                        evaluations_raw.append(line.rstrip(',').strip())

    # Deduplicate evaluations preserving order
    seen = set()
    unique_evals = []
    for e in evaluations_raw:
        if e.lower() not in seen:
            seen.add(e.lower())
            unique_evals.append(e)

    return {
        "filename":            filename,
        "course_code":         course_code,
        "course_title":        course_title,
        "lecture_hours":       lecture_hours,
        "studio_hours":        studio_hours,
        "credit_hours":        credit_hours,
        "prerequisites":       prerequisites,
        "catalog_description": catalog_desc,
        "slos":                "|".join(slos),
        "evaluations":         "|".join(unique_evals),
    }


def main():
    pdf_files = sorted(Path(PDF_DIR).glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files")

    rows = []
    errors = []
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] {pdf_path.name}")
        info = extract_course_info(str(pdf_path))
        rows.append(info)
        if info["catalog_description"].startswith("ERROR"):
            errors.append(pdf_path.name)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone. {len(rows)} rows written to {OUTPUT_CSV}")
    if errors:
        print(f"Errors in {len(errors)} files: {errors}")


if __name__ == "__main__":
    main()
