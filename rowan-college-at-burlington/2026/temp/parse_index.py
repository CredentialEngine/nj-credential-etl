import re, json, html
from bs4 import BeautifulSoup
from urllib.parse import urljoin

INDEX_FILE = r"C:\Temp\rcsj_degrees.html"
PDF_PATTERN = re.compile(r"\.pdf($|\?)", re.IGNORECASE)

def normalize_url(href, base="https://www.rcsj.edu/Degrees"):
    if not href: return None
    href = href.strip()
    if href.startswith('javascript:') or href == '#': return None
    return urljoin(base, href)

def extract_credential_from_name(name):
    if not name: return None
    if re.search(r'Certificate of Achievement', name, re.IGNORECASE): return "COA"
    if re.search(r'Academic Certificate', name, re.IGNORECASE): return "AC"
    if re.search(r'\(Certificate\)', name, re.IGNORECASE): return "CERT"
    return None

with open(INDEX_FILE, encoding='utf-8', errors='replace') as f:
    html_text = f.read()

soup = BeautifulSoup(html_text, "html.parser")
SKIP_H3 = {"Offered At","Refine Your Search","Getting Started","Student Support",
            "Transfer","Career Opportunities","Contact Us","General Filters",
            "Area of Interest","Academic Divisions"}

main = soup.find('main') or soup.find('div', id='main') or soup.body
h3_tags = main.find_all('h3')
programs = []
i = 0
while i < len(h3_tags):
    h3 = h3_tags[i]
    name_text = h3.get_text(strip=True)
    if not name_text or name_text in SKIP_H3:
        i += 1; continue
    if i+1 < len(h3_tags) and h3_tags[i+1].get_text(strip=True) == "Offered At":
        prog = {"name": name_text}
        desc_parts = []
        for sib in h3.find_next_siblings():
            if sib.name == 'h3': break
            t = sib.get_text(separator=' ', strip=True)
            if t: desc_parts.append(t)
        prog["description"] = ' '.join(desc_parts).strip()
        offered_at_h3 = h3_tags[i+1]
        offered_at = []
        ul = offered_at_h3.find_next_sibling('ul')
        if ul:
            for li in ul.find_all('li', recursive=False):
                a = li.find('a')
                if a and a.get('href'):
                    offered_at.append({"label": a.get_text(strip=True), "url": normalize_url(a['href'])})
                else:
                    offered_at.append({"label": li.get_text(strip=True), "url": None})
        prog["offered_at"] = offered_at
        div_tags = []
        after_ul = ul.find_next_siblings() if ul else []
        for sib in after_ul:
            if sib.name in ('h3','h2'): break
            t = sib.get_text(separator='|', strip=True)
            for tag in t.split('|'):
                tag = tag.strip()
                if tag: div_tags.append(tag)
        prog["divisions"] = div_tags
        detail_url = None; guide_url = None
        for oa in offered_at:
            url = oa.get("url")
            if not url: continue
            if PDF_PATTERN.search(url):
                if not guide_url: guide_url = url
            elif not detail_url:
                detail_url = url
        prog["detail_url"] = detail_url
        prog["program_guide_url"] = guide_url
        abbr = extract_credential_from_name(name_text)
        prog["credential_type_abbr"] = abbr
        programs.append(prog)
        i += 2
    else:
        i += 1

print(f"Found {len(programs)} programs")
with open(r"C:\Temp\rcsj_programs.json", "w", encoding="utf-8") as f:
    json.dump(programs, f, indent=2)
print("Saved to C:\\Temp\\rcsj_programs.json")
type_counts = {}
for p in programs:
    abbr = p.get("credential_type_abbr") or "UNKNOWN"
    type_counts[abbr] = type_counts.get(abbr, 0) + 1
for abbr, count in sorted(type_counts.items(), key=lambda x:-x[1]):
    print(f"  {abbr}: {count}")
