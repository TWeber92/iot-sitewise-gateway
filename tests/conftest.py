import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_client():
    """Provide a MagicMock standing in for a boto3 IoT SiteWise client."""
    return MagicMock()
