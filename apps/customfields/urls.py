from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FieldTypeViewSet, CustomFieldViewSet, CustomFieldOptionViewSet, CustomFieldValueViewSet, EntitiesViewSet

router = DefaultRouter()
router.register(r'fieldtypes', FieldTypeViewSet)
router.register(r'customfields', CustomFieldViewSet)
router.register(r'entities', EntitiesViewSet)
router.register(r'customfieldoptions', CustomFieldOptionViewSet)
router.register(r'customfieldvalues', CustomFieldValueViewSet)
# router.register(r'customfieldmappings', CustomFieldEntityMappingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
