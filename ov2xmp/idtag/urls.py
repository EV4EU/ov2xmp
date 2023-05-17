from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.manage_idTags, name="idtag-manage"),
    path('add/', views.add_idTag, name='idtag-add'),
    path('get/', views.get_idTags, name='idtag-get'),
    re_path(r'^edit/*', views.edit_idTag, name='idtag-edit'),
    #path('get/', views.get_users, name='users-get-all'),
    re_path(r'^delete/*', views.delete_idTag, name='idtag-delete'),
]
