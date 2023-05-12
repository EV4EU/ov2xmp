from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.manage_users, name="users-manage"),
    path('add/', views.add_user, name='users-add'),
    re_path(r'^edit/*', views.edit_user, name='users-edit'),
    path('get/', views.get_users, name='users-get-all'),
    re_path(r'^delete/*', views.delete_user, name='users-delete'),
]
