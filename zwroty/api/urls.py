from django.urls import path, include
from .views import (
    WZApiView,
    WZGenerateView,
    WZDownloadView,
    WZConfirmView,
)

urlpatterns = [
    path("wz-order-list/", WZApiView.as_view(), name="wz_order_lis"),
    path("wz/generate/", WZGenerateView.as_view(), name="wz_generate"),
    path("wz/download/<str:batch_id>/<str:token>/", WZDownloadView.as_view(), name="wz_download"),
    path("wz/confirm/<str:batch_id>/", WZConfirmView.as_view(), name="wz_confirm"),
]
