from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),
    path('save_url/', views.save_url, name='save_url'),
    path('url_list/', views.url_list, name='url_list'),
    path('payment/', views.payment, name='payment'),
    path('load_balance/', views.load_balance, name='load_balance'),
    path('purchase_membership/<str:membership_type>/', views.purchase_membership, name='purchase_membership'),
    path('profile/', views.profile, name='profile'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('delete_url/<int:url_id>/', views.delete_url, name='delete_url'),
]
