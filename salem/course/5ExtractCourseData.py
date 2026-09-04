import csv
import re
import sys
from pathlib import Path

import pdfplumber

sys.stdout.reconfigure(encoding="utf-8")

PDF_DIR = Path(r"C:\text\NJ\Salem\course\CoursePDF")
OUT_CSV = Path(r"C:\text\NJ\Salem\course\SCC_course_outlines.csv")

CSV_COLUMNS = [
    "filename",
    "course_code",
    "course_title",
    "lecture_hours",
    "lab_hours",
    "credits",
    "prerequisite",
    "co_requisite",
    "curriculum_placement",
    "revision_date",
    "catalog_description",
    "general_education_requirements",
    "course_objectives",
]


def clean(s: str) -> str:
    if not s:
        return ""
    s = s.strip()
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n+", " ", s)
    return s.strip()


def extract_full_text(pdf) -> str:
    return "\n".join(p.extract_text() for p in pdf.pages if p.extract_text())


# -----------------------------------------------------------------------
# Section I field parsing
# -----------------------------------------------------------------------

def parse_section_i(full_text: str) -> dict:
    """
    Extract labeled Section I fields.  Uses the full PDF text so that
    cover-sheet PDFs (where page 1 is a cover sheet) are handled correctly —
    the field regexes all require a colon, so they naturally skip cover-sheet
    labels that lack them.
    """
    result = {}

    # Course Title: value on same line (with colon label)
    m = re.search(
        r"Course Title:\s*(.+?)(?=\nCourse (?:Code|Number):\s*|\Z)",
        full_text, re.IGNORECASE | re.DOTALL,
    )
    result["course_title"] = clean(m.group(1)) if m else ""

    # Course Code — handles "Course Code: ACC131", "Course Code: ENG 101",
    # "Course Code: NUR-230", "Code: NUR-231", "Course Syllabus: HUM 101"
    CODE_RE = re.compile(
        r"(?:Course (?:Code|Number)|Code):\s*([A-Za-z]{2,5}[-\s]?\d{3}[A-Za-z]?)"
        r"|Course Syllabus:\s*([A-Za-z]{2,5}[-\s]?\d{3}[A-Za-z]?)",
        re.IGNORECASE,
    )
    m = CODE_RE.search(full_text)
    if m:
        raw_code = (m.group(1) or m.group(2) or "").strip()
        result["course_code"] = re.sub(r"\s+", " ", raw_code)
    else:
        result["course_code"] = ""

    # Lecture Hours
    m = re.search(r"Lecture Hours?:\s*(\d+)", full_text, re.IGNORECASE)
    result["lecture_hours"] = m.group(1) if m else ""

    # Lab / Laboratory Hours
    m = re.search(r"Lab(?:oratory)? Hours?:\s*(\d+)", full_text, re.IGNORECASE)
    result["lab_hours"] = m.group(1) if m else ""

    # Credits
    m = re.search(r"Credits?:\s*(\d+)", full_text, re.IGNORECASE)
    result["credits"] = m.group(1) if m else ""

    # Course Description — stop at next labeled field or section marker
    m = re.search(
        r"Course Description:?\s*(.*?)"
        r"(?=Prerequisites?:|Co-requisites?:|Place in College|Date of Last|Section [IVX]\b|\Z)",
        full_text, re.DOTALL | re.IGNORECASE,
    )
    raw = clean(m.group(1)) if m else ""
    # Some PDFs repeat the label inside the value
    raw = re.sub(r"^Course Description:\s*", "", raw, flags=re.IGNORECASE)
    result["catalog_description"] = raw

    # Prerequisite
    m = re.search(
        r"Prerequisites?:?\s*(.*?)"
        r"(?=Co-requisites?:|Place in College|Date of Last|Section [IVX]\b|\Z)",
        full_text, re.DOTALL | re.IGNORECASE,
    )
    result["prerequisite"] = clean(m.group(1)) if m else ""

    # Co-requisite
    m = re.search(
        r"Co-requisites?:?\s*(.*?)"
        r"(?=Place in College|Date of Last|Section [IVX]\b|\Z)",
        full_text, re.DOTALL | re.IGNORECASE,
    )
    result["co_requisite"] = clean(m.group(1)) if m else ""

    # Place in College Curriculum
    m = re.search(
        r"Place in College Curriculum:?\s*(.*?)"
        r"(?=Date of Last|Section [IVX]\b|\Z)",
        full_text, re.DOTALL | re.IGNORECASE,
    )
    result["curriculum_placement"] = clean(m.group(1)) if m else ""

    # Date of Last Revisions (single line)
    m = re.search(r"Date of Last Revisions?:?\s*(.+)", full_text, re.IGNORECASE)
    result["revision_date"] = clean(m.group(1)) if m else ""

    return result


# -----------------------------------------------------------------------
# General Education
# -----------------------------------------------------------------------

def parse_general_education(full_text: str) -> str:
    m = re.search(
        r"General Education Requirements?:?\s*(.*?)"
        r"(?=Section [IVX]\b|Outcomes Assessment|Course Activities|\Z)",
        full_text, re.DOTALL | re.IGNORECASE,
    )
    return clean(m.group(1)) if m else ""


# -----------------------------------------------------------------------
# Course Objectives / Learning Outcomes
# -----------------------------------------------------------------------

def _extract_items(section: str) -> list:
    """
    Extract list items from an objectives section.
    Handles lettered items (A. B. C.) and numbered items (1. 2. 3.).
    Returns cleaned strings, joined as ' | ' by caller.
    """
    # Try lettered first (A. B. C.) — typical for lettered Learning Outcomes
    lettered = re.findall(
        r"(?m)^[A-Z]\.\s+(.+?)(?=\n[A-Z]\.\s+|\nCourse Performance Objective|\Z)",
        section, re.DOTALL,
    )
    lettered = [clean(i) for i in lettered if clean(i)]

    # Numbered items (1. 2. 3.)
    numbered_raw = re.split(r"(?m)^\s*\d+\.\s+", section)
    numbered = []
    for part in numbered_raw[1:]:  # skip preamble before first number
        c = clean(part)
        if c and not re.match(
            r"^(?:the student(?:s)? will|at the end|upon successful)", c, re.IGNORECASE
        ):
            numbered.append(c)

    # Return whichever set is richer; if both, merge (prioritise lettered for LO sections)
    if lettered and len(lettered) >= len(numbered):
        return lettered
    if numbered:
        return numbered
    return lettered


def parse_objectives(full_text: str) -> str:
    """
    Extract course objectives/learning outcomes, handling all known formats.
    """
    # ---- Format 1: Section III block (most common) ----
    m = re.search(r"Section III(.*?)Section IV", full_text, re.DOTALL | re.IGNORECASE)
    if m:
        section = m.group(1)
        items = _extract_items(section)
        if items:
            return " | ".join(items)

    # ---- Format 2: Course Performance Objective blocks without Section III ----
    m = re.search(
        r"(Course Performance Objective.+?)"
        r"(?=Section IV|General Education Requirements?|Course Activities|\Z)",
        full_text, re.DOTALL | re.IGNORECASE,
    )
    if m:
        section = m.group(1)
        items = _extract_items(section)
        if items:
            return " | ".join(items)

    # ---- Format 3: Course Objectives: block ----
    m = re.search(
        r"Course Objectives?:?\s*(?:[^\n]*)?\s*(.*?)"
        r"(?=Course Activities?:|Course Requirements?|Attendance Policy|Section [IVX]|\Z)",
        full_text, re.DOTALL | re.IGNORECASE,
    )
    if m:
        section = m.group(1)
        items = _extract_items(section)
        if items:
            return " | ".join(items)

    return ""


# -----------------------------------------------------------------------
# Per-file processor
# -----------------------------------------------------------------------

def _code_from_filename(stem: str) -> tuple:
    """
    Derive course_code and course_title from filename like
    'ACC_131_-_Principles_of_Accounting_I'.
    Returns (code, title) strings.
    """
    parts = stem.split("_-_", 1)
    if len(parts) == 2:
        code = parts[0].replace("_", " ").strip()
        title = parts[1].replace("_", " ").strip()
    else:
        code = stem.split("_")[0]
        title = stem.replace("_", " ").strip()
    return code, title


def process_pdf(pdf_path: Path) -> dict:
    row = {col: "" for col in CSV_COLUMNS}
    row["filename"] = pdf_path.name

    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return row
            full_text = extract_full_text(pdf)

        # PDFs with no extractable text (scanned) or placeholder notices
        if not full_text.strip() or "Syllabus under review" in full_text:
            code, title = _code_from_filename(pdf_path.stem)
            row["course_code"] = code
            row["course_title"] = title
            return row

        # Skip non-syllabus PDFs (no course code field present)
        has_code = any(
            kw in full_text
            for kw in ("Course Code", "Course Number", "Code:", "Course Syllabus:")
        )
        if not has_code:
            return row

        row.update(parse_section_i(full_text))
        row["general_education_requirements"] = parse_general_education(full_text)
        row["course_objectives"] = parse_objectives(full_text)

        # Fallback: derive title from filename when PDF label was missing/unusual
        if not row["course_title"]:
            _, title = _code_from_filename(pdf_path.stem)
            row["course_title"] = title

    except Exception as e:
        print(f"  ERROR processing {pdf_path.name}: {e}")

    return row


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def main():
    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    total = len(pdf_files)
    print(f"Processing {total} PDFs...")

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()

        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"[{i}/{total}] {pdf_path.name}", flush=True)
            row = process_pdf(pdf_path)
            writer.writerow(row)

    print(f"\nDone. Output: {OUT_CSV}")


if __name__ == "__main__":
    main()
