from src.common.logger import Logger

# Deliberately small so the repository's loop must follow nextToken.
# The real service returns much larger pages (up to 20,000 items).
MOCK_PAGE_SIZE = 3


class MockSiteWiseClient:
    def __init__(self, oort_client):
        self.oort = oort_client
        self._cache = {}

    def put_asset(self, asset_id, data):
        self.oort.put_json(f"sitewise/assets/{asset_id}.json", data)
        self._cache.pop(asset_id, None)

    def _load_asset(self, asset_id):
        # Helper to load the asset file from OORT (cached per client instance)
        if asset_id in self._cache:
            return self._cache[asset_id]
        try:
            data = self.oort.get_json(f"sitewise/assets/{asset_id}.json")
        except Exception:
            Logger.emit(
                "error",
                {"source": "MockSiteWise", "message": f"Asset {asset_id} not found"},
            )
            raise
        self._cache[asset_id] = data
        return data

    @staticmethod
    def _to_epoch(d):
        """Accept datetime objects or epoch seconds, like boto3 does."""
        if d is None:
            return None
        return int(d.timestamp()) if hasattr(d, "timestamp") else int(d)

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
        prop_name = propertyId.replace("-id", "")
        data = self._load_asset(assetId)

        latest_value = data["properties"].get(prop_name)

        if latest_value is None:
            return {"propertyValue": {"value": {"nullValue": {}}}}
        if isinstance(latest_value, str):
            return {"propertyValue": {"value": {"stringValue": latest_value}}}
        else:
            return {"propertyValue": {"value": {"doubleValue": latest_value}}}

    def get_asset_property_value_history(
        self,
        assetId,
        propertyId,
        startDate=None,
        endDate=None,
        qualities=None,
        timeOrdering="ASCENDING",
        maxResults=100,
        nextToken=None,
    ):
        prop_name = propertyId.replace("-id", "")
        data = self._load_asset(assetId)
        items = list(data.get("history", {}).get(prop_name, []))

        start = self._to_epoch(startDate)
        end = self._to_epoch(endDate)

        # Filter and sort first, then slice into pages (the real service
        # paginates last). Boundaries: startDate exclusive, endDate inclusive
        # (verify against the GetAssetPropertyValueHistory API reference).
        if start is not None:
            items = [v for v in items if v["timestamp"]["timeInSeconds"] > start]
        if end is not None:
            items = [v for v in items if v["timestamp"]["timeInSeconds"] <= end]
        if qualities:
            items = [v for v in items if v.get("quality", "GOOD") in qualities]
        items.sort(
            key=lambda v: v["timestamp"]["timeInSeconds"],
            reverse=(timeOrdering == "DESCENDING"),
        )

        # nextToken is opaque to callers; here it is just a string offset.
        offset = int(nextToken) if nextToken else 0
        size = min(maxResults, MOCK_PAGE_SIZE)
        page = items[offset : offset + size]

        response = {"assetPropertyValueHistory": page}
        if offset + size < len(items):
            response["nextToken"] = str(offset + size)
        return response

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
