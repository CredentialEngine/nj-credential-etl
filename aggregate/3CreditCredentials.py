import os
import pandas as pd

def search_and_report_excel_data(root_dir, filename_keyword="_Credit_Credentials.xlsx", target_sheet="Credential Data - MAKE UPDATES"):
    total_files_found = 0
    total_rows = 0

    for foldername, subfolders, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename_keyword in filename and filename.endswith(".xlsx"):
                file_path = os.path.join(foldername, filename)
                total_files_found += 1
                try:
                    # Load only the specific sheet
                    df = pd.read_excel(file_path, sheet_name=target_sheet)
                    row_count = len(df)
                    total_rows += row_count
                    print(f"Processed: {file_path} ({row_count} data rows from sheet '{target_sheet}')")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    # Print summary
    print("\n--- Report Summary ---")
    print(f"Total Excel files containing '{filename_keyword}': {total_files_found}")
    print(f"Total data rows across all '{target_sheet}' sheets: {total_rows}")

# Example usage
if __name__ == "__main__":
    root_directory = "./"  # Replace with the desired search path
    search_and_report_excel_data(root_directory)
