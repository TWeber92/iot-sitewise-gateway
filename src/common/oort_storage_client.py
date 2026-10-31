import boto3
import json
from botocore.client import Config
from src.common.logger import Logger


class OORTStorageClient:
    def __init__(self, access_key, secret_key, bucket):
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            endpoint_url="https://s3-standard.oortech.com",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name="us-east-1",
            config=Config(signature_version="s3v4"),
        )

    def get_json(self, key):
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return json.loads(response["Body"].read().decode("utf-8"))
        except Exception as e:
            Logger.emit("error", {"source": "OORTStorageClient", "message": str(e)})
            raise

    def put_json(self, key, data):
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=json.dumps(data),
                ContentType="application/json",
            )
            return True
        except Exception as e:
            Logger.emit("error", {"source": "OORTStorageClient", "message": str(e)})
            raise
