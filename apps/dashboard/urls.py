from django.urls import path
from .views import *
from . import views

# The API URLs are now determined automatically by the router.
urlpatterns = [
   path('<str:query_name>/' , DynamicQueryAPIView.as_view(), name='dashoard-reports' ),
]
