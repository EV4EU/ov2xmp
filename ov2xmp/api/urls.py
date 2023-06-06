from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView
from chargepoint.views import ChargepointApiView, ChargepointDetailApiView
from idtag.views import IdtagApiView, IdtagDetailApiView
from .views import *
from tasks.views import TasksApiView, TasksDetailApiView

from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView


urlpatterns = [

    path('', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url':'openapi-schema'}
    ), name='swagger-ui'),
    
    path('schema/', get_schema_view(
        title="O-V2X-MP REST API",
        description="The description of the REST API provided by the O-V2X-MP. Under the OCPP category, the user can send OCPP commands to the underlying charge points",
        version="1.0.0"
    ), name='openapi-schema'),

    path('chargepoint/', ChargepointApiView.as_view()),
    path('chargepoint/<str:chargepoint_id>/', ChargepointDetailApiView.as_view()),

    path('idtag/', IdtagApiView.as_view()),
    path('idtag/<str:id_token>/', IdtagDetailApiView.as_view()),

    path('task/', TasksApiView.as_view()),
    path('task/<str:task_id>/', TasksDetailApiView.as_view()),

    path('ocpp/reset/', OcppResetApiView.as_view()),
    path('ocpp/remotestarttransaction', OcppRemoteStartTrasactionApiView.as_view()),
    path('ocpp/reservenow', OcppReserveNowApiView.as_view()),
    path('ocpp/cancelreservation', OcppCancelReservationApiView.as_view()),
    path('ocpp/changeavailaility', OcppChangeAvailabilityApiView.as_view()),
    path('ocpp/changeconfiguration', OcppChangeConfigurationApiView.as_view()),
    path('ocpp/clearcache', OcppClearCacheApiView.as_view()),
    path('ocpp/unlockconnector', OcppUnlockConnectorApiView.as_view()),
    path('ocpp/getconfiguration', OcppGetConfigurationApiView.as_view())

]