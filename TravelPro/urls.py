"""
URL configuration for TravelPro project.

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
<<<<<<< HEAD
from django.urls import path,include
from busop import views 
from user import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('busop/',include('busop.urls')),
    path("",views.home, name="index"),
    path('user/', include('user.urls')),

    

=======
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include administrator app URLconf with namespace so templates can use 'administrator:...'
    path('admin-panel/', include(("administrator.urls", "administrator"), namespace="administrator")),
    # Authentication views (login/logout/password reset)
    path('accounts/', include('django.contrib.auth.urls')),
>>>>>>> origin/feature/admin-module
]
