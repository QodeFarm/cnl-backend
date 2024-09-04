from django.urls import path, include
from rest_framework import routers
from .views  import *

router = routers.DefaultRouter()
router.register(r'country', CountryViewSet),
router.register(r'state', StateViewSet),
router.register(r'city', CityViewSet),
router.register(r'statuses', StatusesViewset)
router.register(r'ledger_groups', LedgerGroupsViews)
router.register(r'firm_statuses', FirmStatusesViews)
router.register(r'territory', TerritoryViews)
router.register(r'customer_categories', CustomerCategoriesViews)
router.register(r'gst_categories', GstCategoriesViews)
router.register(r'customer_payment_terms', CustomerPaymentTermsViews)
router.register(r'price_categories', PriceCategoriesViews)
router.register(r'transporters', TransportersViews)
router.register(r'product_types', ProductTypesViewSet)
router.register(r'product_unique_quantity_codes', ProductUniqueQuantityCodesViewSet)
router.register(r'unit_options', UnitOptionsViewSet)
router.register(r'product_drug_types', ProductDrugTypesViewSet)
router.register(r'product_item_type', ProductItemTypeViewSet)
router.register(r'brand_salesman', BrandSalesmanViewSet)
router.register(r'product_brands', ProductBrandsViewSet)
router.register(r'purchase_types', PurchaseTypesViewSet)
router.register(r'shipping_companies', ShippingCompaniesView)
router.register(r'shipping_modes', ShippingModesView)
router.register(r'sale_types', SaleTypesView)
router.register(r'gst_types', GstTypesView)

router.register(r'orders_salesman', OrdersSalesmanView)
router.register(r'payment_link_type', PaymentLinkTypesView)
router.register(r'order_status', OrderStatusesView)
router.register(r'order_types', OrderTypesView)

router.register(r'task_priorities', TaskPrioritiesViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('uploads/', FileUploadView.as_view(), name='file_uploads'),
    path('generate_order_no/', generate_order_number_view, name='generate_order_no'),
    path('document_generator/<str:pk>/<str:document_type>/', DocumentGeneratorView.as_view(), name='generate-sale-order-pdf'),

]