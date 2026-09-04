"""
RCSJ Degrees & Certificates Scraper
Reads index HTML from local file (fetched via PowerShell),
then fetches detail pages via requests.
"""

import re, csv, time, html, sys, os, json
from pathlib import Path
import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = "https://www.rcsj.edu"
INDEX_URL = "https://www.rcsj.edu/Degrees"
INDEX_FILE = r"C:\Temp\rcsj_degrees.html"
OUTPUT_CSV = r"C:\Temp\rcsj_credentials.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

CREDENTIAL_TYPE_MAP = {
    "A.A.":   "Associate in Arts",
    "A.S.":   "Associate in Science",
    "A.A.S.": "Associate in Applied Science",
    "COA":    "Certificate of Achievement",
    "CERT":   "Certificate",
    "AC":     "Academic Certificate",
}

PDF_PATTERN = re.compile(r'\.pdf($|\?)', re.IGNORECASE)
EXCLUDE_PATTERNS = re.compile(
    r'(javascript:|mailto:|wufoo\.com|linkedin\.com|facebook\.com'
    r'|instagram\.com|youtube\.com|tiktok\.com|eventbrite\.com'
    r'|/Apply|/Courses|/Give|/Internships|/Athletics|/Community'
    r'|/CurrentStudents|/Parents|safelinks\.protection)',
    re.IGNORECASE
)

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"  [WARN] {url}: {e}")
        return None

def normalize_url(href, page_url=BASE_URL):
    if not href: return None
    href = href.strip()
    if href.startswith('javascript:') or href == '#': return None
    return urljoin(page_url, href)

def extract_credential_from_name(name):
    if not name: return None
    if re.search(r'Certificate of Achievement', name, re.IGNORECASE): return "COA"
    if re.search(r'Academic Certificate', name, re.IGNORECASE): return "AC"
    if re.search(r'\(Certificate\)', name, re.IGNORECASE): return "CERT"
    return None

def parse_credential_from_title(title_str):
    if not title_str: return None
    title_str = html.unescape(title_str).strip()
    first_part = title_str.split('|')[0].strip()
    for abbr in CREDENTIAL_TYPE_MAP:
        if re.search(r',?\s*' + re.escape(abbr) + r'\s*$', first_part):
            return abbr
    if re.search(r'Certificate of Achievement', first_part, re.IGNORECASE): return "COA"
    if re.search(r'Academic Certificate', first_part, re.IGNORECASE): return "AC"
    if re.search(r'\bCertificate\b', first_part, re.IGNORECASE): return "CERT"
    return None

def scrape_index():
    print(f"Parsing index from {INDEX_FILE}")
    with open(INDEX_FILE, encoding='utf-8', errors='replace') as f:
        html_text = f.read()

    soup = BeautifulSoup(html_text, "html.parser")

    SKIP_H3 = {"Offered At", "Refine Your Search", "Getting Started",
                "Student Support", "Transfer", "Career Opportunities",
                "Contact Us", "General Filters", "Area of Interest",
                "Academic Divisions"}

    main = soup.find('main') or soup.find('div', id='main') or soup.body
    h3_tags = main.find_all('h3')

    programs = []
    i = 0
    while i < len(h3_tags):
        h3 = h3_tags[i]
        name_text = h3.get_text(strip=True)

        if not name_text or name_text in SKIP_H3:
            i += 1
            continue

        # Check next h3 is "Offered At"
        if i + 1 < len(h3_tags) and h3_tags[i + 1].get_text(strip=True) == "Offered At":
            prog = {"name": name_text}

            # Description: text between this h3 and next h3
            desc_parts = []
            for sib in h3.find_next_siblings():
                if sib.name == 'h3': break
                t = sib.get_text(separator=' ', strip=True)
                if t: desc_parts.append(t)
            prog["description"] = ' '.join(desc_parts).strip()

            # Offered At links
            offered_at_h3 = h3_tags[i + 1]
            offered_at = []
            ul = offered_at_h3.find_next_sibling('ul')
            if ul:
                for li in ul.find_all('li', recursive=False):
                    a = li.find('a')
                    if a and a.get('href'):
                        offered_at.append({
                            "label": a.get_text(strip=True),
                            "url": normalize_url(a['href'], INDEX_URL)
                        })
                    else:
                        offered_at.append({"label": li.get_text(strip=True), "url": None})
            prog["offered_at"] = offered_at

            # Division tags after the ul
            div_tags = []
            after_ul = ul.find_next_siblings() if ul else []
            for sib in after_ul:
                if sib.name in ('h3', 'h2'): break
                t = sib.get_text(separator='|', strip=True)
                for tag in t.split('|'):
                    tag = tag.strip()
                    if tag: div_tags.append(tag)
            prog["divisions"] = div_tags

            # Determine URLs
            detail_url = None
            guide_url = None
            for oa in offered_at:
                url = oa.get("url")
                if not url: continue
                if PDF_PATTERN.search(url):
                    if not guide_url: guide_url = url
                elif not EXCLUDE_PATTERNS.search(url):
                    if not detail_url: detail_url = url
            prog["detail_url"] = detail_url
            prog["program_guide_url"] = guide_url

            # Credential type from name
            abbr = extract_credential_from_name(name_text)
            prog["credential_type_abbr"] = abbr
            prog["credential_type"] = CREDENTIAL_TYPE_MAP.get(abbr, "") if abbr else ""

            programs.append(prog)
            i += 2
        else:
            i += 1

    print(f"Found {len(programs)} programs on index page")
    return programs

def enrich_with_detail_pages(programs):
    need_detail = [p for p in programs if not p.get("credential_type_abbr") and p.get("detail_url")]
    print(f"\nFetching detail pages for {len(need_detail)} programs missing credential type...")

    seen_urls = {}

    for idx, prog in enumerate(need_detail):
        url = prog["detail_url"]
        print(f"  [{idx+1}/{len(need_detail)}] {url}")

        if url in seen_urls:
            abbr = seen_urls[url]
        else:
            html_text = fetch_url(url)
            if not html_text:
                seen_urls[url] = None
                abbr = None
            else:
                soup = BeautifulSoup(html_text, "html.parser")
                title_tag = soup.find('title')
                title_text = title_tag.get_text() if title_tag else ""
                abbr = parse_credential_from_title(title_text)
                seen_urls[url] = abbr

                # Grab program guide PDF from detail page if missing
                if not prog.get("program_guide_url"):
                    for a in soup.find_all('a', href=True):
                        h = a['href']
                        if PDF_PATTERN.search(h) and ('Program-Guide' in h or 'program-guide' in h.lower()):
                            prog["program_guide_url"] = normalize_url(h, url)
                            break

            time.sleep(0.4)

        if abbr:
            prog["credential_type_abbr"] = abbr
            prog["credential_type"] = CREDENTIAL_TYPE_MAP.get(abbr, abbr)

    return programs

def write_csv(programs):
    fieldnames = [
        "name", "credential_type_abbr", "credential_type", "description",
        "offered_at_summary", "offered_at_gloucester_url", "offered_at_cumberland_url",
        "detail_url", "program_guide_url", "divisions",
    ]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for prog in programs:
            gloucester_url, cumberland_url = "", ""
            for oa in prog.get("offered_at", []):
                label = oa.get("label", "").lower()
                url = oa.get("url") or ""
                if "gloucester" in label: gloucester_url = url
                elif "cumberland" in label: cumberland_url = url
            writer.writerow({
                "name": prog.get("name", ""),
                "credential_type_abbr": prog.get("credential_type_abbr", ""),
                "credential_type": prog.get("credential_type", ""),
                "description": prog.get("description", ""),
                "offered_at_summary": "; ".join(oa["label"] for oa in prog.get("offered_at", []) if oa.get("label")),
                "offered_at_gloucester_url": gloucester_url,
                "offered_at_cumberland_url": cumberland_url,
                "detail_url": prog.get("detail_url", ""),
                "program_guide_url": prog.get("program_guide_url", ""),
                "divisions": "; ".join(prog.get("divisions", [])),
            })
    print(f"\nWrote {len(programs)} rows to {OUTPUT_CSV}")

def print_summary(programs):
    total = len(programs)
    with_type = sum(1 for p in programs if p.get("credential_type_abbr"))
    type_counts = {}
    for p in programs:
        abbr = p.get("credential_type_abbr") or "UNKNOWN"
        type_counts[abbr] = type_counts.get(abbr, 0) + 1
    print("\n=== SUMMARY ===")
    print(f"Total programs: {total}, resolved: {with_type}, missing: {total-with_type}")
    for abbr, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {abbr:8s} ({CREDENTIAL_TYPE_MAP.get(abbr, '?')}): {count}")
    if total - with_type > 0:
        print("\nPrograms with UNKNOWN credential type:")
        for p in programs:
            if not p.get("credential_type_abbr"):
                print(f"  - {p['name']}")

if __name__ == "__main__":
    programs = scrape_index()
    programs = enrich_with_detail_pages(programs)
    print_summary(programs)
    write_csv(programs)
    print("Done.")
