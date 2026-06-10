import boto3
import json
import pandas as pd
import os
from botocore.client import Config

# MinIO Config
MINIO_ENDPOINT = "http://localhost:9000"
MINIO_ACCESS_KEY = "minio"
MINIO_SECRET_KEY = "minio123"
BUCKET_NAME = "raffinerie-raw"

s3 = boto3.resource('s3',
                    endpoint_url=MINIO_ENDPOINT,
                    aws_access_key_id=MINIO_ACCESS_KEY,
                    aws_secret_access_key=MINIO_SECRET_KEY,
                    config=Config(signature_version='s3v4'),
                    region_name='us-east-1')

bucket = s3.Bucket(BUCKET_NAME)

data_list = []

print(f"Fetching data from bucket: {BUCKET_NAME}...")

try:
    for obj in bucket.objects.all():
        if obj.key.endswith('.json'):
            content = obj.get()['Body'].read().decode('utf-8')
            # Spark writes multiple JSON objects per file (one per line)
            for line in content.strip().split('\n'):
                if line:
                    data_list.append(json.loads(line))

    if data_list:
        df = pd.DataFrame(data_list)
        # Ensure timestamp is datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        output_path = "ml/historical_data.csv"
        df.to_csv(output_path, index=False)
        print(f"Successfully extracted {len(df)} records to {output_path}")
    else:
        print("No data found in MinIO.")

except Exception as e:
    print(f"Error: {e}")
