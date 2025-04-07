FROM apache/airflow:2.10.5-python3.12

USER root

RUN apt-get update && apt-get install -y wget unzip && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean

USER airflow

RUN pip install --no-cache-dir selenium
RUN pip install webdriver_manager
