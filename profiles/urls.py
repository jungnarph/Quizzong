from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('edit/', views.edit_profile_view, name='edit_profile'),
]
