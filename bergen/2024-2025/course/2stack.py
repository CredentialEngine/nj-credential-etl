import os

def combine_html_files(input_folder, output_file):
    # Initialize a variable to hold the combined content
    combined_content = ''

    for filename in os.listdir(input_folder):
        if filename.endswith(".html"):
            file_path = os.path.join(input_folder, filename)
            
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                content = file.read()
                combined_content += content + "\n"

    with open(output_file, 'w', encoding='utf-8-sig') as file:
        file.write(combined_content)

    print(f"Combined HTML saved to {output_file}")

if __name__ == "__main__":
    INPUT_FOLDER = r"C:\text\NJ\Bergen\course\bergen_course_pages" # Replace with your directory path
    OUTPUT_FILE = 'combined.html'  # The path for the output file

    combine_html_files(INPUT_FOLDER, OUTPUT_FILE)
