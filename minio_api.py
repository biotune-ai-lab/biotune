from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile
import io
import os
from config import config

class MinioAPI:
    def __init__(self):
        self.client = Minio(
            endpoint=config["MINIO_ENDPOINT"],
            access_key=config["MINIO_ACCESS_KEY"],
            secret_key=config["MINIO_SECRET_KEY"],
            secure=False
        )

    async def list_files(self, bucket_name: str):
        try:
            if not self.client.bucket_exists(bucket_name):
                return {"error": f"Bucket '{bucket_name}' does not exist"}
            
            objects = self.client.list_objects_v2(bucket_name)
            files = [{
                "name": obj.object_name,
                "size": obj.size,
                "last_modified": obj.last_modified.isoformat()
            } for obj in objects]
            
            return {
                "bucket": bucket_name,
                "files": files
            }
        except S3Error as e:
            return {"error": f"Error listing files: {str(e)}"}

    async def upload_file(self, bucket_name: str, file: UploadFile):
        try:
            content = await file.read()
            self.client.put_object(
                bucket_name,
                file.filename,
                io.BytesIO(content),
                length=len(content),
                content_type=file.content_type
            )
            return {"message": "File uploaded successfully"}
        except S3Error as e:
            return {"error": f"Error uploading file: {str(e)}"}

    async def download_file(self, bucket_name: str, filename: str):
        try:
            return self.client.get_object(bucket_name, filename)
        except S3Error as e:
            return {"error": f"Error downloading file: {str(e)}"}

    async def delete_file(self, bucket_name: str, filename: str):
        try:
            self.client.remove_object(bucket_name, filename)
            return {"message": "File deleted successfully"}
        except S3Error as e:
            return {"error": f"Error deleting file: {str(e)}"}

    async def create_bucket(self, bucket_name: str):
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                return {"message": f"Bucket '{bucket_name}' created successfully"}
            return {"message": f"Bucket '{bucket_name}' already exists"}
        except S3Error as e:
            return {"error": f"Error creating bucket: {str(e)}"}

    async def delete_bucket(self, bucket_name: str):
        try:
            self.client.remove_bucket(bucket_name)
            return {"message": f"Bucket '{bucket_name}' deleted successfully"}
        except S3Error as e:
            return {"error": f"Error deleting bucket: {str(e)}"}