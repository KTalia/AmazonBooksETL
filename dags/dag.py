from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from webdriver_manager.chrome import ChromeDriverManager
import csv
from datetime import datetime
import os
def get_default_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")

    return options

def get_data_books(num_books,ti):
    # SETUP
    options = get_default_chrome_options()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

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

    books_df = pd.DataFrame(book_data)
    books_df.drop_duplicates(subset="Title", inplace=True)

    # books_df.to_csv('books_data2.csv', index=False, encoding='utf-8-sig')
    driver.quit()

    ti.xcom_push(key='book_data', value=book_data)

def insert_book_data_into_postgres(ti):
    # Pull data from XCom
    book_data = ti.xcom_pull(key='book_data', task_ids='fetch_book_data')
    if not book_data:
        raise ValueError("No book data found")

    # Convert to DataFrame and clean
    books_df = pd.DataFrame(book_data)
    books_df = books_df.dropna(subset=['Title'])
    books_df = books_df[books_df['Title'].apply(lambda x: isinstance(x, str))]

    # Set up database connection
    postgres_hook = PostgresHook(postgres_conn_id='books_connection')
    conn = postgres_hook.get_conn()
    cursor = conn.cursor()
    retrieved_at = datetime.now().date()

    try:
        for _, book in books_df.iterrows():
            title = book.get('Title')
            author = book.get('Author', None)
            category = book.get('Category', None)
            price = book.get('Price', None)

            if not title or price is None:
                continue

            insert_book_sql = """
            INSERT INTO books (title, author, category)
            VALUES (%s, %s, %s)
            ON CONFLICT (title) DO NOTHING;
            """
            cursor.execute(insert_book_sql, (title, author, category))

            cursor.execute("SELECT id FROM books WHERE title = %s", (title,))
            result = cursor.fetchone()
            if not result:
                continue
            book_id = result[0]

            insert_price_sql = """
            INSERT INTO book_prices (book_id, price, retrieved_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (book_id, retrieved_at) DO NOTHING;
            """
            cursor.execute(insert_price_sql, (book_id, price, retrieved_at))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()



def export_data_to_csv():
    hook = PostgresHook(postgres_conn_id='books_connection')
    conn = hook.get_conn()
    cursor = conn.cursor()
    
    output_directory = f'./dags/datasets/{datetime.now().strftime("%Y.%m.%d")}/'
    os.makedirs(output_directory, exist_ok=True)  # Ensure folder exists

    # Export books
    cursor.execute("SELECT * FROM books;")
    books_rows = cursor.fetchall()
    books_columns = [desc[0] for desc in cursor.description]
    books_file_name = f'{output_directory}books_data_{datetime.now().strftime("%Y.%m.%d.%H-%M")}.csv'

    with open(books_file_name, 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(books_columns)
        writer.writerows(books_rows)

    # Export book_prices
    cursor.execute("SELECT * FROM book_prices;")
    prices_rows = cursor.fetchall()
    prices_columns = [desc[0] for desc in cursor.description]
    prices_file_name = f'{output_directory}book_prices_data_{datetime.now().strftime("%Y.%m.%d.%H-%M")}.csv'

    with open(prices_file_name, 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(prices_columns)
        writer.writerows(prices_rows)

    cursor.close()
    conn.close()

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 3, 22),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'fetch_and_store_books',
    default_args=default_args,
    description='Fetch book data and store it normalized into Postgres with price tracking',
    schedule_interval='@weekly',
)

fetch_book_data_task = PythonOperator(
    task_id='fetch_book_data',
    python_callable=get_data_books,
    op_args=[20000], 
    dag=dag,
)

create_table_task = SQLExecuteQueryOperator(
    task_id='create_table',
    conn_id='books_connection',
    sql="""
    
    CREATE TABLE IF NOT EXISTS books (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL UNIQUE,
        author TEXT,
        category TEXT
    );

    CREATE TABLE IF NOT EXISTS book_prices (
        id SERIAL PRIMARY KEY,
        book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
        price TEXT,
        retrieved_at DATE NOT NULL,
        UNIQUE(book_id, retrieved_at)
    );
    """,
    dag=dag,
)

insert_book_data_task = PythonOperator(
    task_id='insert_book_data',
    python_callable=insert_book_data_into_postgres,
    dag=dag,
)

export_data_task = PythonOperator(
    task_id='export_data_to_csv',
    python_callable=export_data_to_csv,
    dag=dag,
)

create_table_task >> fetch_book_data_task >> insert_book_data_task >> export_data_task