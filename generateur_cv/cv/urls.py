from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil),
    path('cv/', views.cv),
    path('cv/<pk>/', views.cv_detail),
    path('cv_list/', views.cv_list),
]
