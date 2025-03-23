from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta
import requests


def get_default_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    # options.add_argument("--headless")

    return options

def get_amazon_data_books(num_books):
    # SETUP
    options = get_default_chrome_options()
    chromedriver_path = r"C:\Users\admin\Desktop\AmazonBooksETL\dags\chromedriver.exe"
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    time.sleep(5)

    book_data = []
    seen_titles = set()
    page = 1

    while len(book_data) < num_books:
        url = f"https://www.literatura.mk/knigi/page-{page}" if page > 1 else "https://www.literatura.mk/knigi/"
        driver.get(url)
        time.sleep(3)
        books = driver.find_elements(By.CSS_SELECTOR, ".item-data.col-xs-12.col-sm-12")

        if not books:  
            print("No books found on the page. Exiting loop.")
            break

        for book in books:
            try:
                # title
                title_div = book.find_element(By.CLASS_NAME, "title")
                title = title_div.find_element(By.TAG_NAME, "a").text.strip()

                # author
                try:
                    author = book.find_element(By.CSS_SELECTOR, ".atributs-wrapper .value").text.strip()
                except NoSuchElementException:
                    author = "N/A"

                # price
                price = book.find_element(By.CLASS_NAME, "prices-wrapper .current-price")
                clean_price = price.text.replace("МКД", "").strip()

                # category
                category = book.find_element(By.CLASS_NAME, "category-wrapper .category").text.strip()

                if title not in seen_titles:
                    seen_titles.add(title)
                    book_data.append({
                        "Title": title,
                        "Author": author,
                        "Price": clean_price,
                        "Category": category,
                    })

                    if len(book_data) >= num_books:
                        break

            except Exception as e:
                print(f"Error extracting book details: {e}")

        page += 1

    # After exiting the loop, save the data to a DataFrame and CSV
    books_df = pd.DataFrame(book_data)
    books_df.drop_duplicates(subset="Title", inplace=True)
    books_df.to_csv('books_data2.csv', index=False, encoding='utf-8-sig')

    driver.quit()

get_amazon_data_books(60)
