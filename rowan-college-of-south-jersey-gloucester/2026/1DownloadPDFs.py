from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
import re
import requests
from bs4 import BeautifulSoup


HTML_FILE = r"C:\text\NJ\Rowan College of South Jersey - Gloucester\2026\Rowan College (Gloucester) Course Syllabi _ Gloucester Syllabi _ Rowan College South Jersey.html"
OUTPUT_SUBDIR = "pdfs"


def sanitize_filename(name: str) -> str:
    name = unquote(name).strip()
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    return name or "download.pdf"


def get_pdf_filename(pdf_url: str, response: requests.Response | None = None) -> str:
    if response is not None:
        cd = response.headers.get("Content-Disposition", "")
        match = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?', cd, re.IGNORECASE)
        if match:
            return sanitize_filename(match.group(1))

    path_name = Path(unquote(urlparse(pdf_url).path)).name
    if path_name.lower().endswith(".pdf"):
        return sanitize_filename(path_name)

    return "download.pdf"


def main() -> None:
    html_path = Path(HTML_FILE)
    output_dir = html_path.parent / OUTPUT_SUBDIR
    output_dir.mkdir(parents=True, exist_ok=True)

    html_text = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html_text, "html.parser")

    pdf_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        full_url = urljoin(html_path.as_uri(), href)

        parsed = urlparse(full_url)
        if parsed.scheme in {"http", "https", "file"} and ".pdf" in parsed.path.lower():
            pdf_links.append(full_url)

    # Remove duplicates while preserving order
    seen = set()
    unique_links = []
    for link in pdf_links:
        if link not in seen:
            seen.add(link)
            unique_links.append(link)

    print(f"Found {len(unique_links)} PDF link(s).")

    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}

    for url in unique_links:
        try:
            if url.startswith("file:///"):
                local_pdf = Path(urlparse(url).path.lstrip("/"))
                if not local_pdf.exists():
                    print(f"Skipping missing local file: {url}")
                    continue

                filename = sanitize_filename(local_pdf.name)
                dest = output_dir / filename
                dest.write_bytes(local_pdf.read_bytes())
                print(f"Copied: {filename}")
                continue

            with session.get(url, headers=headers, stream=True, timeout=60) as resp:
                resp.raise_for_status()
                filename = get_pdf_filename(url, resp)
                dest = output_dir / filename

                # Avoid overwriting duplicate filenames
                if dest.exists():
                    stem = dest.stem
                    suffix = dest.suffix
                    counter = 2
                    while True:
                        candidate = output_dir / f"{stem}_{counter}{suffix}"
                        if not candidate.exists():
                            dest = candidate
                            break
                        counter += 1

                with open(dest, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                print(f"Downloaded: {dest.name}")

        except Exception as e:
            print(f"Failed: {url} -> {e}")


if __name__ == "__main__":
    main()