import pandas as pd

def remove_duplicates(input_csv, output_csv):
    # Read the CSV file
    df = pd.read_csv(input_csv)
    
    # Remove duplicate rows based on 'Title' column
    df_cleaned = df.drop_duplicates(subset=['Title'])
    
    # Save the cleaned data to a new CSV file
    df_cleaned.to_csv(output_csv, index=False)
    
    print(f"Duplicates removed based on Title. Cleaned data saved to {output_csv}")

# Example usage
input_csv = "ALL_articles_Update.csv"  # Change to your actual file name
output_csv = "ALL_articles_Update_cleaned.csv"  # Change to your desired output file name
remove_duplicates(input_csv, output_csv)
