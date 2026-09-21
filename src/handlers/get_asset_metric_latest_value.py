import json

from src.common.sitewise_client import get_sitewise_client
from src.models.asset import Asset


def get_latest_property_values(client, asset: Asset, allowed_suffixes: list) -> list:
    asset_details = client.describe_asset(assetId=asset.asset_id)

    property_values = []
    for prop in asset_details['assetProperties']:
        if not any(prop['name'].endswith(suffix) for suffix in allowed_suffixes):
            continue

        response = client.get_asset_property_value(
            assetId=asset.asset_id,
            propertyId=prop['id']
        )
        for value_key in response['propertyValue']['value']:
            latest_value = response['propertyValue']['value'][value_key]
            property_values.append({
                'name': prop['name'],
                'value': round(latest_value, 2)
            })

    return property_values


def lambda_handler(event, context):
    client = get_sitewise_client()
    asset = Asset(event['assetId'])
    allowed_suffixes = event['allowed_suffixes'].split(',')

    results = get_latest_property_values(client, asset, allowed_suffixes)
    property_values = {prop['name']: prop['value'] for prop in results}

    return {
        'statusCode': 200,
        'body': json.dumps(property_values)
    }