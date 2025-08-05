from minio import Minio
from minio.error import S3Error
import os
import uuid
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

class MinIOClient:
    def __init__(self):
        self.endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
        self.bucket_name = os.getenv("MINIO_BUCKET_NAME", "plant-images")
        
        # Initialize MinIO client
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False  # Set to True for HTTPS
        )
        
        # Create bucket if it doesn't exist
        self._create_bucket_if_not_exists()
    
    def _create_bucket_if_not_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                logger.info(f"Bucket already exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")
            raise
    
    def upload_image(self, file_data: bytes, file_extension: str) -> str:
        """Upload image to MinIO and return filename"""
        try:
            # Generate unique filename
            filename = f"{uuid.uuid4()}.{file_extension.lower()}"
            
            # Upload file
            self.client.put_object(
                self.bucket_name,
                filename,
                BytesIO(file_data),
                length=len(file_data),
                content_type=f"image/{file_extension.lower()}"
            )
            
            logger.info(f"Uploaded image: {filename}")
            return filename
            
        except S3Error as e:
            logger.error(f"Error uploading image: {e}")
            raise
    
    def get_image_url(self, filename: str) -> str:
        """Get presigned URL for image"""
        try:
            # For development, return direct URL
            return f"http://localhost:9002/{self.bucket_name}/{filename}"
        except S3Error as e:
            logger.error(f"Error getting image URL: {e}")
            raise
    
    def get_image(self, filename: str) -> bytes:
        """Get image data from MinIO"""
        try:
            # Get object data
            response = self.client.get_object(self.bucket_name, filename)
            image_data = response.read()
            response.close()
            response.release_conn()
            
            logger.info(f"Retrieved image: {filename}")
            return image_data
            
        except S3Error as e:
            logger.error(f"Error getting image: {e}")
            raise
    
    def delete_image(self, filename: str) -> bool:
        """Delete image from MinIO"""
        try:
            self.client.remove_object(self.bucket_name, filename)
            logger.info(f"Deleted image: {filename}")
            return True
        except S3Error as e:
            logger.error(f"Error deleting image: {e}")
            return False

# Global MinIO client instance
minio_client = MinIOClient()