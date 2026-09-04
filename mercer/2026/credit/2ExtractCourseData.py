import csv
import re
from pathlib import Path

import pdfplumber


PDF_DIR = Path(r"C:\text\NJ\Mercer\2026\credit\pdfs")
OUT_CSV = Path(r"C:\text\NJ\Mercer\2026\credit\course_outlines.csv")

CSV_COLUMNS = [
    "filename",
    "course_number",
    "course_title",
    "credits",
    "hours",
    "co_or_pre_requisite",
    "implementation_semester_year",
    "catalog_description",
    "general_education_category",
    "slos",
    "ilgs",
    "plos",
    "evaluation_of_student_learning",
]

FOOTER_RE = re.compile(r"MCCC Course Outline[;,][^\n]+\n?", re.IGNORECASE)

SKIP_FILENAMES = {
    "strategic_plan_21-26.pdf",
    "general-ed_recommended.pdf",
    "opra request.pdf",
}

# Hand-coded overrides for PDFs whose headers can't be auto-parsed
# (roman-numeral credits, no credits on header line, etc.)
MANUAL_OVERRIDES = {
    "amt291.pdf": {"course_number": "AMT 291", "course_title": "Advanced Manufacturing Internship", "credits": "3.0"},
    "avi132.pdf": {"course_number": "AVI 132", "course_title": "Commercial Pilot II", "credits": "3"},
    "mus170.pdf": {"course_number": "MUS 170", "course_title": "Chamber Ensemble I", "credits": "1"},
    "mus174.pdf": {"course_number": "MUS 174", "course_title": "Chorus I", "credits": "1"},
    "mus275.pdf": {"course_number": "MUS 275", "course_title": "Chorus IV", "credits": "1"},
}

# Strip "[Supports ILG # X; PLO #Y]" reference tags from SLO items.
# Some PDFs close with ) instead of ], so match from [Supports to end of item.
SLO_BRACKET_RE = re.compile(r"\s*\[Supports\b.*$", re.IGNORECASE)

# Label words in the hours/prereq/impl block to skip
HOURS_LABEL_WORDS = {
    "hours", "hours:", "implementation", "implementation:", "lecture/lab/other",
    "lecture/lab/other:", "lecture/lab:", "lab/lecture/other", "semester",
    "semester:", "year", "year:", "sem/year", "semester/year", "semester&",
    "&", "year:",
}

PREREQ_LABEL_WORDS = {
    "co-", "co-or", "pre-requisite", "pre-requisite:", "prerequisite",
    "prerequisite:", "co-", "co-or-pre-requisite",
}

GENED_LABEL_WORDS = {"general", "education", "category", "general:", "education:"}


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def clean_text(s: str) -> str:
    if not s:
        return ""
    s = s.strip()
    # Replace pdfplumber encoding artifacts: bullet chars and dashes decoded as replacement char
    s = s.replace("\ufffd", "\u2022")   # U+FFFD → bullet •
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n+", " ", s)
    return s.strip()


def normalize_gened(s: str) -> str:
    """Standardize GenEd category spelling variations and strip form artifacts."""
    if not s:
        return s
    # "Not Gen Ed" → "Not GenEd"
    s = re.sub(r"\bNot\s+Gen\s+Ed\b", "Not GenEd", s, flags=re.IGNORECASE)
    # Strip dropdown placeholder text left in some PDFs
    s = re.sub(r"\s*Choose an item\.?\s*", "", s, flags=re.IGNORECASE)
    return s.strip()


def load_all_pdfs(pdf_dir: Path) -> list:
    return sorted(pdf_dir.glob("*.pdf"))


def extract_full_text(pdf) -> str:
    pages = []
    for page in pdf.pages:
        t = page.extract_text()
        if t:
            pages.append(t)
    raw = "\n".join(pages)
    return FOOTER_RE.sub("", raw)


def is_course_outline(text: str, filename: str) -> bool:
    if filename.lower() in SKIP_FILENAMES:
        return False
    return bool(re.search(
        r"Course\s+(?:Number|No\.?)\s+Course\s+(?:Title|Name)\s+Credits",
        text, re.IGNORECASE
    ))


# ---------------------------------------------------------------------------
# Header table: course number, title, credits  (text-regex approach)
# ---------------------------------------------------------------------------

# Matches:  "ADV 101 Advertising Design I 3"
#           "CMN-157 Podcasting 3"
#           "FAS 105 Fashion: The Global Marketplace 3 credits"
#           "ENG-101 English Composition I 3.0"
#           "MUS170 Chamber Ensemble I 1"
COURSE_LINE_RE = re.compile(
    r"^([A-Za-z]{2,5}-?\s*\d{3}[A-Za-z]?)\s+(.+?)\s+(\d+\.?\d*)\s*(?:credits?)?\s*$",
    re.IGNORECASE,
)
# Matches: "EDU 210 6"  (course num + credits, no title on same line)
COURSE_NUM_CREDITS_RE = re.compile(
    r"^([A-Za-z]{2,5}-?\s*\d{3}[A-Za-z]?)\s+(\d+\.?\d*)\s*(?:credits?)?\s*$",
    re.IGNORECASE,
)
# Matches any course number prefix (possibly alone on a line)
COURSE_NUM_PREFIX_RE = re.compile(
    r"^([A-Za-z]{2,5}-?\s*\d{3}[A-Za-z]?)\s*(.*)",
    re.IGNORECASE,
)
CREDITS_SUFFIX_RE = re.compile(r"\b(\d+\.?\d*)\s*(?:credits?)?\s*$", re.IGNORECASE)
HOURS_BLOCK_START_RE = re.compile(
    r"^(?:Hours|Lecture|Lab|Co-|Pre-|Implementation|Semester|Catalog)",
    re.IGNORECASE,
)


def _try_full_line(line: str):
    """Try 'COURSE_NUM TITLE CREDITS' on one line. Returns (num, title, credits) or None."""
    m = COURSE_LINE_RE.match(line)
    if m:
        return m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
    return None


def parse_header_course_line(text: str) -> tuple:
    """Extract course number, title, credits from the header block."""
    lines = text.split("\n")
    header_idx = None
    for i, line in enumerate(lines):
        if re.search(r"Course\s+(?:Number|No\.?)\s+Course\s+(?:Title|Name)\s+Credits",
                     line, re.IGNORECASE):
            header_idx = i
            break

    if header_idx is None:
        return "", "", ""

    # Some PDFs place data BEFORE the header row (e.g. avi-style)
    for i in range(max(0, header_idx - 3), header_idx):
        result = _try_full_line(lines[i].strip())
        if result:
            return result

    # Collect candidate lines after the header, stopping at Hours block
    candidates = []
    for line in lines[header_idx + 1: header_idx + 8]:
        stripped = line.strip()
        if not stripped:
            continue
        if HOURS_BLOCK_START_RE.match(stripped):
            break
        candidates.append(stripped)

    if not candidates:
        return "", "", ""

    # Pattern A: full info on one line
    result = _try_full_line(candidates[0])
    if result:
        return result

    # Pattern B: "COURSE_NUM CREDITS" only, title on next line (edu210 style)
    m2 = COURSE_NUM_CREDITS_RE.match(candidates[0])
    if m2 and len(candidates) > 1:
        return m2.group(1).strip(), candidates[1].strip(), m2.group(2).strip()

    # Pattern C: course number prefix found on candidates[0]
    m3 = COURSE_NUM_PREFIX_RE.match(candidates[0])
    if m3:
        course_num = m3.group(1).strip()
        leftover = m3.group(2).strip()
        if leftover:
            # Leftover may be partial title; credits might be in leftover or next line
            cr_m = CREDITS_SUFFIX_RE.search(leftover)
            if cr_m:
                title = leftover[:cr_m.start()].strip()
                return course_num, title, cr_m.group(1)
            # No credits in leftover — check next candidate
            if len(candidates) > 1:
                cr_m2 = CREDITS_SUFFIX_RE.search(candidates[1])
                if cr_m2:
                    title = (leftover + " " + candidates[1][:cr_m2.start()]).strip()
                    return course_num, title, cr_m2.group(1)
        else:
            # Course number alone — title+credits on next line
            if len(candidates) > 1:
                result2 = _try_full_line(candidates[1])
                if result2:
                    # result2 course_num is wrong (it's the title); use our course_num
                    # Actually _try_full_line matched "Title 3" as "Title" + credits only if it looks like course num
                    # More reliable: parse title+credits from candidates[1] directly
                    pass
                cr_m = CREDITS_SUFFIX_RE.search(candidates[1])
                if cr_m:
                    title = candidates[1][:cr_m.start()].strip()
                    return course_num, title, cr_m.group(1)

    # Pattern D: title comes first, course number appears on a later candidate line
    for i, cand in enumerate(candidates[1:], 1):
        m_below = COURSE_NUM_PREFIX_RE.match(cand)
        if m_below:
            course_num = m_below.group(1).strip()
            # Title = candidates[0] (possibly multi-line)
            title_parts = [candidates[0]]
            for j in range(1, i):
                title_parts.append(candidates[j])
            title = " ".join(title_parts).strip()
            # Credits: in leftover of this line, or candidates[0], or next line
            leftover2 = m_below.group(2).strip()
            cr_m = CREDITS_SUFFIX_RE.search(leftover2) if leftover2 else None
            if not cr_m:
                cr_m = CREDITS_SUFFIX_RE.search(candidates[0])
            if not cr_m and i + 1 < len(candidates):
                cr_m = CREDITS_SUFFIX_RE.search(candidates[i + 1])
            credits = cr_m.group(1) if cr_m else ""
            # Strip trailing credits from title if present
            if credits:
                title = re.sub(r"\s+" + re.escape(credits) + r"\s*(?:credits?)?\s*$",
                               "", title, flags=re.IGNORECASE).strip()
            return course_num, title, credits

    return "", "", ""


# ---------------------------------------------------------------------------
# Header table: hours, prereq, implementation  (position-based)
# ---------------------------------------------------------------------------

def get_page1_column_anchors(words: list) -> dict:
    """Derive x-coordinate column split thresholds from page 1 word positions."""
    credits_word = next(
        (w for w in words if w["text"].lower() == "credits"), None
    )
    if not credits_word:
        return {}

    credits_x0 = credits_word["x0"]
    header_top = credits_word["top"]

    # Words on the same row as Credits (±3 pts)
    header_row = [w for w in words if abs(w["top"] - header_top) < 3]

    number_x1 = next(
        (w["x1"] for w in header_row if w["text"].lower() == "number"),
        credits_x0 * 0.25,
    )

    # Second "Course" word begins the title column header
    course_words = [w for w in header_row if w["text"].lower() == "course"]
    title_course_x0 = (
        course_words[1]["x0"] if len(course_words) >= 2 else credits_x0 * 0.45
    )

    return {
        "credits_x0": credits_x0,
        "number_x1": number_x1,
        "title_course_x0": title_course_x0,
        "col12_split": (number_x1 + title_course_x0) / 2,
        "col23_split": credits_x0 - 15,
        "header_top": header_top,
    }


def parse_hours_block(page1_words: list, anchors: dict) -> tuple:
    """Extract hours, co/pre-requisite, implementation using word x-positions."""
    credits_x0 = anchors["credits_x0"]
    col12_split = anchors["col12_split"]
    col23_split = anchors["col23_split"]

    # Find vertical boundaries
    catalog_top = None
    for w in page1_words:
        if w["text"].lower().startswith("catalog"):
            catalog_top = w["top"]
            break

    hours_top = None
    for w in page1_words:
        if w["text"].lower().rstrip(":") in ("hours",):
            if catalog_top is None or w["top"] < catalog_top:
                hours_top = w["top"]
                break

    if hours_top is None:
        # Fallback: first "lecture" word
        for w in page1_words:
            if "lecture" in w["text"].lower():
                if catalog_top is None or w["top"] < catalog_top - 20:
                    hours_top = w["top"]
                    break

    if hours_top is None or catalog_top is None:
        return "", "", ""

    # Collect words in the hours block
    block_words = [
        w for w in page1_words
        if hours_top <= w["top"] < catalog_top - 5
    ]

    # Group by row
    rows = {}
    for w in block_words:
        row_key = round(w["top"])
        rows.setdefault(row_key, []).append(w)

    col1_parts = []  # hours
    col2_parts = []  # prereq
    col3_parts = []  # implementation

    for row_key in sorted(rows):
        row = sorted(rows[row_key], key=lambda w: w["x0"])
        row_text_lower = {w["text"].lower().rstrip(":") for w in row}
        has_prereq_label = bool(row_text_lower & PREREQ_LABEL_WORDS)

        for w in row:
            t = w["text"]
            tl = t.lower().rstrip(":")

            # Skip structural label words
            if tl in HOURS_LABEL_WORDS:
                continue
            if has_prereq_label and tl in PREREQ_LABEL_WORDS:
                continue
            if has_prereq_label and tl == "or":
                continue

            x0 = w["x0"]
            if x0 < col12_split:
                col1_parts.append((w["top"], x0, t))
            elif x0 < col23_split:
                col2_parts.append((w["top"], x0, t))
            else:
                col3_parts.append((w["top"], x0, t))

    def join_parts(parts):
        sorted_parts = sorted(parts, key=lambda p: (p[0], p[1]))
        return clean_text(" ".join(p[2] for p in sorted_parts))

    return join_parts(col1_parts), join_parts(col2_parts), join_parts(col3_parts)


# ---------------------------------------------------------------------------
# General Education Category  (position-based)
# ---------------------------------------------------------------------------

def parse_gened(page1_words: list, anchors: dict) -> str:
    """Extract GenEd category using word positions on page 1."""
    # Find the "General" word that starts the GenEd row
    gen_top = None
    for w in page1_words:
        if w["text"].lower() == "general":
            gen_top = w["top"]
            break

    if gen_top is None:
        return ""

    # Find where the next major section starts (Required texts or coordinator)
    req_top = None
    for w in page1_words:
        if w["text"].lower() in ("required", "revision") and w["top"] > gen_top:
            req_top = w["top"]
            break

    if req_top is None:
        req_top = gen_top + 80  # fallback

    # Find the Course coordinator label x0 to use as left/right split
    coord_x0 = None
    words_sorted = sorted(page1_words, key=lambda w: (w["top"], w["x0"]))
    for i, w in enumerate(words_sorted):
        if w["text"].lower() == "course" and i + 1 < len(words_sorted):
            nxt = words_sorted[i + 1]
            if nxt["text"].lower().startswith("coord"):
                coord_x0 = w["x0"]
                break

    col_split = (coord_x0 - 10) if coord_x0 is not None else 210

    # Collect words in the GenEd row area, left of the split
    gened_words = [
        w for w in page1_words
        if gen_top - 1 < w["top"] < req_top - 5
        and w["x0"] < col_split
        and w["text"].lower().rstrip(":") not in GENED_LABEL_WORDS
    ]

    gened_words_sorted = sorted(gened_words, key=lambda w: (w["top"], w["x0"]))
    return clean_text(" ".join(w["text"] for w in gened_words_sorted))


# ---------------------------------------------------------------------------
# Text-regex section parsers
# ---------------------------------------------------------------------------

def parse_catalog_description(text: str) -> str:
    m = re.search(
        r"Catalog(?:ue)?\s+[Dd]escription:?\s*\n?(.*?)"
        r"(?=General\s+Education|Revision\s+date|Course\s+coordinator)",
        text, re.DOTALL | re.IGNORECASE,
    )
    return clean_text(m.group(1)) if m else ""


def _split_numbered_items(section_text: str) -> list:
    """Split a section on numbered list markers; return items with leading number stripped."""
    # Use multiline ^ so we catch items that start at beginning of string too
    parts = re.split(r"(?m)^\s*\d+\.\s+", section_text)
    items = []
    for part in parts:
        cleaned = clean_text(part)
        # Skip empty parts and the "Upon successful completion..." preamble
        if not cleaned:
            continue
        if re.match(r"upon\s+successful|the\s+student\s+will\s+be\s+able", cleaned, re.IGNORECASE):
            continue
        items.append(cleaned)
    return items


def parse_slos(text: str) -> str:
    m = re.search(
        r"(?:Course\s+)?Student\s+Learning\s+Outcomes?\s*"
        r"(?:\(SLO\)|/Course\s+Goals?)?:?\s*(.*?)"
        # Boundary: any "Course-specific" section OR ILG/PLO/Units/Evaluation
        r"(?=Course.specific|Institutional\s+Learning\s+Goals?"
        r"|Program\s+Learning\s+Outcomes?|Units?\s+of\s+study|Evaluation)",
        text, re.DOTALL | re.IGNORECASE,
    )
    if not m:
        return ""

    section = m.group(1)
    items = _split_numbered_items(section)

    if not items:
        # Fallback: bullet lines (skip the preamble "Upon successful completion..." line)
        lines = [
            clean_text(ln) for ln in section.split("\n")
            if ln.strip() and not re.match(
                r"upon\s+successful|the\s+student\s+will\s+be\s+able", ln.strip(), re.IGNORECASE
            )
        ]
        items = [ln for ln in lines if ln]

    # Strip "[Supports ILG # X; PLO #Y]" reference tags
    items = [SLO_BRACKET_RE.sub("", item).strip() for item in items]
    items = [item for item in items if item]

    return "|".join(items)


def parse_ilgs(text: str) -> str:
    m = re.search(
        r"(?:Course.specific\s+)?Institutional\s+Learning\s+Goals?\s*"
        r"(?:\(ILG\))?:?\s*(.*?)"
        r"(?=Program\s+Learning\s+Outcomes?)",
        text, re.DOTALL | re.IGNORECASE,
    )
    if not m:
        return ""

    section = m.group(1)
    parts = re.split(r"Institutional\s+Learning\s+Goal\.?\s*", section)
    items = []
    for part in parts[1:]:
        cleaned = clean_text(part)
        if cleaned:
            items.append(cleaned)
    return "|".join(items)


def parse_plos(text: str) -> str:
    m = re.search(
        r"Program\s+Learning\s+Outcomes?\s+.*?\(PLOs?\)\s*(.*?)"
        r"(?=Units?\s+(?:of\s+study|Objectives?)|Unit\s+I\b"
        r"|Method\s+of\s+Instruction|Evaluation)",
        text, re.DOTALL | re.IGNORECASE,
    )
    if not m:
        return ""

    section = m.group(1)
    items = _split_numbered_items(section)

    if not items:
        lines = [clean_text(ln) for ln in section.split("\n") if ln.strip()]
        items = [ln for ln in lines if ln]

    # Strip trailing semicolons (PDF formatting artifact)
    items = [item.rstrip(";").strip() for item in items]
    items = [item for item in items if item]

    return "|".join(items)


def parse_evaluation(text: str) -> str:
    m = re.search(
        r"Evaluation(?:\s+of\s+student\s+learning)?:?\s*(.*?)$",
        text, re.DOTALL | re.IGNORECASE,
    )
    return clean_text(m.group(1)) if m else ""


# ---------------------------------------------------------------------------
# Per-file processor
# ---------------------------------------------------------------------------

def process_pdf(pdf_path: Path) -> dict:
    row = {col: "" for col in CSV_COLUMNS}
    row["filename"] = pdf_path.name

    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return row

            page1 = pdf.pages[0]
            page1_words = page1.extract_words()
            full_text = extract_full_text(pdf)

        if not is_course_outline(full_text, pdf_path.name):
            return row

        # Course number / title / credits — text regex
        row["course_number"], row["course_title"], row["credits"] = \
            parse_header_course_line(full_text)

        # Hours / prereq / implementation — position-based
        anchors = get_page1_column_anchors(page1_words)
        if anchors:
            row["hours"], row["co_or_pre_requisite"], \
                row["implementation_semester_year"] = \
                parse_hours_block(page1_words, anchors)
            row["general_education_category"] = normalize_gened(
                parse_gened(page1_words, anchors)
            )

        # Body sections — text regex
        row["catalog_description"] = parse_catalog_description(full_text)
        row["slos"] = parse_slos(full_text)
        row["ilgs"] = parse_ilgs(full_text)
        row["plos"] = parse_plos(full_text)
        row["evaluation_of_student_learning"] = parse_evaluation(full_text)

        # Apply manual overrides for edge-case files (roman-numeral credits, etc.)
        if pdf_path.name in MANUAL_OVERRIDES:
            for field, value in MANUAL_OVERRIDES[pdf_path.name].items():
                row[field] = value

    except Exception as e:
        print(f"  ERROR: {e}")

    return row


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    pdf_files = load_all_pdfs(PDF_DIR)
    total = len(pdf_files)
    succeeded = 0
    skipped = 0
    failed = 0

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()

        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"Processing {i}/{total}: {pdf_path.name}", flush=True)
            row = process_pdf(pdf_path)
            writer.writerow(row)

            if row["course_number"]:
                succeeded += 1
            elif row["catalog_description"] == "" and row["slos"] == "":
                skipped += 1
            else:
                failed += 1

    print(f"\nDone.")
    print(f"  Parsed (course_number found): {succeeded}")
    print(f"  Skipped (non-outline):        {skipped}")
    print(f"  Partial (outline, no number): {failed}")
    print(f"  Output: {OUT_CSV}")


if __name__ == "__main__":
    main()
