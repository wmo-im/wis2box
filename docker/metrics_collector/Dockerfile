FROM python:3-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
	
COPY requirements.txt /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt
	
COPY *_collector.py /usr/src/app/
	
EXPOSE 8000

ENV PYTHONUNBUFFERED="true"
	
ENTRYPOINT [ "python3","-u","metrics_collector.py" ]
