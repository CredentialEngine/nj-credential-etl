import os
import csv
import requests

def main():
    csv_file = r"C:\text\NJ\Hudson County\Credentials\parsed_programs.csv"
    output_folder = r"C:\text\NJ\Hudson County\Credentials\CredentialsHTML"

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Open the CSV file and read each row
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get("Subject Webpage", "").strip()
            if not url:
                # Skip if URL is empty
                continue

            # Extract the last portion of the URL to use as filename
            # e.g. https://www.hccc.edu/programs-courses/academic-pathways/xxx.html -> 'xxx.html'
            filename = url.rsplit('/', 1)[-1]
            # Optionally handle query strings or special chars
            # For simplicity, we just take what's after the last slash

            try:
                response = requests.get(url)
                if response.status_code == 200:
                    # Save to subdirectory as .html
                    output_path = os.path.join(output_folder, filename)
                    # Write as text
                    with open(output_path, "w", encoding="utf-8") as out_file:
                        out_file.write(response.text)
                    print(f"[OK] Downloaded {url} -> {output_path}")
                else:
                    print(f"[ERROR] {url} returned status {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"[EXCEPTION] {url} -> {e}")

if __name__ == "__main__":
    main()
