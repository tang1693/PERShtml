from pdf2image import convert_from_path
import pytesseract
import csv
import re
import os

def extract_with_ocr(pdf_path):
    articles = []
    images = convert_from_path(pdf_path)
    for img in images:
        text = pytesseract.image_to_string(img)
        # Look for "In-Press Articles" section
        if "In-Press Articles" in text:
            lines = text.split("\n")
            start_index = next((i for i, line in enumerate(lines) if "In-Press Articles" in line), None)
            if start_index is not None:
                for line in lines[start_index + 1:]:
                    # Stopping at unrelated sections or footers
                    if re.search(r"(PHOTOGRAMMETRIC ENGINEERING|Delivered by Ingenta|Page\s\d+)", line):
                        break
                    # Try splitting into title and authors
                    if '.' in line:
                        split_line = re.split(r'\.\s+', line, maxsplit=1)
                        if len(split_line) == 2:
                            title, authors = split_line
                            articles.append((title.strip(), authors.strip()))
    return articles

def save_to_csv(data, output_csv_path):
    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Authors'])
        writer.writerows(data)

# Paths to your PDFs
pdf_files = ["s10.pdf", "s11.pdf", "s12.pdf", "s13.pdf"]
output_csv = "in_press_articles.csv"


all_articles = []
for pdf_file in pdf_files:
    pdf_path = f"InPress/{pdf_file}"  # Adjust path as needed
    articles = extract_with_ocr(pdf_path)
    all_articles.extend(articles)

save_to_csv(all_articles, output_csv)
print(f"Extracted data saved to {output_csv}")