import csv
import os
import requests

def download_html_files(csv_file, output_folder):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Read the CSV file and get the URLs
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        rows = list(reader)
    
    # Download each HTML file and update the row with the local file path
    for i, row in enumerate(rows[1:], start=1):  # Skip header row
        url = row[2]  # Assuming URLs are in the third column
        response = requests.get(url)
        response.raise_for_status()

        local_filename = os.path.join(output_folder, f'file_{i}.html')
        with open(local_filename, 'w', encoding='utf-8-sig') as file:
            file.write(response.text)
            print("Wrote " + local_filename)

        # Update the CSV row with the local file path
        row.append(local_filename)

    # Write the updated data back to the CSV file
    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    print("Downloaded HTML files and updated the CSV file.")

if __name__ == "__main__":
    CSV_FILE = r"C:\text\NJ\Bergen\course\output.csv"  # Replace with the path to your CSV file
    OUTPUT_FOLDER = r"C:\text\NJ\Bergen\course\courseHTML"  # Replace with the path to your desired output directory

    download_html_files(CSV_FILE, OUTPUT_FOLDER)
