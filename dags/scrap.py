from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import warnings
warnings.filterwarnings('ignore')
import pandas as pd

def get_default_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    return options

options = get_default_chrome_options()

chromedriver_path = r"C:\Users\admin\Desktop\AmazonBooksETL\dags\chromedriver.exe"
url = "https://literatura.mk/knigi/makedonska-knizevnost"

service = Service(chromedriver_path)

driver = webdriver.Chrome(service=service, options=options)

driver.get(url)
time.sleep(5)

# Find all books on the page
books = driver.find_elements(By.CSS_SELECTOR, ".item-data.col-xs-12.col-sm-12")

book_data = []

# Iterate over each book element and extract details
for book in books:
    try:
        # title
        title_div = book.find_element(By.CLASS_NAME, "title")        
        title = title_div.find_element(By.TAG_NAME, "a").text.strip()

        # author
        author = book.find_element(By.CLASS_NAME, "atributs-wrapper .value").text.strip()

        # price
        price = book.find_element(By.CLASS_NAME, "prices-wrapper .current-price")  
        clean_price = price.text.replace("МКД", "").strip()

        # category
        category = book.find_element(By.CLASS_NAME, "category-wrapper .category").text.strip()

        
        book_data.append({
            "Title": title,
            "Author": author,
            "Price": clean_price,
            "Category": category,
        })

    except Exception as e:
        print(f"Error extracting book details: {e}")


books_df = pd.DataFrame(book_data)
print(books_df)

# Close the driver
driver.quit()
