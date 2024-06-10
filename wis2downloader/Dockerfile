# Use an official Python runtime as a parent image
FROM python:3.9-slim

EXPOSE 5000

# define config variables
ENV DOWNLOAD_DIR /app/downloads
ENV DOWNLOAD_RETENTION_PERIOD_HOURS 24
ENV DOWNLOAD_BROKER_HOST "globalbroker.meteo.fr"
ENV DOWNLOAD_BROKER_PORT 443
ENV DOWNLOAD_BROKER_USERNAME "everyone"
ENV DOWNLOAD_BROKER_PASSWORD "everyone"
ENV DOWNLOAD_BROKER_TRANSPORT "websockets"
ENV DOWNLOAD_WORKERS 8
ENV DOWNLOAD_MAX_VOLUME_MB 100
ENV SAVE_LOGS false
ENV LOG_PATH /app/logs
ENV WIS2DOWNLOADER_CONFIG "/app/config.json"

# update pyopenssl and pin requests and urllib3 to avoid SSL error
RUN pip install pyopenssl --upgrade && pip install requests==2.26.0 urllib3==1.26.0
# install cron and envsubst and guincorn
RUN apt-get update && apt-get install -y cron gettext-base gunicorn

# copy all the code to the Docker image
COPY . /app

# Set the working directory to /app
WORKDIR /app

# install wis2downloader from github branch=minor-fixes
RUN pip3 install https://github.com/wmo-im/wis2downloader/archive/minor-fixes.zip

# add wis2box.cron to crontab
COPY ./clean.cron /etc/cron.d/clean.cron

# set permissions for the cron job and install it
RUN chmod 0644 /etc/cron.d/clean.cron && crontab /etc/cron.d/clean.cron

# set permissions for the entrypoint script
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT [ "/app/entrypoint.sh" ]

# Run wis2downloader when the container launches
CMD ["gunicorn","--bind","0.0.0.0:5000","--pythonpath","/usr/local/lib/python3.9/site-packages/","--workers", "1", "wis2downloader.app:app"]