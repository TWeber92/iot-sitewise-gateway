import os
from src.common.oort_storage_client import OORTStorageClient
from src.common.mock_sitewise_client import MockSiteWiseClient

# Import Repositories
from src.repository.admin_repository import AdminRepository
from src.repository.asset_repository import AssetRepository
from src.repository.child_repository import ChildRepository
from src.repository.hierarchy_repository import HierarchyRepository
from src.repository.property_repository import PropertyRepository

# Import Services
from src.service.admin_service import AdminService
from src.service.asset_service import AssetService
from src.service.child_service import ChildService
from src.service.hierarchy_service import HierarchyService
from src.service.property_service import PropertyService

# Import Controllers
from src.controller.admin_controller import AdminController
from src.controller.asset_controller import AssetController
from src.controller.child_controller import ChildController
from src.controller.hierarchy_controller import HierarchyController
from src.controller.property_controller import PropertyController

from src.common.logger import Logger


class Main:
    def __init__(self, env):
        Logger.setup_default_logger()
        # 1. Initialize the Client (OORT)
        oort = OORTStorageClient(
            env["OORT_ACCESS_KEY"],
            env["OORT_SECRET_KEY"],
            env["OORT_BUCKET"],
        )
        self.client = MockSiteWiseClient(oort)
        self.admin_controller = self.build_admin()
        self.asset_controller = self.build_asset()
        self.child_controller = self.build_child()
        self.hierarchy_controller = self.build_hierarchy()
        self.property_controller = self.build_property()

    def build_admin(self) -> AdminController:
        repo = AdminRepository(self.client)
        service = AdminService(repo)
        return AdminController(service)

    def build_asset(self) -> AssetController:
        repo = AssetRepository(self.client)
        service = AssetService(repo)
        return AssetController(service)

    def build_child(self) -> ChildController:
        repo = ChildRepository(self.client)
        service = ChildService(repo)
        return ChildController(service)

    def build_hierarchy(self) -> HierarchyController:
        repo = HierarchyRepository(self.client)
        service = HierarchyService(repo)
        return HierarchyController(service)

    def build_property(self) -> PropertyController:
        repo = PropertyRepository(self.client)
        service = PropertyService(repo)
        return PropertyController(service)
