import asyncio
import logging
import requests
import json
import sys
from pathlib import Path
# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))
from minio_api import MinioApi

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_minio_and_api():
    minio_api = None
    try:
        API_URL = "http://127.0.0.1:8000"  # Backend URL
        
        # Health Check
        logger.info("Testing health check endpoint")
        response = requests.get(f"{API_URL}/health")
        logger.info(f"Health check response: {response.json()}")

        # Initialize MinIO client
        minio_api = MinioApi()
        
        # Test file path
        test_file_path = Path("C:/Users/ishan/Pictures/demo/tcga_10.png")
        if not test_file_path.exists():
            logger.error(f"Test file not found at {test_file_path}")
            return

        # Create bucket
        bucket_name = "test-bucket"
        logger.info(f"Creating bucket: {bucket_name}")
        response = requests.post(f"{API_URL}/bucket/create/{bucket_name}")
        logger.info(f"Create bucket response: {response.json()}")

        # Upload file
        logger.info(f"Uploading file: {test_file_path.name}")
        with open(test_file_path, 'rb') as f:
            files = {'file': (test_file_path.name, f, 'image/png')}
            response = requests.post(
                f"{API_URL}/bucket/{bucket_name}/upload",
                files=files
            )
        logger.info(f"Upload response: {response.json()}")

        # List files
        logger.info("Listing files in bucket")
        response = requests.get(f"{API_URL}/bucket/{bucket_name}")
        logger.info(f"List files response: {response.json()}")

        # Cleanup
        logger.info("Cleaning up...")
        response = requests.delete(f"{API_URL}/bucket/delete/{bucket_name}")
        logger.info(f"Cleanup response: {response.json()}")

        logger.info("All tests completed successfully")

    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_minio_and_api())