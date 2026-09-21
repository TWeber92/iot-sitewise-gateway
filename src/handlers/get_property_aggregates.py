from datetime import datetime
import json
import boto3

from Asset import Asset

client = boto3.client('iotsitewise')

def get_property_aggregates(self, body):
    start_time_str = body['startTime']
    end_time_str = body['endTime']
    end_time = datetime.strptime(end_time_str, '%Y-%m-%d')
    start_time = datetime.strptime(start_time_str, '%Y-%m-%d')
    interval = body['interval']
    asset = client.describe_asset(assetId=self.asset_id)
    asset_properties = {prop['id']:prop['name'] for prop in asset['assetProperties']}
    asset_properties_aggregates = {}
    aggregate_types = []

    for propId in asset_properties:
        for propName in body['propertiesNeeded']:
            if propName == asset_properties[propId]:
                prop_val = client.get_asset_property_value(assetId=self.asset_id, propertyId=propId)
                if 'stringValue' in prop_val['propertyValue']['value']:
                    aggregate_types.append("COUNT") 
                else: 
                    aggregate_types = body['aggregateTypes']

                aggregates = client.get_asset_property_aggregates(
                    assetId = self.asset_id,
                    propertyId = propId,
                    aggregateTypes = aggregate_types,
                    resolution = interval,
                    startDate = int(start_time.timestamp()),
                    endDate = int(end_time.timestamp()),
                    maxResults = 10,
                )

                while 'nextToken' in aggregates:
                    asset_name = {}
                    aggregate_values = {}
                    if not aggregates['aggregatedValues']:
                        asset_properties_aggregates["assetName: "+asset_properties[propId]] = "aggregatedValues: {}"
                        break
                    for aggregate in aggregates['aggregatedValues']:
                        aggType = list(aggregate['value'].keys())[0]
                        ag_val = str(aggregate['value'][aggType])
                        aggregate_values['aggregatedValue']={aggType:ag_val}
                        name = asset_properties[propId]
                        asset_name['assetName'] = asset_properties[propId]
                        asset_properties_aggregates[str(asset_name)] = aggregate_values
                        break
                    break
                
    return asset_properties_aggregates

event = {
    "body": {
        "assetId": "2e360a4e-4cbb-4394-b04c-c70f2ac79f85",
        "startTime": "2023-03-01",
        "endTime": "2023-03-03",
        "interval": "1m",
        'aggregateTypes': ['SUM'],
        "propertiesNeeded": ["Runtime","Stoptime", "Faulttime", "Idletime", "Downtime", "Availability"]

    }
}

context = {}

def lambda_handler(event, context):
    body = event['body']
    asset = Asset(body["assetId"])

    results = get_property_aggregates(asset, body)

    response = {
        "statusCode":200,
        "body": json.dumps(results)
    }

    return results

results = lambda_handler(event, context)
print(json.dumps(results, indent=4))