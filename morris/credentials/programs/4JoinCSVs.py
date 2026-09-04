import pandas as pd

def map_type(type_):
    type_mapping = {
        "(AA)": "AssociateofArtsDegree",
        "(AAS)": "AssociateofAppliedScienceDegree",
        "(AFA)": "AssociateofArtsDegree",
        "(AS)": "AssociateofScienceDegree",
        "(Certificates)": "Certificate",
        "(Workforce Development)": "Certificate",
        "Unknown": "Certificate",

    }
    return type_mapping.get(str(type_).strip(), type_)



# File paths
file1 = r"C:\text\NJ\Morris\credentials\programs\credentials_parsed.csv"
file2 = r"C:\text\NJ\Morris\credentials\programs\parsed_credentials.csv"

# Load CSVs into DataFrames
df1 = pd.read_csv(file1)  # credentials_parsed.csv
df2 = pd.read_csv(file2)  # parsed_credentials.csv

# Merge based on 'Program Link ' from df1 and 'URL' from df2, keeping all rows from df2
merged_df = df2.merge(df1[['Program Link', 'Credential Type']], 
                       left_on='URL', right_on='Program Link', 
                       how='left')

# Drop the 'Program Link ' column after merging (optional)
merged_df.drop(columns=['Program Link'], inplace=True)

merged_df['Type'] = merged_df['Credential Type_y'].apply(map_type)

merged_df['Name'] = merged_df['Credential Name'] + ": " + merged_df['Credential Type_y'].str.replace(r"[()]", "", regex=True).replace(r"Certificates", "Certificate", regex=True)



# Save the updated DataFrame back to CSV
output_file = r"C:\text\NJ\Morris\credentials\programs\parsed_credentials_updated.csv"
merged_df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"Updated CSV saved to: {output_file}")
