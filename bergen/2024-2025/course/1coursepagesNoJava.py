import requests
import os

def download_html_pages(base_url, total_pages, output_folder):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for page in range(1, total_pages + 1):
        # Construct the URL with the current page number
        url = f"{base_url}&filter%5Bcpage%5D={page}#acalog_template_course_filter"

        # Fetch the content of the page
        response = requests.get(url)
        response.raise_for_status()  # Will raise an error for bad responses

        # Save the content to an HTML file
        filename = f"page_{page}.html"
        with open(os.path.join(output_folder, filename), 'w', encoding='utf-8') as file:
            file.write(response.text)

        print(f"Downloaded and saved {filename}")

if __name__ == "__main__":
    #BASE_URL = "https://catalog.vinu.edu/content.php?catoid=45&navoid=3462&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1"
    #BASE_URL = "https://catalog.ivytech.edu/content.php?catoid=9&navoid=1014"
    BASE_URL = "https://catalog.bergen.edu/content.php?catoid=7&navoid=305"
    TOTAL_PAGES = 10 #Look up total number of course pages
    OUTPUT_FOLDER = "bergen_course_pages"

    download_html_pages(BASE_URL, TOTAL_PAGES, OUTPUT_FOLDER)
