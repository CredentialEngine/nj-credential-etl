import os
import csv

def search_and_report_csv_data(root_dir, target_suffix="_Credit_Courses.csv"):
    total_files_found = 0
    total_rows = 0

    for foldername, subfolders, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(target_suffix):
                file_path = os.path.join(foldername, filename)
                total_files_found += 1
                try:
                    with open(file_path, mode='r', encoding='utf-8-sig') as csvfile:
                        reader = csv.reader(csvfile)
                        row_count = sum(1 for row in reader)
                        total_rows += row_count - 1  # Assuming first row is a header
                        print(f"Processed: {file_path} ({row_count - 1} data rows)")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    # Print summary
    print("\n--- Report Summary ---")
    print(f"Total '*{target_suffix}' files found: {total_files_found}")
    print(f"Total data rows across all files: {total_rows}")

# Example usage
if __name__ == "__main__":
    root_directory = "./"  # Set to your desired root directory
    search_and_report_csv_data(root_directory)
