from django.contrib import admin
from django.urls import path, include
from rest_framework import routers, permissions
from .views  import *

router = routers.DefaultRouter()
router.register(r'product_groups', ProductGroupsViewSet)
router.register(r'product_categories', ProductCategoriesViewSet)
router.register(r'product_stock_units', ProductStockUnitsViewSet)
router.register(r'product_gst_classifications', ProductGstClassificationsViewSet)
router.register(r'product_sales_gl', ProductSalesGlViewSet)
router.register(r'product_purchase_gl', ProductPurchaseGlViewSet)
router.register(r'products', productsViewSet)

urlpatterns = [
    path('', include(router.urls)),  
]