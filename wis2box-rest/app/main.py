import os
from fastapi import FastAPI
from minio import Minio
from models import UploadData

# Get environment variables
HOST = os.getenv('WIS2BOX_STORAGE_SOURCE', 'http://minio:9000')
ACCESS_KEY = os.getenv('WIS2BOX_STORAGE_USERNAME')
SECRET_KEY = os.getenv('WIS2BOX_STORAGE_PASSWORD')
INCOMING_BUCKET = os.getenv('WIS2BOX_STORAGE_INCOMING')

# Initialize Minio client
client = Minio(
    HOST,
    access_key=ACCESS_KEY,
    secret_key=SECRET_KEY,
    secure=True
)

# Initialize FastAPI app
app = FastAPI()


@app.post("/upload_data")
async def upload_data(data: UploadData):
    try:
        # Upload the data to the incoming bucket
        client.put_object(INCOMING_BUCKET, data.title,
                          data.content, len(data.content))
        return {
            "message": f"Data uploaded successfully to {INCOMING_BUCKET}/{data.title}"  # noqa
        }
    except Exception as e:
        return {
            "message": f"Error uploading data to {INCOMING_BUCKET}: {str(e)}"  # noqa
        }
