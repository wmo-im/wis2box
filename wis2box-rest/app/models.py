from pydantic import BaseModel


class UploadData(BaseModel):
    title: str
    content: bytes
