import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ov2xmp.settings")
import django
django.setup()
from django.conf import settings
from chargepoint.models import Chargepoint as ChargepointModel
from chargingprofile.models import Chargingprofile as ChargingprofileModel
from chargepoint.models import OcppProtocols
from ocpp.v16.enums import ChargePointStatus
from chargepoint.ChargePoint16 import ChargePoint16
# from chargepoint.ChargePoint201 import ChargePoint201

import asyncio
from asgiref.sync import sync_to_async

from sanic import Sanic, Request, Websocket
from sanic.log import logger
from sanic import json
from dataclasses import dataclass, asdict
import logging
logging.basicConfig(level=logging.INFO)
app = Sanic(__name__)

app.ctx.CHARGEPOINTS_V16 = {}
app.ctx.CHARGEPOINTS_V201 = {}
app.config.FALLBACK_ERROR_FORMAT = "json"

###################################################################################################
################################## CSMS REST API ##################################################
###################################################################################################

# Reset (hard or soft)
@app.route("/ocpp16/reset/<chargepoint_id:str>", methods=["POST"])
async def reset(request: Request, chargepoint_id: str):
    if chargepoint_id in app.ctx.CHARGEPOINTS_V16 and request.json is not None:
        resetType = request.json["reset_type"]
        result = await app.ctx.CHARGEPOINTS_V16[chargepoint_id].reset(resetType)
        return json(result)
    else:
        return json({"status": "Charge Point does not exist"})


# RemoteStartTransaction  
@app.route("/ocpp16/remotestarttransaction/<chargepoint_id:str>", methods=["POST"])
async def remote_start_transaction(request: Request, chargepoint_id: str):
    if chargepoint_id in app.ctx.CHARGEPOINTS_V16 and request.json is not None:
        connector_id = request.json['connector_id']
        id_tag = request.json['id_tag']
        charging_profile = request.json['charging_profile']
        result = await app.ctx.CHARGEPOINTS_V16[chargepoint_id].remote_start_transaction(id_tag, connector_id, charging_profile)
        return json(result)
    else:
        return json({"status": "Charge Point does not exist"})


# RemoteStopTransaction  
@app.route("/ocpp16/remotestoptransaction/<chargepoint_id:str>", methods=["POST"])
async def remote_stop_transaction(request: Request, chargepoint_id: str):
    if chargepoint_id in app.ctx.CHARGEPOINTS_V16 and request.json is not None:
        transaction_id = request.json['transaction_id']
        result = await app.ctx.CHARGEPOINTS_V16[chargepoint_id].remote_stop_transaction(transaction_id)
        return json(result)
    else:
        return json({"status": "Charge Point does not exist"})


# ReserveNow
@app.route("/ocpp16/reservenow/<chargepoint_id:str>", methods=["POST"])
async def reserve_now(request: Request, chargepoint_id: str):
    if chargepoint_id in app.ctx.CHARGEPOINTS_V16 and request.json is not None:
        connector_id = request.json['connector_id']
        id_tag = request.json['id_tag']
        expiry_date = request.json['expiry_date']
        reservation_id = request.json['reservation_id']
        result = await app.ctx.CHARGEPOINTS_V16[chargepoint_id].reserve_now(connector_id, id_tag, expiry_date, reservation_id)
        return json(result)
    else:
        return json({"status": "Charge Point does not exist"})


# CancelReservation
@app.route("/ocpp16/cancelreservation/<chargepoint_id:str>", methods=["POST"])
async def cancel_reservation(request: Request, chargepoint_id: str):
    if chargepoint_id in app.ctx.CHARGEPOINTS_V16 and request.json is not None:
        reservation_id = request.json['reservation_id']
        result = await app.ctx.CHARGEPOINTS_V16[chargepoint_id].cancel_reservation(reservation_id)
        return json(result)
    else:
        return json({"status": "Charge Point does not exist"})


# ChangeAvailability
@app.route("/ocpp16/changeavailability/<chargepoint_id:str>", methods=["POST"])
async def change_availability(request: Request, chargepoint_id: str):
    if chargepoint_id in app.ctx.CHARGEPOINTS_V16 and request.json is not None:
        connector_id = request.json['connector_id']
        availability_type = request.json['type']
        result = await app.ctx.CHARGEPOINTS_V16[chargepoint_id].change_availability(connector_id, availability_type)
        return json(result)
    else:
        return json({"status": "Charge Point does not exist"})

# ChangeConfiguration
@app.route("/ocpp16/changeconfiguration/<chargepoint_id:str>", methods=["POST"])
async def change_configuration(request: Request, chargepoint_id: str):
    if chargepoint_id in app.ctx.CHARGEPOINTS_V16 and request.json is not None:
        key = request.json['key']
        value = request.json['value']
        result = await app.ctx.CHARGEPOINTS_V16[chargepoint_id].change_configuration(key, value)
        return json(result)
    else:
        return json({"status": "Charge Point does not exist"})


# ClearCache
@app.route("/ocpp16/clearcache/<chargepoint_id:str>", methods=["POST"])
async def clear_cache(request: Request, chargepoint_id: str):
    if chargepoint_id in app.ctx.CHARGEPOINTS_V16:
        result = await app.ctx.CHARGEPOINTS_V16[chargepoint_id].clear_cache()
        return json(result)
    else:
        return json({"status": "Charge Point does not exist"})


# UnlockConnector
@app.route("/ocpp16/unlockconnector/<chargepoint_id:str>", methods=["POST"])
async def unlock_connector(request: Request, chargepoint_id: str):
    if chargepoint_id in app.ctx.CHARGEPOINTS_V16 and request.json is not None:
        connector_id = request.json['connector_id']
        result = await app.ctx.CHARGEPOINTS_V16[chargepoint_id].unlock_connector(connector_id)
        return json(result)
    else:
        return json({"status": "Charge Point does not exist"})


# GetConfiguration
@app.route("/ocpp16/getconfiguration/<chargepoint_id:str>", methods=["POST"])
async def get_configuration(request: Request, chargepoint_id: str):
    if chargepoint_id in app.ctx.CHARGEPOINTS_V16 and request.json is not None:
        keys = request.json['keys']
        result = await app.ctx.CHARGEPOINTS_V16[chargepoint_id].get_configuration(keys)
        result["status"] = asdict(result["status"])
        return json(result)
    else:
        return json({"status": "Charge Point does not exist"})


# GetCompositeSchedule
@app.route("/ocpp16/getcompositeschedule/<chargepoint_id:str>", methods=["POST"])
async def get_composite_schedule(request: Request, chargepoint_id: str):
    if chargepoint_id in app.ctx.CHARGEPOINTS_V16 and request.json is not None:
        connector_id = request.json["connector_id"]
        duration = request.json["duration"]
        charging_rate_unit_type= request.json["charging_rate_unit"]
        result = await app.ctx.CHARGEPOINTS_V16[chargepoint_id].get_composite_schedule(connector_id, duration, charging_rate_unit_type)
        return json(result)
    else:
        return json({"status": "Charge Point does not exist"})


# ClearChargingProfile
@app.route("/ocpp16/clearchargingprofile/<chargepoint_id:str>", methods=["POST"])
async def clear_charging_profile(request: Request, chargepoint_id: str):
    if chargepoint_id in app.ctx.CHARGEPOINTS_V16 and request.json is not None:
        id_charging_profile=request.json["id"]
        connector_id = request.json["connector_id"]
        charging_profile_purpose_type= request.json["charging_profile_purpose"]
        stack_level= request.json["stack_level"]
        result = await app.ctx.CHARGEPOINTS_V16[chargepoint_id].clear_charging_profile(id_charging_profile, connector_id, charging_profile_purpose_type, stack_level)
        return json(result)
    else:
        return json({"status": "Charge Point does not exist"})


# SetChargingProfile
@app.route("/ocpp16/setchargingprofile/<chargepoint_id:str>", methods=["POST"])
async def set_charging_profile(request: Request, chargepoint_id: str):
    if chargepoint_id in app.ctx.CHARGEPOINTS_V16 and request.json is not None:
        connector_id = request.json["connector_id"]
        charging_profile_id = request.json["charging_profile_id"]
        try:
            chargingprofile_object = ChargingprofileModel.objects.get(pk=charging_profile_id)
            chargingprofile = {
                "chargingProfileId": chargingprofile_object.chargingprofile_id,
                "stackLevel": chargingprofile_object.stack_level,
                "chargingProfilePurpose": chargingprofile_object.chargingprofile_purpose,
                "chargingProfileKind": chargingprofile_object.chargingprofile_kind,
                "chargingSchedule": {
                    "chargingSchedulePeriod": chargingprofile_object.chargingschedule_period,
                    "chargingRateUnit": chargingprofile_object.charging_rate_unit
                }
            }

            if chargingprofile_object.transaction_id is not None:
                chargingprofile["transactionId"] = chargingprofile_object.transaction_id
            
            if chargingprofile_object.recurrency_kind is not None:
                chargingprofile["recurrencyKind"] = chargingprofile_object.recurrency_kind

            if chargingprofile_object.valid_from is not None:
                chargingprofile["validFrom"] = chargingprofile_object.valid_from.utcnow().isoformat()

            if chargingprofile_object.valid_to is not None:
                chargingprofile["validTo"] = chargingprofile_object.valid_to.utcnow().isoformat()
            
            if chargingprofile_object.duration is not None:
                chargingprofile["chargingSchedule"]["duration"] = chargingprofile_object.duration

            if chargingprofile_object.start_schedule is not None:
                chargingprofile["chargingSchedule"]["startSchedule"] = chargingprofile_object.start_schedule.utcnow().isoformat()
            
            if chargingprofile_object.min_charging_rate is not None:
                chargingprofile["chargingSchedule"]["minChargingRate"] = float(chargingprofile_object.min_charging_rate)

            result = await app.ctx.CHARGEPOINTS_V16[chargepoint_id].set_charging_profile(connector_id, chargingprofile)
            return json(result)
        except ChargingprofileModel.DoesNotExist:
            return json({"status": "Charging Profile does not exist"})
    else:
        return json({"status": "Charge Point does not exist"})


###################################################################################################
################################## Websocket Handler ##############################################
###################################################################################################

@app.websocket("/ocpp/<charge_point_id:str>", subprotocols=['ocpp1.6'])
async def on_connect(request: Request, websocket: Websocket, charge_point_id: str):
    # For every new charge point that connects, create a ChargePoint instance and start listening for messages.

    logger.info("Protocols Matched: %s", websocket.subprotocol)
    logger.info("Charge Point connected: %s, from: %s", charge_point_id, request.ip)

    cp = ChargePoint16(charge_point_id, websocket)
    app.ctx.CHARGEPOINTS_V16.update({charge_point_id: cp})

    new_chargepoint = await sync_to_async(ChargepointModel.objects.filter, thread_sensitive=True)(pk=charge_point_id)

    if not (await sync_to_async(new_chargepoint.exists, thread_sensitive=True)()):
        await ChargepointModel.objects.acreate(chargepoint_id = charge_point_id, 
                                                ocpp_version=OcppProtocols.ocpp16,
                                                chargepoint_status=ChargePointStatus.available.value,
                                                ip_address=request.ip,
                                                websocket_port=request.port)
    else:
        await new_chargepoint.aupdate(connected=True, chargepoint_status=ChargePointStatus.available.value)

    try:
        await cp.start()

    except asyncio.exceptions.CancelledError:
        logger.error("Disconnected from CP: %s", charge_point_id)
        ChargepointModel.objects.filter(pk=charge_point_id).update(connected=False, chargepoint_status=ChargePointStatus.unavailable.value)
        app.ctx.CHARGEPOINTS_V16[charge_point_id]._connection.fail_connection()  # Ungracefully close the Websocket connection so that the CP tries to reconnect
