import os
from dotenv import load_dotenv
from src.common.oort_storage_client import OORTStorageClient

load_dotenv()

oort = OORTStorageClient(
    os.environ["OORT_ACCESS_KEY"],
    os.environ["OORT_SECRET_KEY"],
    os.environ["OORT_BUCKET"],
)

key = "sitewise/assets/057bdfea-2dc4-4d21-8d0f-c54ffec0e36c.json"
print(f"Fetching: {key}")

try:
    data = oort.get_json(key)
    print("SUCCESS!")
    print(data)
except Exception as e:
    print(f"FAILED: {e}")
