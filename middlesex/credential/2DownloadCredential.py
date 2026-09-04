import os
import csv
import requests

def download_html_files():
    current_dir = os.getcwd()
    csv_file = os.path.join(current_dir, "parsed_credentials.csv")
    output_folder = os.path.join(current_dir, "CredentialsHTML")

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created directory: {output_folder}")

    # Read the CSV file
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            print(f"Opened CSV file: {csv_file}")

            for row in reader:
                degree_url = row.get("Degree URL", "").strip()
                if not degree_url:
                    print(f"Skipping row with missing Degree URL: {row}")
                    continue

                # Extract the filename from the URL
                filename = os.path.basename(degree_url)
                output_file = os.path.join(output_folder, filename + ".html")

                # Check if the file already exists to avoid duplicate downloads
                if os.path.exists(output_file):
                    print(f"File already exists, skipping: {output_file}")
                    continue

                # Download the HTML file
                try:
                    print(f"Downloading {degree_url}...")
                    response = requests.get(degree_url, timeout=10)
                    response.raise_for_status()  # Raise an exception for HTTP errors

                    # Save the HTML content to the file
                    with open(output_file, "w", encoding="utf-8") as html_file:
                        html_file.write(response.text)
                        print(f"Saved: {output_file}")

                except requests.RequestException as e:
                    print(f"[ERROR] Failed to download {degree_url}: {e}")

    except FileNotFoundError:
        print(f"[ERROR] CSV file not found: {csv_file}")
    except Exception as e:
        print(f"[ERROR] An error occurred while processing: {e}")

    print("\nDone.")

if __name__ == "__main__":
    download_html_files()
