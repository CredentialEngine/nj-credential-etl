import pandas as pd

def main():
    # Get the current working directory
    current_dir = os.getcwd()
    # Paths to your CSV files
    parsed_credentials_csv = os.path.join(current_dir, "parsed_credentials.csv")
    all_data_csv = os.path.join(current_dir, "all_data.csv"")

    # Path for the output
    output_csv = os.path.join(current_dir, "combined_credentials.csv")

    # Read both CSVs into pandas DataFrames
    df_parsed = pd.read_csv(parsed_credentials_csv)   # columns include 'Program Code'
    df_all = pd.read_csv(all_data_csv)                # columns include 'code'

    # Merge on 'Program Code' from df_parsed and 'code' from df_all
    # Join type can be 'left', 'right', 'inner', or 'outer' depending on your needs.
    # Here we do a "left" join so that all rows from parsed_credentials are kept.
    merged_df = pd.merge(
        df_parsed,
        df_all,
        how="left",
        left_on="Program Code",
        right_on="code"
    )

    # Write out the combined CSV without an index column
    merged_df.to_csv(output_csv, index=False)

    print(f"Combined CSV written to: {output_csv}")

if __name__ == "__main__":
    main()
