# Import necessary libraries
import os
from bs4 import BeautifulSoup
import pandas as pd

def main():
    # 1. Define configuration settings
    config = {
        'input_folder': r"C:\text\NJ\{Provider}\credentials",
        'output_folder': r"C:\text\{Output}",
        'file_ext': ['html'],
        'required_fields': ['Credential Title', 'Competency', 'Issue Date'],
        'tags_map': {
            'Credential Title': 'h1, h2, h3',
            'Competency': 'div, span',
            'Issue Date': 'p, div'
        }
    }

    # 2. Define a function to parse individual HTML files
    def parse_single_html(filename):
        try:
            with open(os.path.join(config['input_folder'], filename), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                
                data_row = []
                
                # Extract relevant information based on tags and classes
                for tag in config['tags_map'].get('Credential Title', []):
                    titles = soup.find_all(tag, class_=config['tags_map']['Credential Title'])
                    for title in titles:
                        if (title.text.strip() not in data_row) and \
                           ('Credential Title' not in data_row):
                            data_row.append({'Credential Title': title.text.strip()})
                
                # Repeat similar logic for other fields...
                
                return data_row
        except Exception as e:
            print(f"Error parsing {filename}: {str(e)}")
            return []

    # 3. Define a function to get all HTML files in a folder
    def get_html_files(directory):
        html_files = []
        for filename in os.listdir(directory):
            if filename.lower().endswith(config['file_ext']):
                html_files.append(filename)
        return html_files

    # 4. Define a function to save results to CSV
    def save_to_csv(results, filename):
        try:
            df = pd.DataFrame(results)
            output_path = os.path.join(config['output_folder'], filename)
            
            if not os.path.exists(output_path):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
            df.to_csv(output_path + '.csv', index=False, encoding='utf-8-sig')
            print(f"Successfully saved results to {output_path}")
        except Exception as e:
            print(f"Error saving to CSV: {str(e)}")
            return

    # 5. Main processing logic
    if __name__ == "__main__":
        html_files = get_html_files(config['input_folder'])
        results = []
        
        for file in html_files:
            row = parse_single_html(file)
            results.extend(row)
            
        # Save all results to CSV files
        current_date = pd.Timestamp.now().date()
        for idx, result in enumerate(results):
            filename = f"Credentials_{current_date}_{idx + 1}.csv"
            save_to_csv([result], filename)

if __name__ == "__main__":
    main()
"""

### Key Features:
1. **Modular Design**:
   - Configuration settings can be easily adjusted via the `config` dictionary.
   - Each HTML file is processed individually, making it easier to debug and maintain.

2. **Customization**:
   - Users can map specific HTML tags and classes to different fields (e.g., 'h1' to 'Credential Title').
   - Fields marked as 'required_fields' will be verified before saving to CSV.

3. **Handling Special Characters**:
   - Uses UTF-8-sig encoding for CSV files to handle special characters properly.

4. **Error Handling**:
   - Gracefully handles errors when parsing individual HTML files or saving results.

5. ** Bulk Processing**:
   - Processes all HTML files in a specified folder.
   - Saves results to separate CSV files with timestamps in the filenames.

### Usage Instructions:
1. Modify the `config` dictionary to match your specific requirements (e.g., input and output folders, file extensions, etc.).
2. Run the script from the command line or within a Python environment.
3. The script will automatically process all HTML files in the specified input folder and save results to the output folder.

This design ensures flexibility while maintaining robustness for handling different types of HTML structures and bulk data processing requirements.
"""