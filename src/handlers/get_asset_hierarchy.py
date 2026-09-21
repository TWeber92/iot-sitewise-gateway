import json

from src.common.sitewise_client import get_sitewise_client
from src.models.asset import Asset
from src.models.child import Child


def get_asset_hierarchy(client, asset: Asset, line_suffixes: list) -> dict:
    parent_line = {}
    children = []

    parent_asset = client.describe_asset(assetId=asset.asset_id)
    for key in parent_asset:
        for suffix in line_suffixes:
            if key.lower().endswith(suffix):
                if key.lower().endswith("assetmodelid"):
                    continue
                parent_key = "line" + suffix.capitalize()
                parent_line[parent_key] = (
                    parent_asset[key]
                    if not parent_key.endswith("Status")
                    else parent_asset[key]["state"]
                )

    for hierarchy in parent_asset["assetHierarchies"]:
        response = client.list_associated_assets(
            assetId=asset.asset_id,
            hierarchyId=hierarchy["id"],
            traversalDirection="CHILD",
            maxResults=25,
        )
        for asset_summary in response["assetSummaries"]:
            gchild_assets = []
            child_asset = client.describe_asset(assetId=asset_summary["id"])
            child = Child(asset_summary["id"], child_asset["assetName"])
            grandchildren = []
            for h in child_asset["assetHierarchies"]:
                gchild = Child(h["id"], h["name"])
                grandchildren.append(gchild.to_dict())
            children.append({"child": child.to_dict(), "grandchildren": grandchildren})

    return {"parent": parent_line, "children": children}


def lambda_handler(event, context):
    client = get_sitewise_client()
    parent = Asset(event["assetId"])
    asset_hierarchy = get_asset_hierarchy(client, parent, event["lineSuffixes"])
    return json.dumps(asset_hierarchy, indent=4, sort_keys=True, ensure_ascii=False)
