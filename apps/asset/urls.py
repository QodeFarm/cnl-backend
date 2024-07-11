from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

#add your urls

router = DefaultRouter()
router.register(r'assets', AssetsViewSet)
router.register(r'asset_maintenance', AssetMaintenanceViewSet)

urlpatterns = [
    path('',include(router.urls))
]