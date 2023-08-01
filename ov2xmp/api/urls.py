from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from chargepoint.views import ChargepointApiView, ChargepointDetailApiView
from connector.views import ConnectorApiView, ConnectorDetailApiView
from chargingprofile.views import ChargingprofileApiView, ChargingprofileDetailApiView
from idtag.views import IdtagApiView, IdtagDetailApiView
from tasks.views import TasksApiView, TasksDetailApiView
from api.views import *
from heartbeat.views import HeartbeatApiView, HeartbeatSearchApiView
from location.views import LocationApiView, LocationDetailApiView
from reservation.views import ReservationApiView, ReservationDetailApiView
from statusnotification.views import StatusnotificationApiView, StatusnotificationSearchApiView
from transaction.views import TransactionApiView, TransactionDetailApiView, TransactionSearchApiView

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
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

    path('heartbeat/<str:heartbeat_id>/', HeartbeatApiView.as_view()),
    path('heartbeat/search/<str:chargepoint_id>/', HeartbeatSearchApiView.as_view()),

    path('location/', LocationApiView.as_view()),
    path('location/<str:location_id>/', LocationDetailApiView.as_view()),

    path('reservation/', ReservationApiView.as_view()),
    path('reservation/<str:reservation_id>/', ReservationDetailApiView.as_view()),

    path('statusnotification/<str:statusnotification_id>/', StatusnotificationApiView.as_view()),
    path('statusnotification/search/<str:chargepoint_id>/', StatusnotificationSearchApiView.as_view()),

    path('transaction/', TransactionApiView.as_view()),
    path('transaction/<str:transaction_id>/', TransactionDetailApiView.as_view()),
    path('transaction/search/<str:chargepoint_id>/', TransactionSearchApiView.as_view()),

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