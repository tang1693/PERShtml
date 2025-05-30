import re
import json
import csv
from openai import OpenAI
import os
import pandas as pd
from dotenv import load_dotenv
from PyPDF2 import PdfReader

# Load environment variables from a .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def read_pdf_to_text(pdf_path):
    """Extract text from the PDF."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def query_gpt_with_text(text, prompt):
    """Send the text to GPT with a specific prompt."""
    full_prompt = f"{prompt}\nHere is the pdf:\n{text}..."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful PDF careful reader. You know different sections of the PDF."},
            {"role": "user", "content": full_prompt},
        ]
    )
    return response.choices[0].message.content

def clean_gpt_response(gpt_response):
    """Clean and validate the GPT response to ensure it is valid JSON."""
    try:
        # Use regex to extract JSON portion if there are extra characters
        json_match = re.search(r"\[.*\]", gpt_response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            raise ValueError("No valid JSON found in GPT response.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    
    

def store_gpt_response_to_csv(gpt_response, output_file):
    """
    Reads GPT response (JSON format) and writes it to a CSV file with consistent quotes for all fields.
    """
    fieldnames = ["Title", "Authors"]

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)  # Use QUOTE_ALL for consistent quotes
        writer.writeheader()
        for article in gpt_response:
            writer.writerow(article)
            
            
def csv_to_html(csv_file, html_file):
    """
    Reads a CSV file and generates an HTML file with articles formatted in a specific style.
    
    Parameters:
    csv_file (str): Path to the CSV file containing the articles.
    html_file (str): Path to the output HTML file.
    """
    # Read the CSV file into a DataFrame
    df_articles = pd.read_csv(csv_file)
    
    # Start generating the HTML content
    html_content = '<div id="articles-content">\n'

    for index, row in df_articles.iterrows():
        # Add border style for articles after the first
        border_style = "border-top: 1px solid #000; padding: 15px;" #if index > 0 else "padding: 15px;"
        
        # Start the article section
        article_html = f'<article style="{border_style}">\n'
        
        # Add title
        article_html += f'    <h3 style="margin: 5px 0;">{row["Title"]}</h3>\n'
        
        # Add authors
        article_html += f'    <div>{row["Authors"]}</div>\n'
        
        # Close the article section
        article_html += '</article>\n'
        
        # Append the article HTML to the main content
        html_content += article_html

    # Close the main div
    html_content += '</div>\n'

    # Save the HTML content to the specified file
    with open(html_file, 'w', encoding='utf-8') as file:
        file.write(html_content)

    print(f"HTML content for in-press articles successfully saved to {html_file}")


            

if __name__ == "__main__":
    pdf_path = "InPress/s13.pdf"  # Replace with the actual path to your PDF
    text = read_pdf_to_text(pdf_path)

    prompt = "Focus on extracting the 'In-Press Articles' section (not the articles on top, but the articles at the end of pdf) from the text. Structure each article as JSON with 'Title' and 'Authors'. Only reply to me Json code and nothing else."

    try:
        gpt_response_raw = query_gpt_with_text(text, prompt)
        print("Raw GPT Response:", gpt_response_raw)

        # Clean and parse GPT response
        gpt_response = clean_gpt_response(gpt_response_raw)
        # gpt_response = json.loads(gpt_response_raw)

        # Write to CSV
        store_gpt_response_to_csv(gpt_response, "in_press_articles.csv")
        print("CSV file created successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


    # CSV to HTML
    csv_to_html('in_press_articles.csv', 'in_press_articles.html')