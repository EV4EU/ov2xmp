from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from chargepoint.views import ChargepointApiView, ChargepointDetailApiView
from connector.views import ConnectorApiView, ConnectorDetailApiView
from chargingprofile.views import ChargingprofileApiView, ChargingprofileDetailApiView
from idtag.views import IdtagApiView, IdtagDetailApiView
from .views import *
from tasks.views import TasksApiView, TasksDetailApiView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [


    #path('', TemplateView.as_view(
    #    template_name='swagger-ui.html',
    #    extra_context={'schema_url':'openapi-schema'}
    #), name='swagger-ui'),
    
    #path('schema/', get_schema_view(
    #    title="O-V2X-MP REST API",
    #    description="The description of the REST API provided by the O-V2X-MP.",
    #    version="1.0.0"
    #), name='openapi-schema'),

    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('redoc/', SpectacularRedocView.as_view(), name='redoc'),

    path('chargepoint/', ChargepointApiView.as_view()),
    path('chargepoint/<str:chargepoint_id>/', ChargepointDetailApiView.as_view()),

    path('connector/', ConnectorApiView.as_view()),
    path('connector/<str:chargepoint_id>/', ConnectorDetailApiView.as_view()),

    path('chargingprofile/', ChargingprofileApiView.as_view()),
    path('chargingprofile/<str:chargingprofile_id>/', ChargingprofileDetailApiView.as_view()),

    path('idtag/', IdtagApiView.as_view()),
    path('idtag/<str:id_token>/', IdtagDetailApiView.as_view()),

    path('task/', TasksApiView.as_view()),
    path('task/<str:task_id>/', TasksDetailApiView.as_view()),

    path('ocpp16/reset/', OcppResetApiView.as_view()),
    path('ocpp16/remotestarttransaction', OcppRemoteStartTrasactionApiView.as_view()),
    path('ocpp16/remotestoptransaction', OcppRemoteStopTrasactionApiView.as_view()),
    path('ocpp16/reservenow', OcppReserveNowApiView.as_view()),
    path('ocpp16/cancelreservation', OcppCancelReservationApiView.as_view()),
    path('ocpp16/changeavailaility', OcppChangeAvailabilityApiView.as_view()),
    path('ocpp16/changeconfiguration', OcppChangeConfigurationApiView.as_view()),
    path('ocpp16/clearcache', OcppClearCacheApiView.as_view()),
    path('ocpp16/unlockconnector', OcppUnlockConnectorApiView.as_view()),
    path('ocpp16/getconfiguration', OcppGetConfigurationApiView.as_view()),
    path('ocpp16/getcompositeschedule', OcppGetCompositeScheduleApiView.as_view()),
    path('ocpp16/clearchargingprofile', OcppClearChargingProfileApiView.as_view()),
    path('ocpp16/setchargingprofile', OcppSetChargingProfileApiView.as_view())
]