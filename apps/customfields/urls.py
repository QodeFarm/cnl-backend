from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomFieldViewSet, CustomFieldOptionViewSet, CustomFieldValueViewSet, CustomFieldCreateViewSet

router = DefaultRouter()

router.register(r'customfields', CustomFieldViewSet)
router.register(r'customfieldoptions', CustomFieldOptionViewSet)
router.register(r'customfieldvalues', CustomFieldValueViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('customfieldscreate/', CustomFieldCreateViewSet.as_view(), name='customefields-create'),
    path('customfieldscreate/<str:pk>/', CustomFieldCreateViewSet.as_view(), name='customefields-details')
]
