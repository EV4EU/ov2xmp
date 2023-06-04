import asyncio
import logging
from datetime import datetime
from websockets.server import serve
from django.core.management.base import BaseCommand
from asgiref.sync import sync_to_async
from websockets.typing import Subprotocol
import uuid 
from django.db import DatabaseError
from django.utils import timezone

from chargepoint.models import Chargepoint as ChargepointModel
from idtag.models import IdTag as idTagModel
from transaction.models import Transaction as TransactionModel
from connector.models import Connector as ConnectorModel
from reservation.models import Reservation as ReservationModel

from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result, call
import ocpp.v16.enums as ocpp_v16_enums

ocpp_v16_enums.AuthorizationStatus._value_

import redis
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from flask import Flask, jsonify, request
import threading


logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

CHARGEPOINTS_V16 = {}


def authorize_idTag(id_token):
    if id_token is not None: 
        try:
            idTag_object = idTagModel.objects.get(idToken=id_token)
            if not idTag_object.revoked:
                if idTag_object.expiry_date is not None:
                    if idTag_object.expiry_date.timestamp() > datetime.utcnow().timestamp():
                        return {"status": ocpp_v16_enums.AuthorizationStatus.accepted}
                    else:
                        return {"status": ocpp_v16_enums.AuthorizationStatus.expired}
                else:
                    return {"status": ocpp_v16_enums.AuthorizationStatus.accepted}
            else:
                return {"status": ocpp_v16_enums.AuthorizationStatus.blocked}
        except idTagModel.DoesNotExist:
            return {"status": ocpp_v16_enums.AuthorizationStatus.invalid}
    else:
        return {"status": None}


class ChargePoint(cp):
    ##########################################################################################################################
    ###################  HANDLE INCOMING OCPP MESSAGES #######################################################################
    ##########################################################################################################################
    @on(ocpp_v16_enums.Action.BootNotification)
    def on_boot_notification(self, **kwargs):
        
        charge_point_vendor = kwargs.get('charge_point_vendor', None)
        charge_point_model = kwargs.get('charge_point_model', None)
        charge_point_serial_number = kwargs.get('charge_point_serial_number', None)

        ChargepointModel.objects.filter(pk=self.id).update(
            chargepoint_serial_number = charge_point_serial_number,
            chargepoint_model = charge_point_model, 
            chargepoint_vendor = charge_point_vendor
        ) 

        # Sends BootNotification.conf as a response to the BootNotification.req
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=ocpp_v16_enums.RegistrationStatus.accepted,
        )
    

    @on(ocpp_v16_enums.Action.Heartbeat)
    def on_heartbeat(self):
        current_cp = ChargepointModel.objects.filter(pk=self.id).get()
        current_cp.last_heartbeat = timezone.now()
        current_cp.save()
        return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        )


    @on(ocpp_v16_enums.Action.StatusNotification)
    def on_status_notification(self, connector_id, status, **kwargs):
        current_cp = ChargepointModel.objects.filter(pk=self.id).get()
        if connector_id != 0:
            connector_to_update = ConnectorModel.objects.filter(chargepoint=current_cp, connectorid=connector_id)
            if connector_to_update.exists():
                connector_to_update.update(availability_status= status)
            else:
                ConnectorModel.objects.create(
                    uuid = uuid.uuid4(),
                    connectorid = connector_id,
                    availability_status = status,
                    chargepoint = current_cp
                )
        else:
            current_cp.availability_status = status
            current_cp.save()
        
        return call_result.StatusNotificationPayload()


    @on(ocpp_v16_enums.Action.Authorize)
    def on_authorize(self, id_tag):
        result = authorize_idTag(id_tag)
        return call_result.AuthorizePayload(id_tag_info=result["status"])

    
    @on(ocpp_v16_enums.Action.StartTransaction)
    def on_startTransaction(self, connector_id, id_tag, meter_start, timestamp):
        
        new_transaction = TransactionModel.objects.create(
            start_transaction_timestamp = timestamp,
            wh_meter_start = meter_start,
            id_tag = idTagModel.objects.get(idToken=id_tag)
        )
        new_transaction.save()

        result = authorize_idTag(id_tag)
        return call_result.StartTransactionPayload(
            transaction_id = new_transaction.transaction_id,
            id_tag_info = {
                "status": result["status"]
            }
        )


    @on(ocpp_v16_enums.Action.MeterValues)
    def on_meterValues(self, **kwargs):
        transaction_id = kwargs.get('transaction_id', None)
        meter_values = kwargs.get('meter_value', None)
        connector_id = kwargs.get('connector_id', None)

        logging.info("MeterValue received: {Transaction ID: " + str(transaction_id) + ", Connector ID: " + str(connector_id))
        logging.info(meter_values)

        return call_result.MeterValuesPayload()


    @on(ocpp_v16_enums.Action.StopTransaction)
    def on_stopTransaction(self, meter_stop, timestamp, transaction_id, reason, id_tag, transaction_data):
        
        try:
            current_transaction = TransactionModel.objects.get(transaction_id=transaction_id)

            current_transaction.stop_transaction_timestamp = timestamp
            current_transaction.wh_meter_stop = meter_stop
            current_transaction.reason_stopped = reason

            current_transaction.save()

            return call_result.StopTransactionPayload()
        
        except DatabaseError as e:
            logging.error("Connection error with Django DB. The transaction details for # " + str(transaction_id) + " have not been saved.")
            return call_result.StopTransactionPayload()


    ##########################################################################################################################
    #################### ACTIONS INITIATED BY THE CSMS #######################################################################
    ##########################################################################################################################

    async def reset(self, type):
        request = call.ResetPayload(type = type)
        response = await self.call(request)
        if response is not None:
            return {"status": response.status}
        else:
            return {"status": None}

    
    async def remote_start_transaction(self, id_tag, connector_id, charging_profile):
        request = call.RemoteStartTransactionPayload(
            connector_id=connector_id,
            id_tag=id_tag,
            charging_profile=charging_profile
        )
        response = await self.call(request)
        if response is not None:
            return {"status": response.status}
        else:
            return {"status": None}
        

    async def remote_stop_transaction(self, transaction_id):
        request = call.RemoteStopTransactionPayload(
            transaction_id=transaction_id
        )
        response = await self.call(request)
        if response is not None:
            return {"status": response.status}
        else:
            return {"status": None}
    

    async def reserve_now(self, connector_id, id_tag, expiry_date, reservation_id):

        if reservation_id is None:
            # If reservation_id is not provided, we need to find the maximum reservation_id that exists for the particular EVCS
            reservation_ids = []
            # Get all connectors of the specific EVCS
            connectors = ConnectorModel.objects.filter(chargepoint__chargepoint_id=self.id)
            for connector in connectors:
                # For each connector, get all the relevant reservations
                _reservations = ReservationModel.objects.filter(connector__uuid = connector.uuid)
                # For each reservation of the particular connector, collect the reservation_id
                for _reservation in _reservations:
                    reservation_ids.append(_reservation.reservation_id)
            # Find the maximum reservation_id and increase it by 1 (so we do not replace any existing reservation_id on the particular EVCS)
            reservation_id = max(reservation_ids) + 1
            
        request = call.ReserveNowPayload(
            connector_id=connector_id,
            id_tag=id_tag,
            expiry_date=expiry_date,
            reservation_id=reservation_id
        )

        response = await self.call(request)
        if response is not None:
            # Create the reservation instance, if status accepted
            if response.status == ocpp_v16_enums.ReservationStatus.accepted:
                connector = ConnectorModel.objects.filter(chargepoint__chargepoint_id=self.id, connectorid=connector_id)
                ReservationModel.objects.create(
                    connector=connector,
                    reservation_id=reservation_id,
                    expiry_date=expiry_date
                ).save()
            return {"status": response.status}
        else:
            return {"status": None}

    # TODO: Cancel reservation when a transaction starts
    async def cancel_reservation(self, reservation_id):
        request = call.CancelReservationPayload(
            reservation_id=reservation_id
        )
        response = await self.call(request)
        if response is not None:
            if response.status == ocpp_v16_enums.ReservationStatus.accepted:
                reservation_to_delete = ReservationModel.objects.filter(connector__chargepoint__chargepoint_id=self.id, reservation_id=reservation_id)
                reservation_to_delete.delete()
            return {"status": response.status}
        else:
            return {"status": None}
        

    async def change_availability(self, connector_id, type):
        request = call.ChangeAvailabilityPayload(
            connector_id=connector_id,
            type=type
        )
        response = await self.call(request)
        if response is not None:
            return {"status": response.status}
        else:
            return {"status": None}

    # TODO: REST API interface
    async def change_configuration(self, key, value):
        request = call.ChangeConfigurationPayload(
            key=key,
            value=value
        )
        response = await self.call(request)
        if response is not None:
            return {"status": response.status}
        else:
            return {"status": None}
    
    # TODO: REST API interface
    async def clear_cache(self):
        request = call.ClearCachePayload()
        response = await self.call(request)
        if response is not None:
            return {"status": response.status}
        else:
            return {"status": None}
    
    # TODO: REST API interface
    async def unlock_connector(self, connector_id):
        request = call.UnlockConnectorPayload(
            connector_id=connector_id
        )
        response = await self.call(request)
        if response is not None:
            return {"status": response.status}
        else:
            return {"status": None}


    async def get_configuration(self, keys):
        request = call.GetConfigurationPayload(
            key=keys
        )
        response = await self.call(request)
        if response is not None:
            return {"status": response}
        else:
            return {"status": None}


##########################################################################################################################
##################### CSMS REST API ######################################################################################
##########################################################################################################################

# hardReset and softReset
@app.route("/ocpp/reset/<resetType>/<chargepoint_id>")
async def reset(resetType, chargepoint_id):
    if chargepoint_id in CHARGEPOINTS_V16:
        result = await CHARGEPOINTS_V16[chargepoint_id].reset(resetType)
        return jsonify(result)
    else:
        return jsonify({"status": "Charge Point does not exist"})


# Remote Start Transaction  
@app.route("/ocpp/remotestarttransaction/<chargepoint_id>", methods=["POST"])
async def remote_start_transaction(chargepoint_id):
    if chargepoint_id in CHARGEPOINTS_V16:
        connector_id = request.form.get('connector_id')
        id_tag = request.form.get('id_tag')
        charging_profile = request.form.get('charging_profile', None)
        result = await CHARGEPOINTS_V16[chargepoint_id].remote_start_transaction(id_tag, connector_id, charging_profile)
        return jsonify(result)
    else:
        return jsonify({"status": "Charge Point does not exist"})


# Remote Stop Transaction  
@app.route("/ocpp/remotestoptransaction/<chargepoint_id>", methods=["POST"])
async def remote_stop_transaction(chargepoint_id):
    if chargepoint_id in CHARGEPOINTS_V16:
        transaction_id = request.form.get('transaction_id')
        result = await CHARGEPOINTS_V16[chargepoint_id].remote_stop_transaction(transaction_id)
        return jsonify(result)
    else:
        return jsonify({"status": "Charge Point does not exist"})


# Reserve Now
@app.route("/ocpp/reservenow/<chargepoint_id>", methods=["POST"])
async def reserve_now(chargepoint_id):
    if chargepoint_id in CHARGEPOINTS_V16:
        connector_id = request.json['connector_id']
        id_tag = request.json['id_tag']
        expiry_date = request.json['expiry_date']
        reservation_id = request.json['reservation_id']
        result = await CHARGEPOINTS_V16[chargepoint_id].reserve_now(connector_id, id_tag, expiry_date, reservation_id)
        return jsonify(result)
    else:
        return jsonify({"status": "Charge Point does not exist"})


# Cancel Reservation
@app.route("/ocpp/cancelreservation/<chargepoint_id>", methods=["POST"])
async def cancel_reservation(chargepoint_id):
    if chargepoint_id in CHARGEPOINTS_V16:
        reservation_id = request.form.get('reservation_id')
        result = await CHARGEPOINTS_V16[chargepoint_id].cancel_reservation(reservation_id)
        return jsonify(result)
    else:
        return jsonify({"status": "Charge Point does not exist"})


# Change Availability
@app.route("/ocpp/changeavailability/<chargepoint_id>", methods=["POST"])
async def change_availability(chargepoint_id):
    if chargepoint_id in CHARGEPOINTS_V16:
        connector_id = request.form.get('connector_id')
        type = request.form.get('type')
        result = await CHARGEPOINTS_V16[chargepoint_id].change_availability(connector_id, type)
        return jsonify(result)
    else:
        return jsonify({"status": "Charge Point does not exist"})


# Get Configuration
@app.route("/ocpp/getconfiguration/<chargepoint_id>", methods=["POST"])
async def get_configuration(chargepoint_id):
    if chargepoint_id in CHARGEPOINTS_V16:
        keys = request.form.get('keys')
        result = await CHARGEPOINTS_V16[chargepoint_id].get_configuration(keys)
        return jsonify(result)
    else:
        return jsonify({"status": "Charge Point does not exist"})


##########################################################################################################################
##########################################################################################################################
##########################################################################################################################

async def on_connect(websocket, path):
    # For every new charge point that connects, create a ChargePoint instance and start listening for messages.
    
    try:
        requested_protocols = websocket.request_headers["Sec-WebSocket-Protocol"]
    except KeyError:
        logging.error("Client hasn't requested any Subprotocol. Closing Connection")
        return await websocket.close()
    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        # In the websockets lib if no subprotocols are supported by the
        # client and the server, it proceeds without a subprotocol,
        # so we have to manually close the connection.
        logging.warning(
            "Protocols Mismatched | Expected Subprotocols: %s,"
            " but client supports  %s | Closing connection",
            websocket.available_subprotocols,
            requested_protocols,
        )
        return await websocket.close()

    charge_point_id = path.strip("/")
    cp = ChargePoint(charge_point_id, websocket)
    
    CHARGEPOINTS_V16.update({charge_point_id: cp})

    new_chargepoint = await sync_to_async(ChargepointModel.objects.filter, thread_sensitive=True)(pk=charge_point_id)

    if not (await sync_to_async(new_chargepoint.exists, thread_sensitive=True)()):
        await ChargepointModel.objects.acreate(chargepoint_id = charge_point_id, ocpp_version="1.6-J")

    await cp.start()


async def main():

    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5688, debug=True, use_reloader=False)).start()

    async with serve(on_connect, "0.0.0.0", 9016, subprotocols=[Subprotocol("ocpp1.6")]):
        logging.info("Server Started listening to new connections...")
        await asyncio.Future()


class Command(BaseCommand):
    # asyncio.run() is used when running this example with Python >= 3.7v
    def handle(self, *args, **kwargs):
        asyncio.run(main())