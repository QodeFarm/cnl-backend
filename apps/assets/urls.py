from django.urls import path, include
from .views import AssetStatusesViewSet, AssetCategoriesViewSet, LocationsViewSet, AssetsViewSet, AssetMaintenanceViewSet
from rest_framework.routers import DefaultRouter


#add your urls
router = DefaultRouter()
router.register(r'asset_statuses', AssetStatusesViewSet)
router.register(r'asset_categories', AssetCategoriesViewSet)
router.register(r'locations', LocationsViewSet)
router.register(r'assets', AssetsViewSet)
router.register(r'asset_maintenance', AssetMaintenanceViewSet)

urlpatterns = [
    path('',include(router.urls))
]