import os
import time
import random
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- 配置 ---
csv_filename = '6_IssuesArticles/test/ALL_articles_Selenium_2018.csv'
log_filename = '6_IssuesArticles/test/processed_urls.log'
os.makedirs(os.path.dirname(csv_filename), exist_ok=True)

def setup_driver():
    """初始化 Chrome 浏览器配置"""
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # 如果调试成功后想静默运行，取消注释
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 隐藏 Selenium 特征，防止被识别
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
        """
    })
    return driver

def get_urls():
    """生成 2018 至今的 URL"""
    urls = []
    start_date = datetime(2018, 1, 1)
    current = datetime.today()
    while current >= start_date:
        vol = 89 + (current.year - 2023)
        url = f"https://www.ingentaconnect.com/content/asprs/pers/{current.year}/{vol:08d}/{current.month:08d}"
        urls.append(url)
        current -= relativedelta(months=1)
    return urls

def scrape():
    driver = setup_driver()
    urls = get_urls()
    
    # 读取进度
    processed = set()
    if os.path.exists(log_filename):
        with open(log_filename, 'r') as f:
            processed = set(f.read().splitlines())

    for url in urls:
        if url in processed: continue
        
        print(f"🚀 正在访问目录页: {url}")
        try:
            driver.get(url)
            # 等待文章标题加载（最多等15秒）
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "heading")))
            
            # 获取当前页所有文章的链接
            article_elements = driver.find_elements(By.CSS_SELECTOR, "div.data strong a")
            article_links = [el.get_attribute('href') for el in article_elements]
            
            page_data = []
            for link in article_links:
                print(f"  📖 正在抓取详情: {link[-15:]}")
                driver.get(link)
                time.sleep(random.uniform(2, 4)) # 模拟阅读
                
                try:
                    title = driver.find_element(By.TAG_NAME, "h1").text
                    # 尝试多种方式抓取作者和机构
                    authors = driver.find_element(By.CLASS_NAME, "contributions").text if driver.find_elements(By.CLASS_NAME, "contributions") else "N/A"
                    
                    # 抓取 Affiliations
                    affs = driver.find_elements(By.CLASS_NAME, "aff")
                    affiliations = " | ".join([a.text for a in affs]) if affs else "N/A"
                    
                    # 抓取 Abstract
                    abst_box = driver.find_elements(By.ID, "Abst")
                    abstract = abst_box[0].text if abst_box else "N/A"
                    
                    page_data.append({
                        'Title': title, 'Authors': authors, 'Affiliations': affiliations,
                        'URL': link, 'Abstract': abstract
                    })
                except Exception as e:
                    print(f"  ❌ 详情页解析失败: {e}")
                
                driver.back() # 返回列表页
                time.sleep(1)

            # 保存数据
            if page_data:
                df = pd.DataFrame(page_data)
                df.to_csv(csv_filename, mode='a', header=not os.path.exists(csv_filename), index=False, encoding='utf-8-sig')
            
            with open(log_filename, 'a') as f: f.write(url + '\n')
            print(f"✅ 完成一期保存。")

        except Exception as e:
            print(f"💥 目录页访问失败（可能是403或验证码）: {url}")
            # 如果出现验证码，脚本会停在这里，你可以手动在弹出的 Chrome 里点一下验证码，然后脚本会继续
            input("请在浏览器中完成验证码，然后按回车继续...") 

    driver.quit()

if __name__ == "__main__":
    scrape()