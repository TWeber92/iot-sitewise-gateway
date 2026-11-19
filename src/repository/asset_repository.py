PAGE_SIZE = 250  # per-call page size, same as the old paginator config


class AssetRepository:
    def __init__(self, client):
        self.client = client

    def get_asset_with_children(self, asset_id: str, max_results: int = 25) -> dict:
        parent_asset = self.client.describe_asset(assetId=asset_id)

        children_data = []

        for hierarchy in parent_asset.get("assetHierarchies", []):
            response = self.client.list_associated_assets(
                assetId=asset_id,
                hierarchyId=hierarchy["id"],
                traversalDirection="CHILD",
                maxResults=max_results,
            )
            for asset_summary in response.get("assetSummaries", []):
                child_asset = self.client.describe_asset(assetId=asset_summary["id"])
                grandchildren = [
                    {"id": h["id"], "name": h["name"]}
                    for h in child_asset.get("assetHierarchies", [])
                ]
                children_data.append(
                    {
                        "child": {
                            "id": child_asset["assetId"],
                            "name": child_asset["assetName"],
                        },
                        "grandchildren": grandchildren,
                    }
                )

        return {"parent_asset": parent_asset, "children": children_data}

    def get_latest_property_values(self, asset_id: str, allowed_suffixes: list) -> list:
        asset_details = self.client.describe_asset(assetId=asset_id)
        property_values = []

        for prop in asset_details.get("assetProperties", []):
            if not any(prop["name"].endswith(suffix) for suffix in allowed_suffixes):
                continue
            response = self.client.get_asset_property_value(
                assetId=asset_id, propertyId=prop["id"]
            )
            value_obj = response["propertyValue"]["value"]
            latest_value = list(value_obj.values())[0]
            property_values.append({"name": prop["name"], "value": latest_value})
        return property_values

    def get_raw_historical_values(
        self,
        asset_id,
        property_id,
        start_date,
        end_date,
        qualities,
        time_ordering,
        max_results,
    ):
        """Follow nextToken until the data runs out or max_results is reached.

        Works the same against real boto3 and the mock client. Termination
        keys off nextToken, never off page length: a real page can be smaller
        than requested and still have more data behind it.
        """
        raw_values = []
        next_token = None

        while len(raw_values) < max_results:
            kwargs = dict(
                assetId=asset_id,
                propertyId=property_id,
                startDate=start_date,
                endDate=end_date,
                qualities=qualities,
                timeOrdering=time_ordering,
                maxResults=min(max_results - len(raw_values), PAGE_SIZE),
            )
            if next_token:
                kwargs["nextToken"] = next_token

            response = self.client.get_asset_property_value_history(**kwargs)
            raw_values.extend(response.get("assetPropertyValueHistory", []))

            next_token = response.get("nextToken")
            if not next_token:
                break

        return raw_values[:max_results]

    def get_asset_details(self, asset_id: str) -> dict:
        return self.client.describe_asset(assetId=asset_id)
