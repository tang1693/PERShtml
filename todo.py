import runpy
import requests
import warnings
import logging
import os
import urllib3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 1. Suppress General Python Warnings (Deprecation, etc.)
warnings.filterwarnings("ignore")

# 2. Suppress SSL/Insecure Request Warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 3. Suppress Selenium and Library Logging
logging.getLogger('selenium').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# 4. Silence Chrome Browser Console Logs
options.add_argument("--log-level=3") 
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=options)

















# 第一步 先来这儿看看 https://www.ingentaconnect.com/content/asprs/pers 
# 如果有新的issue，去Google drive 看看是否已经有GA
# https://drive.google.com/drive/folders/1vgP1MI7tQmGU6uJnP94W5PsWTxUVQkFT
# 把 GA 下载到 IssuesArticles/html/img/year/month/ 文件夹下
# 把时间调整到 下个月 (setting/general/date and time/ ). 如果Ingenta提前发了的话!~
# 然后直接运行就好. 下面的不需要去动了就

# 跑这个过程大概10分钟~

#跑完了记得把时间调整回去
# Git推送到服务器
# 去网页上看看, 是否正确捏

# 1. 然后就准备更新Editor choice
# 2. 准备更新公众号捏. 
# 3. 把Editor choice 简介发给GPT 然后发给 YUKI Day ASPRS Office <office@asprs.org>





# 1. update InPress. 
print("❤️❤️❤️1.1. update InPress. ")
runpy.run_path("1_InPress/1_read_ingenta_generate_html.py")
print("❤️❤️❤️1.2. load csv and visit website and load abs to csv. ")
runpy.run_path("1_InPress/2_load_csv_visit_website_load_abs_2_csv.py")
print("❤️❤️❤️1.3. csv to html. ")
runpy.run_path("1_InPress/3_csv_2_html.py")

# - exam: 1_InPress/filtered_InPress_articles_info_abs.csv
# - exam: 1_InPress/processed_urls.log

# //deprecated
# - dwoanload inpress pdf from ingenta.
# https://www.ingentaconnect.com/contentone/asprs/pers/2025/00000091/00000002
# https://www.ingentaconnect.com/contentone/asprs/pers/yyyy/00000091/000000mm
# 91 is issues refers to the year 2025
# - put it to InPress folder
# - change the file name to s13.pdf
# - run python inpress_pdf2html_GPT.py
# - exam: in_press_articles.csv
# - exam: in_press_articles.html

# 2. Issues
print("❤️❤️❤️2. Issues. ")
runpy.run_path("2_Issues/issues_generate_html.py")
# - exam: issues.html 
# check if latest issues exist.
# if latest issue is not available, change the local year and run again.


# 3. MostCited
# - fetch google scholar citation. two ways.
#     - use 3 request per day. from scholarly. => articles_with_citation_scholarly.csv
#     - use serpdog 10k per day. => articles_with_citation.csv (remember to add the apikey and remove it after use)
#     https://api.serpdog.io/

# - run most_cite_1csv_{{method}}.py to get the csv 
# - most_cited_2sort_csv_citation_descend.py => sorted_articles_with_citation.csv
# - get sorted csv.
# - only use the top 6 csv to generate html
# - exam: top_6_articles.html

# 4. Most Download
# - download the most recent csv with download data.
# - run python: most_download_csv2html.py
# - exam: most_download_articles.html

# 5. Recent Articles 
# - run rencent_articles_1screaper.py (if issue were released ahead of time. change local time to next monoth and run.) 
print("❤️❤️❤️5.1. Recent Articles. ")
runpy.run_path("5_RecentArticles/recent_article_1scraper.py")
# it fet all the info from recent 24 issues. and collect them to the pool
# - run recent_articles_2generate_html.py
print("❤️❤️❤️5.2. Recent Articles. ")
runpy.run_path("5_RecentArticles/recent_article_2generate_html.py")
# it generates all the artilces in the pool to html. and the html on pers will select them randomly
# exam: member_only_articles and open_access_articles html

# 6. Update the IssuesArticles
# goto S3 bucket to download the issues GA.
# https://us-east-1.console.aws.amazon.com/s3/buckets/persearlyaccess?region=us-east-1&tab=objects&bucketType=general
# use tang.1693 account
# or download from https://www.ingentaconnect.com/content/asprs/pers

# - download the issues GA.
# - check all the GA is added to the 6_IssuesArticles/IssuesArticles/html/img/year/month/ same name as the article title.
# - run 
print("❤️❤️❤️6.1. Update the IssuesArticles. ")
runpy.run_path("6_IssuesArticles/recent_article_1scraper.py")
# (if issue were released ahead of time. change local time to next monoth and run.)
# then 
# remove_dublicated_rows_CSV.py
print("❤️❤️❤️6.2. Update the IssuesArticles. ")
runpy.run_path("6_IssuesArticles/remove_dublicated_rows_CSV.py")

# to get the new articles. 
# if you need to rerun part of whole of the process. delete the processed_urls.log and run the process again.
# the csv file is ALL_articles_Update.csv
# - then goes to IssuesArticles/remove_dublicated_rows_CSV.py to remove the duplicate rows.
# the csv file is ALL_articles_Update_cleaned.csv
# - run 
print("❤️❤️❤️6.3. Update the IssuesArticles. ")
runpy.run_path("6_IssuesArticles/generate_article_page.py")
# generate_articles_page.py 

# to generate the html.
# if you need to rerun part of whole of the process. delete the processed_issues.log and run the process again.
# - exam: /IssuesArticles/html/yyyymm.html

print("❤️❤️❤️ FINISH SUCCESSFULLY ❤️❤️❤️")

# !!!!!!!
# add the editor's choice to the html.
# beloe this part of the HTML:
#       <div style="display: flex; justify-content: space-between; align-items: center;">
#             <div style="font-weight: bold; color: gray;">Research Articles </div>
#       </div>

# add the following:    
#     <span style="background-color: gold; color: black; font-weight: bold; padding: 3px 8px; border-radius: 5px; font-size: 12px; margin-left: 0px;">
#         Editor’s Choice
#     </span>


