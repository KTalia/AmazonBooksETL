# 📚 Book ETL Pipeline Project

This is a personal ETL (Extract, Transform, Load) project that automates the process of scraping book data from Literatura.mk, storing it in a PostgreSQL database, and exporting it to CSV files for analysis and visualization. The project aims to extract insights on book pricing, categories, and trends over time.

---

## Technologies Used

- **Python** – Data processing and automation (Selenium, Pandas)
- **Apache Airflow** – Workflow orchestration using DAGs for task scheduling
- **Docker** – Containerization and environment setup
- **PostgreSQL** – Relational database to store scraped data efficiently
- **Power BI** – Data visualization and dashboard creation for insights
- **ChromeDriver + Selenium** – Headless web scraping for automated data collection

---

## Features

- 🔁 Automated Weekly Scraping using Airflow
- 💾 Stores structured data in PostgreSQL
- 📤 CSV export for Power BI
- 📊 Visualizations in Power BI
- 🐳 Fully containerized with Docker
---
## Project Structure
```
Books_ETL_Pipeline/
│
├── dags/                           
│   ├── dag.py                      # Main DAG file that defines the flow of tasks
│   ├── preprocess_data.ipynb       # Jupyter notebook for preprocessing the data
│   └── preprocessed_data.csv       # CSV file that stores the processed data
│
├── Dockerfile                      # Dockerfile for containerizing the application
├── docker-compose.yaml             # Defines the services needed for the project 

```
## How It Works

1. **Extract:**  
   Scrapes book title, author, category, and price from the Literatura.mk site using Selenium.

2. **Transform:**  
   Cleans and processes data using Pandas, filling missing values and standardizing fields.

3. **Load:**  
   Stores the processed data in a PostgreSQL database and exports a snapshot to CSV for further     analysis.
4. **Visualize:**  
   Data is analyzed in Power BI via imported CSVs, with charts for:
   - Category distribution  
   - Price outliers  
---
## Airflow DAG Overview

The DAG `fetch_and_store_books` is scheduled to run weekly and performs the following steps:

1. **create_table** – Ensures the PostgreSQL tables (`books` and `book_prices`) exist.
2. **fetch_book_data** – Uses Selenium to scrape up to 20,000 books from literatura.mk and pushes the data to Airflow XCom.
3. **insert_book_data** – Inserts new books into the `books` table and tracks their prices over time in `book_prices`.
4. **export_data_to_csv** – Exports data from both tables into timestamped CSV files for Power BI analysis.

Tasks are executed in the following order:

```text
create_table --> fetch_book_data --> insert_book_data --> export_data_to_csv
```
---
## Power BI Dashboard
![dashboard](https://github.com/user-attachments/assets/23119db2-96a3-40b6-974f-ac36169925e2)

---
## Notable Challenges
- Running Selenium and ChromeDriver in a headless Docker container
- Scraping dynamically loaded content with Selenium
- Passing data between Airflow tasks using XCom
- Managing missing or inconsistent data during the scraping process
---
## Future Changes/Additions
- **Expand Data Sources & Price Comparison** – Integrate additional websites for scraping book data and create visualizations to compare prices for the same books across different platforms.
- **Advanced Visualizations** – Add price trend analysis and category-based insights in Power BI.
- **Machine Learning for Pricing Predictions** Incorporate machine learning models (e.g., regression, time series forecasting) to predict future book prices or category trends based on historical data.




















