import pandas as pd

# Load the CSV file with citation data
csv_filename = 'articles_with_citations.csv'
articles = pd.read_csv(csv_filename)

# Replace empty citation values with 0 for sorting
articles['Citations'].fillna(0, inplace=True)

# Convert Citations to integer for proper sorting
articles['Citations'] = articles['Citations'].astype(int)

# Sort by Citations in descending order
sorted_articles = articles.sort_values(by='Citations', ascending=False)

# Save the sorted data back to a new CSV file
sorted_csv_filename = 'sorted_articles_by_citations.csv'
sorted_articles.to_csv(sorted_csv_filename, index=False)

print(f"Sorted data saved to {sorted_csv_filename}")
