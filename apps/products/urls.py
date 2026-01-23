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
router.register(r'products_get', productsViewSet)
router.register(r'product_item_balance', ProductItemBalanceViewSet)
router.register(r'sizes', SizeViewSet)
router.register(r'colors', ColorViewSet)
router.register(r'product_variations', ProductVariationViewSet)
router.register(r'item-master', ItemMasterViewSet)

urlpatterns = [
    path('',include(router.urls)),
    path('products/', ProductViewSet.as_view(), name='products-list-create'),
    path('products/<str:pk>/', ProductViewSet.as_view(), name='products-detail-update-delete'),
    path('download-template/', ProductTemplateAPIView.as_view(), name='download_product_template'),
    path('upload-excel/', ProductExcelUploadAPIView.as_view(), name='upload_product_excel'),
    path('barcode-scan/', BarcodeScanAPIView.as_view(), name='barcode-scan' ),
]
    