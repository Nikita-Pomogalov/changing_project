"""
URL configuration for changing project.

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
from tempfile import template
from tkinter.font import names

from django.contrib import admin
from django.urls import path
from changingApp import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auto_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('create/', views.create_an, name='create_an'),
    path('<int:an_id>/update/', views.update_an, name='update_an'),
    path('<int:an_id>/delete/', views.delete_an, name='delete_an'),
    path('accounts/login/', auto_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', auto_views.LogoutView.as_view(next_page='main'), name='logout'),
    path('accounts/register/', views.register, name='register'),
    # path('home/', views.login_user, name='home'),
    path('', views.main_page, name='main'),
    path('all_an/', views.my_announcements, name='all_an')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)