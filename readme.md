# PERS HTML Project

This project automates the process of fetching article data from the PERS webpage on the IngentaConnect website, saving it to a CSV file, and generating an HTML file to display the articles dynamically on a website.

## Workflow Overview

1. **Scrape Data from PERS Webpage**: Use Python to read research articles from the IngentaConnect PERS webpage, extracting titles, authors, page numbers, access status, and URLs.
2. **Save to CSV**: Store the scraped article data in a CSV file (`filtered_articles_info.csv`).
3. **Generate HTML**: Convert the CSV file content into an HTML file (`articles.html`) for embedding in a web page.
4. **Load Articles HTML Dynamically**: Integrate `articles.html` into your main webpage using JavaScript to load the content dynamically.

## Steps

### Step 1: Run the Python Script to Scrape and Save Data

1. Execute the Python script to scrape articles from the PERS webpage on IngentaConnect.
2. The script saves the article data to `filtered_articles_info.csv`.

**Sample Python Code**:
Ensure the Python script is set up correctly to fetch the articles and output them to `filtered_articles_info.csv`.

### Step 2: Generate `articles.html` from CSV

1. After obtaining `filtered_articles_info.csv`, run the second Python script to generate `articles.html` based on the CSV data.
2. The HTML file will format each article according to the desired layout.

### Step 3: Upload `articles.html` to GitHub

1. Add `articles.html` to your GitHub repository.
2. Commit and push the file to make it available for GitHub Pages.

### Step 4: Use GitHub Pages to Host `articles.html`

1. Go to your repository on GitHub.
2. Navigate to **Settings** > **Pages**.
3. In the **Source** section, select the branch where `articles.html` is stored (typically `main`) and set the root directory.
4. Save your settings. GitHub Pages will provide a URL for your repository, such as `https://yourusername.github.io/your-repository-name/`.

Once GitHub Pages is set up, you can access `articles.html` at `https://yourusername.github.io/your-repository-name/articles.html`.

### Step 5: Integrate `articles.html` with JavaScript on Your Main HTML Page

1. **Create a Placeholder `<div>`**:
   In your main HTML file where you want the articles to appear, add a `<div>` with an ID (e.g., `articles-content`):

   ```html
   <div id="articles-content"></div>
   ```

2. **Add JavaScript to Load articles.html**:
 Include the following JavaScript code in your main HTML file to fetch and inject articles.html into the #articles-content div:
   ```javascript
   document.addEventListener("DOMContentLoaded", function() {
    // Fetch the articles HTML content and inject it into the placeholder div
    fetch('https://yourusername.github.io/your-repository-name/articles.html')
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok " + response.statusText);
            }
            return response.text();
        })
        .then(html => {
            document.getElementById('articles-content').innerHTML = html;
        })
        .catch(error => {
            console.error("Failed to load articles.html:", error);
            document.getElementById('articles-content').innerHTML = "<p>Failed to load articles. Please try again later.</p>";
        });
   });
   ```

   ```javascript
   async function loadRandomArticles() {
    // URLs of the HTML files
    const openAccessURL = 'path/to/open_access_articles.html';
    const memberOnlyURL = 'path/to/member_only_articles.html';

    // Fetch and parse the articles from each HTML file
    const openAccessArticles = await fetchArticles(openAccessURL);
    const memberOnlyArticles = await fetchArticles(memberOnlyURL);

    // Randomly select 3 articles from each group
    const selectedOpenAccess = selectRandomArticles(openAccessArticles, 3);
    const selectedMemberOnly = selectRandomArticles(memberOnlyArticles, 3);

    // Combine and display the selected articles
    const articlesContainer = document.getElementById('articles-content');
    articlesContainer.innerHTML = [...selectedOpenAccess, ...selectedMemberOnly].join('');
}

// Fetch and parse articles from a URL
async function fetchArticles(url) {
    try {
        const response = await fetch(url);
        const htmlText = await response.text();

        // Create a temporary DOM element to parse the HTML
        const parser = new DOMParser();
        const doc = parser.parseFromString(htmlText, 'text/html');

        // Extract all article elements
        return Array.from(doc.querySelectorAll('article')).map(article => article.outerHTML);
    } catch (error) {
        console.error(`Failed to load articles from ${url}`, error);
        return [];
    }
}

// Select a specified number of random articles from the list
function selectRandomArticles(articles, count) {
    const shuffled = articles.sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
}

// Run the function to load random articles on page load
loadRandomArticles();

   ```
   Replace https://yourusername.github.io/your-repository-name/articles.html with your actual GitHub Pages URL. for example https://tang1693.github.io/PERShtml/articles.html

## Updating the Articles
### Re-run the Python Scripts: To update the articles
re-run the Python scripts to scrape the latest data and regenerate filtered_articles_info.csv and articles.html.
### Push to GitHub: 
Commit and push the updated articles.html to your repository. GitHub Pages will automatically serve the latest version.


























