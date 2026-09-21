import json

from src.common.sitewise_client import get_sitewise_client
from src.models.asset import Asset
from src.models.child import Child


def get_child_assets(client, parent: Asset, body: dict) -> list:
    child_assets = []
    child_names = set(body['childNames'])
    parent_details = client.describe_asset(assetId=parent.asset_id)
    for hierarchy in parent_details['assetHierarchies']:
        response = client.list_associated_assets(
            assetId=parent.asset_id,
            hierarchyId=hierarchy['id'],
            traversalDirection='CHILD',
            maxResults=100
        )
        for asset_summary in response['assetSummaries']:
            child_asset_details = client.describe_asset(assetId=asset_summary['id'])
            if child_asset_details['assetName'] in child_names:
                child = Child(asset_summary['id'], child_asset_details['assetName'])
                child_assets.append(child.to_dict())

    return child_assets
    


def lambda_handler(event, context):
    client = get_sitewise_client()
    body = event['body']
    parent = Asset(body['parent_asset_id'])

    results = get_child_assets(client, parent, body)
    child_assets = {child['name']: child['id'] for child in results}

    return {
        'statusCode': 200,
        'body': json.dumps(child_assets)
    }