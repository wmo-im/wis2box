 
# Use an official Python runtime as a parent image.
FROM python:3.10-slim

WORKDIR /src

# Copy only the file with the requirements first, not the rest of the code.
# As this file doesn't change often, Docker will detect it and use the cache for this step, enabling the cache for the next step too.
COPY ./requirements.txt /src/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

# Copy the application code to the container.
# As this has all the code which is what changes most frequently the Docker cache won't be used for this or any following steps easily.
COPY ./app /src/app

# Run FastAPI when the container launches, which uses Uvicorn underneath.
CMD ["fastapi", "run", "app/main.py", "--port", "80"]