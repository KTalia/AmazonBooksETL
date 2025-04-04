FROM apache/airflow:2.10.5-python3.12

USER root

RUN apt-get update && apt-get install -y wget unzip && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean


# # Install Chromium and required libraries
# RUN apt-get update && apt-get install -y \
#     chromium \
#     chromium-driver \
#     fonts-liberation \
#     libappindicator3-1 \
#     libasound2 \
#     libatk-bridge2.0-0 \
#     libatk1.0-0 \
#     libcups2 \
#     libdbus-1-3 \
#     libgdk-pixbuf2.0-0 \
#     libnspr4 \
#     libnss3 \
#     libxcomposite1 \
#     libxdamage1 \
#     libxrandr2 \
#     xdg-utils \
#     --no-install-recommends && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Install Python packages
RUN pip install --no-cache-dir selenium
RUN pip install webdriver_manager
