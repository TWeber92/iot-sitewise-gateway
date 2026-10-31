from src.common.logger import Logger


class MockSiteWiseClient:
    def __init__(self, oort_client):
        self.oort = oort_client

    def put_asset(self, asset_id, data):
        self.oort.put_json(f"sitewise/assets/{asset_id}.json", data)

    def _load_asset(self, asset_id):
        # Helper to load the asset file from OORT
        try:
            return self.oort.get_json(f"sitewise/assets/{asset_id}.json")
        except Exception:
            Logger.emit(
                "error",
                {"source": "MockSiteWise", "message": f"Asset {asset_id} not found"},
            )
            raise

    def describe_asset(self, assetId):
        data = self._load_asset(assetId)
        return {
            "assetId": data["id"],
            "assetName": data["name"],
            "assetStatus": {"state": data.get("status", "ACTIVE")},
            "assetProperties": [
                {"id": f"{name}-id", "name": name} for name in data["properties"].keys()
            ],
            "assetHierarchies": data.get("hierarchies", []),
        }

    def list_associated_assets(
        self, assetId, hierarchyId, traversalDirection, maxResults
    ):
        data = self._load_asset(assetId)
        # In the mock, we just return the children defined in the parent's file
        return {"assetSummaries": data.get("children", [])}

    def get_asset_property_value(self, assetId, propertyId):
        # propertyId will be like "speed-id" from our describe_asset
        prop_name = propertyId.replace("-id", "")
        data = self._load_asset(assetId)

        # Return the latest value in AWS shape
        latest_value = data["latest"].get(prop_name, 0)

        if isinstance(latest_value, str):
            return {"propertyValue": {"value": {"stringValue": latest_value}}}
        else:
            return {"propertyValue": {"value": {"doubleValue": latest_value}}}

    def get_asset_property_value_history(
        self,
        assetId,
        propertyId,
        startDate,
        endDate,
        qualities,
        timeOrdering,
        maxResults,
    ):
        prop_name = propertyId.replace("-id", "")
        data = self._load_asset(assetId)

        # Fetch history and filter by date
        history = data.get("history", {}).get(prop_name, [])
        filtered = [
            v
            for v in history
            if startDate <= v["timestamp"]["timeInSeconds"] <= endDate
        ]

        # Return in AWS shape
        return {"assetPropertyValueHistory": filtered}

    def get_asset_property_aggregates(
        self,
        assetId,
        propertyId,
        aggregateTypes,
        resolution,
        startDate,
        endDate,
        maxResults,
    ):
        prop_name = propertyId.replace("-id", "")
        data = self._load_asset(assetId)

        # Fetch aggregates
        aggs = data.get("aggregates", {}).get(prop_name, [])

        return {"aggregatedValues": aggs}
