from django.urls import path
from . import views

urlpatterns = [

    path('', views.store, name = "store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('ordered/', views.ordered, name="ordered"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
]