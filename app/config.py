import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # AWS S3
    S3_BUCKET = os.getenv('S3_BUCKET', 'default-bucket-name')
    S3_REGION = os.getenv('S3_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'your-access-key-id')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'your-secret-access-key')
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-api-key')
    
    # Other configs
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    DEBUG = os.getenv('DEBUG', False) == 'True'