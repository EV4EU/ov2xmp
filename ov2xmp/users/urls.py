from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.manage_users, name="users-manage"),
    path('create/', views.create_user, name='users-create'),
    re_path(r'^edit/*', views.edit_user, name='users-edit'),
    path('get/', views.get_users, name='users-get-all'),
    re_path(r'^delete/*', views.delete_user, name='users-delete'),
]
