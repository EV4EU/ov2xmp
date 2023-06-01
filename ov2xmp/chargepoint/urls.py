from django.urls import path, include
from .views import ChargepointApiView, ChargepointDetailApiView


urlpatterns = [
    #path('', ChargepointApiView.as_view()),
    #path('<str:chargepoint_url_identity>/', ChargepointDetailApiView.as_view()),
]
