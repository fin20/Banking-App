from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admins/', login_required(views.admin_view), name='admin-home'),
    path('registeradmins/', login_required(views.admin_register), name='register-admin')
]


