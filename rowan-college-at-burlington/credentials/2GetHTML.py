import csv
import os
import requests

def main():
    csv_file = r"C:\text\NJ\Rowan College at Burlington\credentials\all_data.csv"
    output_folder = r"C:\text\NJ\Rowan College at Burlington\credentials\CredentialHTML"

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the CSV file and read each row
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get("programGroupId", "").strip()
            if not code:
                # Skip if 'code' is missing or empty
                continue

            # Construct the URL
            url = f"https://catalog.rcbc.edu/programs/{code}"

            # Build path to output file <code>.html
            output_path = os.path.join(output_folder, f"{code}.html")

            # Check if file already exists, skip if it does
            if os.path.exists(output_path):
                print(f"[SKIP] {code} -> Already exists at {output_path}")
                continue

            try:
                # Fetch the webpage
                response = requests.get(url)
                # Check if request was successful
                if response.status_code == 200:
                    with open(output_path, "w", encoding="utf-8") as html_file:
                        html_file.write(response.text)
                    print(f"[SUCCESS] Downloaded {code} -> {output_path}")
                else:
                    print(f"[ERROR] {code} -> {url} (Status: {response.status_code})")

            except requests.exceptions.RequestException as e:
                # Handle any network exceptions (e.g., timeout, DNS error, etc.)
                print(f"[EXCEPTION] {code} -> {url} | {e}")

if __name__ == "__main__":
    main()
