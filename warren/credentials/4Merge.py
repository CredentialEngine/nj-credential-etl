import pandas as pd
import os

def extract_filename_from_url(url):
    # Extract the filename part from the URL
    return os.path.basename(url)

# Paths to the CSV files
credentials_csv_path = r"C:\text\NJ\Warren\credentials\credentials.csv"
descriptions_csv_path = r"C:\text\NJ\Warren\credentials\pdf_descriptions.csv"

# Read the CSV files into DataFrames
credentials_df = pd.read_csv(credentials_csv_path)
descriptions_df = pd.read_csv(descriptions_csv_path)

# Transform 'Credential Link' into a new column 'Filename' for joining
credentials_df['Filename'] = credentials_df['Credential Link'].apply(extract_filename_from_url)

# Merge the DataFrames on the 'Filename' column
combined_df = pd.merge(credentials_df, descriptions_df, on='Filename', how='inner')

# Specify the path for the output CSV file
output_csv_path = r"C:\text\NJ\Warren\credentials\combined_credentials.csv"

# Save the merged DataFrame to a new CSV file
combined_df.to_csv(output_csv_path, index=False)

print(f'Data combined and saved to {output_csv_path}')
