import boto3

def get_sitewise_client():
    """Return a boto3 IoT SiteWise client.

    Handlers should call this instead of creating their own client so tests
    can patch it with a mock.
    """
    return boto3.client('iotsitewise')