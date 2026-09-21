import json

from src.common.sitewise_client import get_sitewise_client
from src.models.line_hierarchy import Hierarchy


def get_asset_properties(client, asset_id: str, property_names: list) -> list:
    response = client.describe_asset(assetId=asset_id)
    props = response["assetProperties"]

    if property_names:
        names_set = set(property_names)
        props = [p for p in props if p["name"] in names_set]

    values = []
    for prop in props:
        value_response = client.get_asset_property_value(
            assetId=asset_id,
            propertyId=prop["id"],
        )
        if "propertyValue" in value_response:
            raw = value_response["propertyValue"]["value"]
            for key in raw:
                latest = raw[key]
                values.append(
                    {
                        "propertyName": prop["name"],
                        "latestValue": (
                            latest if isinstance(latest, str) else round(latest, 2)
                        ),
                    }
                )
        else:
            values.append({"propertyName": prop["name"], "latestValue": None})

    return values


def build_node(
    client, asset_id: str, asset_name: str, property_names: list, depth: int
) -> dict:
    node = {
        "id": asset_id,
        "name": asset_name,
        "properties": get_asset_properties(client, asset_id, property_names),
        "children": [],
    }

    if depth <= 0:
        return node

    asset_details = client.describe_asset(assetId=asset_id)
    for hierarchy in asset_details["assetHierarchies"]:
        response = client.list_associated_assets(
            assetId=asset_id,
            hierarchyId=hierarchy["id"],
            traversalDirection="CHILD",
            maxResults=100,
        )
        for child_summary in response["assetSummaries"]:
            child_node = build_node(
                client,
                child_summary["id"],
                child_summary["name"],
                property_names,
                depth - 1,
            )
            node["children"].append(child_node)

    return node


def lambda_handler(event, context):
    client = get_sitewise_client()
    body = event["body"]

    # depth cap: PARENT = parent only, CHILD1 = + children, CHILD2 = + grandchildren
    depth = Hierarchy[body["hierarchy"]].value

    parent_details = client.describe_asset(assetId=body["parentAssetId"])
    parent_node = build_node(
        client,
        parent_details["assetId"],
        parent_details["assetName"],
        body["propertyNames"],
        depth,
    )

    return json.dumps({"parent": parent_node}, indent=4)
