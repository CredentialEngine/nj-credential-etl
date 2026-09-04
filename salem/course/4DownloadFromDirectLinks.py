import os
import csv
import requests
import time

csv_file = r"C:\text\NJ\Salem\course\SCC_Course_Links.csv"
output_dir = r"C:\text\NJ\Salem\course\CoursePDF"

os.makedirs(output_dir, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/pdf,*/*",
}

failed = []

with open(csv_file, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Downloading {len(rows)} files...")

for i, row in enumerate(rows, 1):
    course_name = row["Course Name"].replace(" ", "_").replace("/", "-")
    filename = f"{course_name}.pdf"
    url = row["URL"] + "&download=1"
    dest = os.path.join(output_dir, filename)

    print(f"[{i}/{len(rows)}] {filename}", end=" ... ", flush=True)

    try:
        response = requests.get(url, headers=headers, timeout=30, stream=True, allow_redirects=True)
        response.raise_for_status()

        chunks = []
        first_bytes = b""
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                chunks.append(chunk)
                if not first_bytes:
                    first_bytes = chunk

        if first_bytes[:4] != b"%PDF":
            content_type = response.headers.get("Content-Type", "")
            print(f"SKIPPED (not a PDF — {content_type})")
            failed.append((filename, url, f"Not a PDF: {content_type}"))
            continue

        with open(dest, "wb") as out:
            for chunk in chunks:
                out.write(chunk)

        size_kb = os.path.getsize(dest) // 1024
        print(f"OK ({size_kb} KB)")

    except requests.exceptions.RequestException as e:
        print(f"ERROR: {e}")
        failed.append((filename, url, str(e)))

    time.sleep(0.2)

print(f"\nDone. {len(rows) - len(failed)} succeeded, {len(failed)} failed.")

if failed:
    print("\nFailed files:")
    for name, url, reason in failed:
        print(f"  {name}: {reason}")
