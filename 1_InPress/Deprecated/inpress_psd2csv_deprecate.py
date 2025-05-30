import PyPDF2
import pandas as pd
import re

def extract_in_press_articles(pdf_path):
    """
    Extracts the 'In-Press Articles' section from a PDF file and consolidates multiline entries.
    :param pdf_path: Path to the PDF file.
    :return: A list of dictionaries with title and author information.
    """
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        articles = []
        capture = False
        current_entry = ""

        for page in reader.pages:
            text = page.extract_text()
            if "In-Press Articles" in text:
                capture = True
                text = text.split("In-Press Articles", 1)[1]
            if capture:
                lines = text.strip().split("\n")
                for line in lines:
                    if line.strip() and re.search(r"[A-Za-z]", line):
                        if re.match(r".*\.$", line) or re.match(r".*\, and .*", line):
                            # Line likely ends an entry
                            current_entry += " " + line.strip()
                            articles.append(current_entry.strip())
                            current_entry = ""
                        else:
                            # Line continues the current entry
                            current_entry += " " + line.strip()

        # Clean up remaining entry if any
        if current_entry:
            articles.append(current_entry.strip())

    # Process articles into Title and Authors
    processed_articles = []
    for article in articles:
        # Remove unnecessary rows (e.g., footer rows)
        if "PHOTOGRAMMETRIC ENGINEERING" in article:
            continue
        parts = re.split(r"\. ", article, maxsplit=1)  # Split at the first period
        title = parts[0].strip() if len(parts) > 0 else ""
        authors = parts[1].strip() if len(parts) > 1 else ""
        if title and authors:
            processed_articles.append({"Title": title, "Authors": authors})

    return processed_articles

def save_to_csv(data, output_path):
    """
    Saves the extracted data to a CSV file.
    :param data: List of dictionaries with extracted data.
    :param output_path: Path to save the CSV file.
    """
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"Data saved to {output_path}")


    
# Process the PDFs and save the data to CSV
pdf_files = ['InPress/s13.pdf']
all_articles = []

for pdf_file in pdf_files:
    articles = extract_in_press_articles(pdf_file)
    all_articles.extend(articles)

output_csv = 'in_press_articles.csv'
save_to_csv(all_articles, output_csv)
