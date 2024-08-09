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
ENV DOWNLOAD_MIN_FREE_SPACE_GB 1
ENV DOWNLOAD_VALIDATE_TOPICS "false"
ENV LOG_PATH /app/logs
ENV WIS2DOWNLOADER_CONFIG "/app/config.json"

# update pyopenssl and pin requests and urllib3 to avoid SSL error
RUN pip install pyopenssl --upgrade && pip install requests==2.32.3 urllib3==1.26.0
# install cron and envsubst and guincorn
RUN apt-get update && apt-get install -y cron gettext-base gunicorn

# copy all the code to the Docker image
COPY . /app

# Set the working directory to /app
WORKDIR /app

# install wis2downloader from pypi
RUN pip install wis2downloader==0.3.0

# add wis2box.cron to crontab
COPY ./clean.cron /etc/cron.d/clean.cron

# set permissions for the cron job and install it
RUN chmod 0644 /etc/cron.d/clean.cron && crontab /etc/cron.d/clean.cron

# set permissions for the entrypoint script
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT [ "/app/entrypoint.sh" ]

# Run wis2downloader when the container launches
CMD ["gunicorn","--bind","0.0.0.0:5000","--pythonpath","/usr/local/lib/python3.9/site-packages/","--workers", "1", "wis2downloader.app:app"]
