"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'main/dashboard.html')

def landing(request):
    return render(request, 'main/landing.html')

@login_required
def view_history(request):
    return render(request, 'main/history.html')

urlpatterns = [
    path('', landing, name='landing'),
    path('dashboard/', dashboard, name='dashboard'),
    path('history', view_history, name='history'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('social/', include('allauth.socialaccount.urls')),  # This line includes the socialaccount URLs
    path('courses/', include('courses.urls')),
    path('inbox/', include('inbox.urls')),
]
