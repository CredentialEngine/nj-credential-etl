import pandas as pd

# File paths
courses_file = r"C:\text\NJ\Middlesex\courses\parsed_courses.csv"
course_details_file = r"C:\text\NJ\Middlesex\courses\parsed_course_details.csv"
output_file = r"C:\text\NJ\Middlesex\courses\merged_courses.csv"

# Load CSV files
df_courses = pd.read_csv(courses_file, encoding="utf-8-sig")
df_course_details = pd.read_csv(course_details_file, encoding="utf-8-sig")

# Debug: Print column names
print("Courses Columns:", df_courses.columns.tolist())
print("Course Details Columns:", df_course_details.columns.tolist())

# Ensure column names are stripped of extra spaces
df_courses.columns = df_courses.columns.str.strip()
df_course_details.columns = df_course_details.columns.str.strip()

# Perform the merge on URL (parsed_courses) and Subject Webpage (parsed_course_details)
merged_df = df_courses.merge(df_course_details, left_on="URL", right_on="Subject Webpage", how="inner")

# Save to CSV
merged_df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"Merged file saved to {output_file}")
