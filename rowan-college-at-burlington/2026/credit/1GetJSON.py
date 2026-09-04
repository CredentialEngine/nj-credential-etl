import csv
import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import requests

#Catalog POST API from here https://catalog.rcbc.edu/courses

#BASE_URL = "https://app.coursedog.com/api/v1/cm/brookdale/courses/search/%24filters"
BASE_URL = "https://app.coursedog.com/api/v1/cm/rcbc_colleague/courses/search/%24filters"

PARAMS = {
    "catalogId": "hIvqwey1AcC8uorbz4If",
    "skip": 0,
    "limit": 20,
    "orderBy": "catalogDisplayName,transcriptDescription,longName,name",
    "formatDependents": "false",
    "effectiveDatesRange": "2025-07-01%2C2025-07-01",
    "ignoreEffectiveDating": "false",
    "columns": (
        "customFields.rawCourseId,"
        "customFields.crseOfferNbr,"
        "customFields.catalogAttributes,"
        "customFields.66FYg,"
        "displayName,"
        "department,"
        "description,"
        "name,"
        "courseNumber,"
        "subjectCode,"
        "code,"
        "courseGroupId,"
        "career,"
        "college,"
        "longName,"
        "status,"
        "institution,"
        "institutionId,"
        "credits"
    ),
}

PAYLOAD_FILE = Path("payload.json")
OUTPUT_JSON = Path("rcbc_courses_all.json")
OUTPUT_CSV = Path("rcbc_courses_all.csv")
CHECKPOINT_FILE = Path("rcbc_checkpoint.json")


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://catalog.rcbc.edu",
        "Referer": "https://catalog.rcbc.edu/",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/146.0.0.0 Safari/537.36"
        ),
        "X-Requested-With": "catalog",
    })
    return session


def load_payload() -> Dict[str, Any]:
    if not PAYLOAD_FILE.exists():
        raise FileNotFoundError(
            f"Missing {PAYLOAD_FILE}. Save the full DevTools request payload there."
        )
    with PAYLOAD_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def fetch_page(
    session: requests.Session,
    payload: Dict[str, Any],
    skip: int,
    limit: int,
) -> Dict[str, Any]:
    params = PARAMS.copy()
    params["skip"] = skip
    params["limit"] = limit

    response = session.post(
        BASE_URL,
        params=params,
        json=payload,
        timeout=60,
    )

    if response.status_code != 200:
        print(f"\nHTTP {response.status_code} for skip={skip}")
        print("URL:", response.url)
        print("Response text (first 2000 chars):")
        print(response.text[:2000])
        response.raise_for_status()

    return response.json()


def save_checkpoint(
    all_rows: List[Dict[str, Any]],
    next_skip: int,
    list_length: int,
    limit: int,
) -> None:
    checkpoint = {
        "listLength": list_length,
        "limit": limit,
        "nextSkip": next_skip,
        "fetchedCount": len(all_rows),
        "data": all_rows,
    }
    with CHECKPOINT_FILE.open("w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)


def load_checkpoint() -> Dict[str, Any] | None:
    if not CHECKPOINT_FILE.exists():
        return None
    with CHECKPOINT_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def print_progress(current: int, total: int, width: int = 40) -> None:
    if total <= 0:
        total = 1
    ratio = min(max(current / total, 0), 1)
    filled = int(width * ratio)
    bar = "#" * filled + "-" * (width - filled)
    percent = ratio * 100
    sys.stdout.write(f"\r[{bar}] {current}/{total} ({percent:5.1f}%)")
    sys.stdout.flush()
    if current >= total:
        print()


def flatten_json(obj: Any, parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    items: Dict[str, Any] = {}

    if isinstance(obj, dict):
        for key, value in obj.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            items.update(flatten_json(value, new_key, sep=sep))
    elif isinstance(obj, list):
        if all(not isinstance(x, (dict, list)) for x in obj):
            items[parent_key] = "|".join("" if x is None else str(x) for x in obj)
        else:
            items[parent_key] = json.dumps(obj, ensure_ascii=False)
    else:
        items[parent_key] = obj

    return items


def write_json(all_rows: List[Dict[str, Any]], list_length: int) -> None:
    output = {
        "listLength": list_length,
        "fetchedCount": len(all_rows),
        "data": all_rows,
    }
    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


def write_csv(all_rows: List[Dict[str, Any]]) -> None:
    flattened_rows = [flatten_json(row) for row in all_rows]

    fieldnames = sorted({
        key
        for row in flattened_rows
        for key in row.keys()
    })

    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(flattened_rows)


def main() -> None:
    payload = load_payload()
    session = build_session()
    limit = int(PARAMS["limit"])

    checkpoint = load_checkpoint()
    all_rows: List[Dict[str, Any]] = []
    list_length = 0
    next_skip = 0

    if checkpoint:
        all_rows = checkpoint.get("data", [])
        list_length = int(checkpoint.get("listLength", 0))
        next_skip = int(checkpoint.get("nextSkip", 0))
        print(f"Resuming from checkpoint: fetched {len(all_rows)} rows, next skip={next_skip}")
    else:
        print("No checkpoint found. Starting fresh.")

    if not checkpoint:
        first_page = fetch_page(session, payload, skip=0, limit=limit)
        list_length = int(first_page["listLength"])
        first_data = first_page.get("data", [])
        if not isinstance(first_data, list):
            raise ValueError("Response 'data' field was not a list.")
        all_rows.extend(first_data)
        next_skip = limit
        save_checkpoint(all_rows, next_skip, list_length, limit)

    total_pages = math.ceil(list_length / limit) if list_length else 0
    print(f"Total results: {list_length}")
    print(f"Total pages:   {total_pages}")

    print_progress(len(all_rows), list_length)

    while next_skip < list_length:
        page_json = fetch_page(session, payload, skip=next_skip, limit=limit)
        page_data = page_json.get("data", [])

        if not isinstance(page_data, list):
            raise ValueError(f"Page at skip={next_skip} returned non-list 'data'.")

        all_rows.extend(page_data)
        next_skip += limit

        save_checkpoint(all_rows, next_skip, list_length, limit)
        print_progress(len(all_rows), list_length)

        time.sleep(0.15)

    write_json(all_rows, list_length)
    write_csv(all_rows)

    print(f"Saved JSON: {OUTPUT_JSON.resolve()}")
    print(f"Saved CSV:  {OUTPUT_CSV.resolve()}")

    if CHECKPOINT_FILE.exists():
        print(f"Checkpoint retained: {CHECKPOINT_FILE.resolve()}")

    if len(all_rows) != list_length:
        print(f"Warning: fetchedCount={len(all_rows)} but listLength={list_length}")


if __name__ == "__main__":
    main()