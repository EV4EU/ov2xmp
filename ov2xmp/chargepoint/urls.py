from django.urls import path, include
from .views import ChargepointApiView, ChargepointDetailApiView


urlpatterns = [
    #path('', ChargepointApiView.as_view()),
    #path('<str:chargepoint_id>/', ChargepointDetailApiView.as_view()),
]
