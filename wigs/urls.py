from django.urls import path
from . import views

app_name = 'wigs'

urlpatterns = [
    path('', views.index, name='index'),
    path('wig/<slug:slug>/', views.wig_detail, name='detail'),
    path('buy/<str:product_id>/', views.buy_now, name='buy_now'),
    path('order-success/<str:order_number>/', views.order_success, name='order_success'),
    
    # Key 2: Ask
    path('ask/', views.submit_inquiry, name='ask_inquiry'),
    
    # Key 3: Cart
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<str:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Refund System
    path('refund/', views.refund_request_view, name='refund_request'),
    
    # Blessed Mobile Hub
    path('Blessed-portal/', views.blessed_dashboard, name='blessed_dashboard'),
]

