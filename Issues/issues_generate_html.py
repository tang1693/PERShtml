import requests
from bs4 import BeautifulSoup
from datetime import datetime

def check_most_recent_issue(url):
    """
    Checks if the most recent issue is available by trying to access the URL.
    Returns True if accessible, False otherwise.
    """
    try:
        response = requests.get(url)
        return response.status_code == 200
    except Exception as e:
        print(f"Error accessing {url}: {e}")
        return False

def check_access_status(url):
    """
    Checks if the most recent issue is fully accessible or partially accessible.
    Returns "Full access" if fully accessible, otherwise "Partial Open Access content".
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            access_icon = soup.find("span", class_="access-icon")
            if access_icon and "Partial Open Access content" in access_icon.img.get("title", ""):
                return "Partial Open Access content"
            return "Full access"
        else:
            return None
    except Exception as e:
        print(f"Error accessing {url}: {e}")
        return None

def calculate_volume(year):
    """
    Calculates the volume number based on the year.
    Volume 90 corresponds to the year 2024, and it increments or decrements by 1 each year.
    """
    base_year = 2024
    base_volume = 90
    return base_volume + (year - base_year)

def generate_issue_links(year, volume, start_issue=1, end_issue=12, check_latest_only=False):
    """
    Generates a list of issues for a given year and volume.
    Issues are listed from December to January.
    """
    issues = []
    for issue in range(end_issue, start_issue - 1, -1):  # Descending from Dec to Jan
        url = f"https://www.ingentaconnect.com/content/asprs/pers/{year}/000000{volume}/000000{issue:02d}"
        print(url)
        if check_latest_only and issue == end_issue and year == datetime.now().year:
            # Only check the most recent issue
            if not check_most_recent_issue(url):
                continue  # Skip if the most recent issue is not available
            access_status = check_access_status(url)
        else:
            # Assume all other issues are available and set to full access by default
            access_status = "Full access"

        issues.append((url, f"No. {issue}, {datetime(year, issue, 1).strftime('%b %Y')}", access_status))
    
    return issues

def generate_html():
    """
    Generates the HTML block for all issues from January 2023 to the current month.
    """
    start_year = 2003
    current_year = datetime.now().year
    current_month = datetime.now().month
    html_output = '<div style="margin: 40px;">\n'
    # html_output += '<strong style="font-size: 32px; display: block; margin-bottom: 20px;">All Issues</strong>\n'
    html_output += '<div style="display: flex; flex-wrap: wrap; gap: 20px;">\n'

    for year in range(current_year, start_year - 1, -1):
        volume = calculate_volume(year)  # Calculate the volume based on the year
        start_issue = 1
        end_issue = 12 if year != current_year else current_month  # Only up to the current month for the current year

        # Only check the most recent issue if we're in the current year
        check_latest_only = (year == current_year)
        
        issues = generate_issue_links(year, volume, start_issue, end_issue, check_latest_only)
        html_output += '<div style="flex: 1 1 calc(20% - 20px);">\n'
        html_output += f'<ul class="bobby" style="padding: 0; list-style: none;">\n'
        html_output += f'    <li class="issueVolume" style="font-size: 12px; font-weight: 700;">Volume {volume}</li>\n'

        for url, issue_name, access_status in issues:
            access_html = f' <strong style="color: green;">{access_status}</strong>' if access_status == "Full access" else ""
            html_output += f'    <li><a href="{url}" rel="noreferrer" >{issue_name}</a>{access_html}</li>\n'

        html_output += '</ul>\n</div>\n'

    html_output += '</div>\n'
    html_output += '<div style="text-align: center; margin-top: 20px;">\n'
    # html_output += '<a href="https://www.asprs.org/pers-archives-of-the-past" style="font-size: 16px; text-decoration: none; color: #1b5faa; padding: 10px 20px; background-color: #f1f1f1; border-radius: 5px;">More Issues</a>\n'
    html_output += '</div>\n</div>'

    return html_output

# Generate the HTML
html_content = generate_html()

# Save the HTML output to a file
with open('issues.html', 'w') as f:
    f.write(html_content)

print("HTML file 'issues.html' has been generated.")
