import pandas as pd

# Paths to the CSV files
extracted_csv_path = r"C:\text\NJ\Atlantic Cape\credentials\credentials_extracted.csv"
output_csv_path = r"C:\text\NJ\Atlantic Cape\credentials\credentials_output.csv"

# Read the CSV files into DataFrames
df_extracted = pd.read_csv(extracted_csv_path)
df_output = pd.read_csv(output_csv_path)

# Merge the DataFrames on 'URL' from df_extracted and 'Type URL' from df_output
merged_df = pd.merge(df_extracted, df_output, left_on='URL', right_on='Type URL', how='inner')

# Create the 'Credential Title' column by combining 'Title' and 'CEType'
merged_df["Credential Title"] = merged_df["Title_x"] + ": " + merged_df["Type"]

# Path to save the new merged CSV
new_csv_path = r"C:\text\NJ\Atlantic Cape\credentials\combined_credentials.csv"

# Save the merged DataFrame to CSV
merged_df.to_csv(new_csv_path, index=False, encoding="utf-8-sig")

print(f"Data successfully merged and saved to {new_csv_path}")
