import os
from fastapi import FastAPI, UploadFile
from minio import Minio


# Get environment variables

HOST = os.getenv('WIS2BOX_STORAGE_SOURCE', 'minio:9000')
# Remove beginning http:// or https:// from the host to prevent invalid
# endpoint issues with the Minio client
HOST = HOST.replace('http://', '').replace('https://', '')

ACCESS_KEY = os.getenv('WIS2BOX_STORAGE_USERNAME')
SECRET_KEY = os.getenv('WIS2BOX_STORAGE_SECRET_PASSWORD')
INCOMING_BUCKET = 'wis2box-incoming'

# Initialize Minio client
client = Minio(
    endpoint=HOST,
    access_key=ACCESS_KEY,
    secret_key=SECRET_KEY,
    secure=True
)

# Initialize FastAPI app
app = FastAPI()


@app.post("/upload-file/")
def upload_file(data: UploadFile):
    if not data:
        return {
            "message": "No file uploaded"
        }
    try:
        # Upload the data to the incoming bucket
        client.fput_object(bucket_name=INCOMING_BUCKET,
                           object_name=data.filename,
                           file_path=data.file)
        return {
            "message": f"Data uploaded successfully to {INCOMING_BUCKET}/{data.filename}"  # noqa
        }
    except Exception as e:
        return {
            "message": f"Error uploading data to {INCOMING_BUCKET}: {str(e)}"  # noqa
        }
