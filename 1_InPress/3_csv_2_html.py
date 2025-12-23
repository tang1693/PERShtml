# import pandas as pd

# # Load the CSV file
# csv_filename = '1_InPress/filtered_InPress_articles_info_abs.csv'
# articles = pd.read_csv(csv_filename)

# # Filter out articles with "No Abstract"
# articles = articles[articles["Abstract"] != "No Abstract"]

# # Start the combined HTML content
# html_combined = ""

# # Generate HTML for each article
# for index, row in articles.iterrows():
#     # Set article border-top style except for the first article
#     border_style = "border-top: 1px solid #000; padding: 15px;" if index > 0 else "padding: 15px;"

#     # Start the article section
#     article_html = f'<article style="{border_style}">\n'

#     # --- Research Articles header with "Open Access" badge ---
#     access_text = '<span style="color: rgb(0, 191, 255);">Open Access</span>' if row['Access'] == "Open Access content" else ''
#     article_html += f'''    <div style="display: flex; justify-content: space-between; align-items: center;">
#         <div style="font-weight: bold; color: gray;">Research Articles {access_text}</div>
#     </div>\n'''

#     # --- Title and link (only if Title is valid) ---
#     if pd.notna(row['Title']) and row['Title'] != 'N/A':
#         article_html += f'''    <h3 style="margin: 5px 0;">
#         <a href="{row["URL"]}" rel="noreferrer" style="text-decoration: none; color: #1b5faa;">
#             {row["Title"]}
#         </a>
#     </h3>\n'''

#     # --- Publication info (Pages as date) ---
#     if pd.notna(row['Pages']) and row['Pages'] != 'N/A':
#         article_html += f'    <div style="font-style: italic;">Avaliable online: {row["Pages"]}</div>\n'

#     # --- Authors ---
#     if pd.notna(row['Authors']) and row['Authors'] != 'N/A':
#         article_html += f'    <div>Authors: {row["Authors"]}</div>\n'

#     # --- Abstract with <details> (foldable) ---
#     if pd.notna(row['Abstract']) and row['Abstract'] != 'N/A':
#         article_html += f'''    <div>
#         Abstract:
#         <details>
#             <summary style="color: #1b5faa;">Read more...</summary>
#             {row["Abstract"]}
#         </details>
#     </div>\n'''

#     # --- Close article section ---
#     article_html += '</article>\n'

#     # Add this article to combined HTML
#     html_combined += article_html

# # Save to a single HTML file
# combined_filename = 'in_press_articles.html'
# with open(combined_filename, 'w', encoding='utf-8') as file:
#     file.write(html_combined)

# print(f"✅ Combined HTML content successfully saved to {combined_filename}")

import pandas as pd

# Load the CSV file
csv_filename = "1_InPress/filtered_InPress_articles_info_abs.csv"
articles = pd.read_csv(csv_filename)

# Filter out articles with "No Abstract"
articles = articles[articles["Abstract"] != "No Abstract"]

# NEW: clean titles that contain ""
articles["Title"] = articles["Title"].astype(str).str.replace('"', "", regex=False).str.strip()

# NEW: sort descending by available online date (Pages)
# If parsing fails, it becomes NaT and goes to the bottom
articles["_sort_date"] = pd.to_datetime(articles["Pages"], errors="coerce", infer_datetime_format=True)
articles = articles.sort_values("_sort_date", ascending=False, na_position="last").drop(columns=["_sort_date"]).reset_index(drop=True)

# Start the combined HTML content
html_combined = ""

# Generate HTML for each article
for index, row in articles.iterrows():
    border_style = "border-top: 1px solid #000; padding: 15px;" if index > 0 else "padding: 15px;"
    article_html = f'<article style="{border_style}">\n'

    access_text = '<span style="color: rgb(0, 191, 255);">Open Access</span>' if row["Access"] == "Open Access content" else ""
    article_html += f'''    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style="font-weight: bold; color: gray;">Research Articles {access_text}</div>
    </div>\n'''

    if pd.notna(row["Title"]) and row["Title"] != "N/A" and str(row["Title"]).strip() != "":
        article_html += f'''    <h3 style="margin: 5px 0;">
        <a href="{row["URL"]}" rel="noreferrer" style="text-decoration: none; color: #1b5faa;">
            {row["Title"]}
        </a>
    </h3>\n'''

    if pd.notna(row["Pages"]) and row["Pages"] != "N/A":
        article_html += f'    <div style="font-style: italic;">Avaliable online: {row["Pages"]}</div>\n'

    if pd.notna(row["Authors"]) and row["Authors"] != "N/A":
        article_html += f'    <div>Authors: {row["Authors"]}</div>\n'

    if pd.notna(row["Abstract"]) and row["Abstract"] != "N/A":
        article_html += f'''    <div>
        Abstract:
        <details>
            <summary style="color: #1b5faa;">Read more...</summary>
            {row["Abstract"]}
        </details>
    </div>\n'''

    article_html += "</article>\n"
    html_combined += article_html

combined_filename = "in_press_articles.html"
with open(combined_filename, "w", encoding="utf-8") as file:
    file.write(html_combined)

print(f"✅ Combined HTML content successfully saved to {combined_filename}")
