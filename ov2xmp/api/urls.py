from django.urls import path, re_path
from . import views

urlpatterns = [
    #path('', views.manage_users, name="users-manage"),
    path('softReset/<str:chargepoint_id>', views.soft_reset, name='ocpp-v16-softReset'),
    #re_path(r'^edit/*', views.edit_user, name='users-edit'),
    #path('get/', views.get_users, name='users-get-all'),
    #re_path(r'^delete/*', views.delete_user, name='users-delete'),
]
