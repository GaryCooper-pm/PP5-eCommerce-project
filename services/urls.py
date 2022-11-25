from django.urls import path
from . import views

urlpatterns = [
    path('', views.ServicesView.as_view(), name='services'),
    path('brake/', views.ServicesView.as_view(), name='brake'),
    path('suspension/', views.ServicesView.as_view(), name='suspension'),
    path('full/', views.ServicesView.as_view(), name='full'),
    path('wheel/', views.ServicesView.as_view(), name='wheel'),
    path('gear/', views.ServicesView.as_view(), name='gear'),
]
