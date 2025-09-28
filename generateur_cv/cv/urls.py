from django.urls import path
from django.contrib.auth import views as auth_views
from . import views, auth_views as custom_auth_views

urlpatterns = [
    path('', views.accueil),
    path('cv/', views.cv),
    path('cv/<pk>/', views.cv_detail),
    path('cv_list/', views.cv_list),
    
    # Authentication URLs
    path('auth/login/', custom_auth_views.login_view, name='login'),
    path('auth/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('auth/register/', custom_auth_views.register_view, name='register'),
    path('auth/profile/', custom_auth_views.profile_view, name='profile'),
    
    # 2FA URLs
    path('auth/setup-2fa/', custom_auth_views.setup_2fa_view, name='setup_2fa'),
    path('auth/verify-2fa/', custom_auth_views.two_factor_verify_view, name='two_factor_verify'),
    path('auth/disable-2fa/', custom_auth_views.disable_2fa_view, name='disable_2fa'),
]
