from django.urls import path
from . import views
from .admin import admin_analytics_data

app_name = 'marketplace'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/contact/', views.contact_seller, name='contact_seller'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<slug:slug>/', views.category_detail, name='category_detail'),
    path('search/', views.search, name='search'),
    
    # Location-based filtering
    path('regions/', views.region_list, name='region_list'),
    path('regions/<slug:slug>/', views.region_detail, name='region_detail'),
    path('cities/<slug:slug>/', views.city_detail, name='city_detail'),
    
    # User authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    
    # Cart management
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Wishlist
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # User account
    path('profile/', views.profile, name='profile'),
    path('orders/', views.orders, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/confirm-receipt/', views.confirm_receipt, name='confirm_receipt'),
    
    # Static pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    
    # API endpoints
    path('api/cart/add/', views.api_add_to_cart, name='api_add_to_cart'),
    path('api/wishlist/toggle/', views.api_toggle_wishlist, name='api_toggle_wishlist'),
    path('api/search/', views.api_search, name='api_search'),
    path('api/cities/', views.api_cities, name='api_cities'),
    path('admin/analytics-data/', views.admin_analytics_data, name='admin_analytics_data'),
] 