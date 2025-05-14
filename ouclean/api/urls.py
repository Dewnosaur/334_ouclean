from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import CustomAuthToken

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(r'orders', views.OrderViewSet, basename='order')
urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('user/', views.UserDetailView.as_view(), name='user-detail'),
    path('login/', CustomAuthToken.as_view(), name='api-login'),
    
    # Custom endpoints
    path('products/<int:product_id>/details/', views.get_product_details, name='product-details'),
    path('my-orders/', views.get_user_orders, name='my-orders'),
]