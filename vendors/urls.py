from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/vendors/', views.vendors, name='vendors'),
    path('api/vendors/<str:vendor_id>/', views.vendor_data, name='vendor_data'),
    path('api/vendors/<str:vendor_id>/performance', views.vendor_performance, name='vendor_performance'),
    path('api/purchase_orders/', views.purchase_orders, name='purchase_orders'),
    path('api/purchase_orders/<str:po_id>/', views.purchase_order_data, name='purchase_order_data'),
    path('api/purchase_orders/<str:po_id>/acknowledge', views.acknowledge_purchase_order, name='acknowledge_purchase_order')
]
