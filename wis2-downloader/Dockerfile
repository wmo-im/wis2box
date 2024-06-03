# Use an official Python runtime as a parent image
FROM python:3.9-slim

EXPOSE 5000

# define config variables
ENV DOWNLOAD_DIR /app/downloads
ENV MAX_MB_DOWNLOAD_DIR 1000
ENV RETENTION_PERIOD_HOURS 24
ENV BROKER_URL "globalbroker.meteo.fr"
ENV BROKER_PORT 443
ENV BROKER_USERNAME "everyone"
ENV BROKER_PASSWORD "everyone"
ENV BROKER_PROTOCOL "websockets"
ENV FLASK_HOST "0.0.0.0"
ENV FLASK_PORT 5000
ENV DOWNLOAD_WORKERS 8
ENV SAVE_LOGS false
ENV LOGS_DIR /app/logs

# update pyopenssl and pin requests and urllib3 to avoid SSL error
RUN pip install pyopenssl --upgrade && pip install requests==2.26.0 urllib3==1.26.0
# install cron and envsubst
RUN apt-get update && apt-get install -y cron gettext-base

# copy all the code to the Docker image
COPY . /app

# Set the working directory to /app
WORKDIR /app

# install wis2-downloader
RUN pip install https://github.com/wmo-im/wis2-downloader/archive/main.zip

# add wis2box.cron to crontab
COPY ./clean.cron /etc/cron.d/clean.cron

# set permissions for the cron job and install it
RUN chmod 0644 /etc/cron.d/clean.cron && crontab /etc/cron.d/clean.cron

# set permissions for the entrypoint script
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT [ "/app/entrypoint.sh" ]

# Run wis2-downloader when the container launches
CMD ["wis2downloader","--config","/app/config.json"]
