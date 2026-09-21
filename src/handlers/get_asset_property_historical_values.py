from datetime import datetime
import json
from src.models.property_historical_values import PropertyHistoricalValues
from src.common.sitewise_client import get_sitewise_client
from src.models.asset import Asset
from src.models.query_params import QueryParams


def get_formatted_date(date_in_seconds):
    dt = datetime.fromtimestamp(date_in_seconds)
    return dt.strftime("%Y-%m-%d %I:%M:%S %p")


def get_asset_historical_values(
    client, asset: Asset, query_params: QueryParams
) -> dict:
    result = PropertyHistoricalValues.from_query_params(asset, query_params)

    paginator = client.get_paginator("get_asset_property_value_history")
    page_iterator = paginator.paginate(
        assetId=query_params.asset_id,
        propertyId=query_params.property_id,
        startDate=query_params.start_date,
        endDate=query_params.end_date,
        qualities=query_params.qualities,
        timeOrdering=query_params.time_ordering,
        PaginationConfig={"MaxItems": query_params.max_results, "PageSize": 250},
    )

    for page in page_iterator:
        for value in page["assetPropertyValueHistory"]:
            for key in value["value"].keys():
                result["values"].append(
                    {
                        "timestamp": str(value["timestamp"]),
                        "formattedTime": get_formatted_date(
                            value["timestamp"]["timeInSeconds"]
                        ),
                        "value": round(value["value"][key], 2),
                    }
                )

    return result


def lambda_handler(event, context):
    client = get_sitewise_client()
    body = event["body"]

    asset_response = client.describe_asset(assetId=body["assetId"])
    asset = Asset(asset_response["assetId"], asset_response["assetName"])

    start_date = datetime.strptime(body["startDate"], "%Y-%m-%d")
    end_date = datetime.strptime(body["endDate"], "%Y-%m-%d")

    property_names = body["propertyNames"]
    if not property_names:
        property_names = [prop["name"] for prop in asset_response["assetProperties"]]

    property_names_set = set(property_names)
    results = []

    for prop in asset_response["assetProperties"]:
        if prop["name"] not in property_names_set:
            continue

        query_params = QueryParams(
            asset_id=asset_response["assetId"],
            property_name=prop["name"],
            property_id=prop["id"],
            qualities=body["qualities"],
            time_ordering=body["timeOrdering"],
            start_date=int(start_date.timestamp()),
            end_date=int(end_date.timestamp()),
            max_results=body["maxResults"],
        )
        results.append(get_asset_historical_values(client, asset, query_params))

    return {
        "statusCode": 200,
        "body": [json.dumps(res, indent=4) for res in results],
    }
