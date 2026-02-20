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
router.register(r'gst', GSTMasterViewSet, basename='gst')
router.register(r'sub-product-categories',SubProductCategoriesViewSet,basename='sub-product-categories')

urlpatterns = [
    path('',include(router.urls)),
    path('bulk-update/', ProductBulkUpdateView.as_view(), name='products-bulk-update'),
    path('products/', ProductViewSet.as_view(), name='products-list-create'),
    path('products/bulk-update/', ProductBulkUpdateView.as_view(), name='products-bulk-update-alt'),
    path('products/<str:pk>/', ProductViewSet.as_view(), name='products-detail-update-delete'),
    path('download-template/', ProductTemplateAPIView.as_view(), name='download_product_template'),
    path('export-products/', ProductExportAPIView.as_view(), name='export_products'),
    path('upload-excel/', ProductExcelUploadAPIView.as_view(), name='upload_product_excel'),
    path(
        "update-balance/<uuid:pk>/",
        UpdateProductBalanceView.as_view(),
        name="update-product-balance"
    ),
]
    