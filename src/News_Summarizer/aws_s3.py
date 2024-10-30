import boto3
from botocore.exceptions import NoCredentialsError
import os
from dotenv import load_dotenv

load_dotenv()
session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')  # Optional, e.g., 'us-west-2'
)
from botocore.exceptions import NoCredentialsError

def download_model_from_s3(bucket_name, model_file, local_path):
    s3 = session.client('s3')
    
    # Check if the local file already exists
    if os.path.exists(local_path):
        print(f"Model already exists at {local_path}. Skipping download.")
        return

    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Download the file from S3
        s3.download_file(bucket_name, model_file, local_path)
        print(f"Downloaded {model_file} from S3 to {local_path}")
    except NoCredentialsError:
        print("Credentials not available")
    except Exception as e:
        print(f"Error downloading file: {e}")
