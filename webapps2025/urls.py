

from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('webapps2025/', views.home, name="home-page"),
    path('logout/', LogoutView.as_view(next_page='/webapps2025/'), name='logout'),
    path('webapps2025/', include('register.urls')),
    path('webapps2025/', include('customer.urls')),
    path('webapps2025/', include('admins.urls')),
    path('currencyapi/', include('currencyapi.urls')),
]

