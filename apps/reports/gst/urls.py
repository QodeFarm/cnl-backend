from django.urls import path
from apps.reports.gst.views import Gstr3bView

urlpatterns = [
    path("gstr-3b/", Gstr3bView.as_view(), name="gstr-3b"),
]
