from django.urls import path
from django.urls import path
from .views import *

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('report/<str:query_name>/', dashoardView.as_view(), name='dashoard-reports' ),
    path('tables/', DatabaseView.as_view(), name='return-tables'),  #List down the tables
    path('tables/<str:table_name>/columns/', DatabaseView.as_view(), name='return-tables-columns'),   #List down the selected table's columns 
    path('execute_query/', ExecuteQueryView.as_view(), name='execute-query'),
    path('save_query/', ReportDefinitionView.as_view(), name='save-custom-query'),

 ]
