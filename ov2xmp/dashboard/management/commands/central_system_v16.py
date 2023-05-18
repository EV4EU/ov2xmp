import asyncio
import logging
from datetime import datetime
from websockets.server import serve
from django.core.management.base import BaseCommand
from asgiref.sync import sync_to_async
from websockets.typing import Subprotocol
import random
import uuid 
from django.db import DatabaseError

from chargepoint.models import Chargepoint as ChargepointModel
from idtag.models import IdTag as idTagModel
from transaction.models import Transaction as TransactionModel
from connector.models import Connector as ConnectorModel

from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result, call
#from ocpp.v16.enums import Action, RegistrationStatus
import ocpp.v16.enums as ocpp_v16_enums


import redis
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from flask import Flask, jsonify, request
import threading


logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

CHARGEPOINTS_V16 = {}

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
                new_connector = ConnectorModel.objects.create(
                    uuid = uuid.uuid4(),
                    connectorid = connector_id,
                    availability_status = status,
                    chargepoint = current_cp
                )
                new_connector.save()
        else:
            ChargepointModel.objects.filter(pk=self.id).update(availability_status = status)
        
        return call_result.StatusNotificationPayload()


    @on(ocpp_v16_enums.Action.Authorize)
    def on_authorize(self, id_tag):
        status_rejected = {"status": ocpp_v16_enums.AuthorizationStatus.invalid}
        status_accepted = {"status": ocpp_v16_enums.AuthorizationStatus.accepted}

        if id_tag is not None: 
            try:
                idTag_object = idTagModel.objects.get(idToken=id_tag)
                if not idTag_object.revoked:
                    return call_result.AuthorizePayload(id_tag_info=status_accepted)
            except idTagModel.DoesNotExist:
                return call_result.AuthorizePayload(id_tag_info=status_rejected)
        else:
            return call_result.AuthorizePayload(id_tag_info=status_rejected)

    
    @on(ocpp_v16_enums.Action.StartTransaction)
    def on_startTransaction(self, connector_id, id_tag, meter_start, timestamp):
        
        new_transaction = TransactionModel.objects.create(
            start_transaction_timestamp = timestamp,
            wh_meter_start = meter_start,
            id_tag = id_tag
        )
        new_transaction.save()
        return call_result.StartTransactionPayload(
            transaction_id = new_transaction.transaction_id,
            id_tag_info = {
                "status": ocpp_v16_enums.AuthorizationStatus.accepted
            }
        )


    @on(ocpp_v16_enums.Action.MeterValues)
    def on_meterValues(self, **kwargs):
        transaction_id = kwargs.get('transaction_id', None)
        meter_values = kwargs.get('meter_value', None)
        connector_id = kwargs.get('connector_id', None)

        return call_result.MeterValuesPayload()


    @on(ocpp_v16_enums.Action.StopTransaction)
    def on_stopTransaction(self, meter_stop, timestamp, transaction_id, reason, id_tag, transaction_data, **kwargs):
        
        try:
            current_transaction = TransactionModel.objects.get(transaction_id=transaction_id)

            current_transaction.stop_transaction_timestamp = timestamp
            current_transaction.wh_meter_stop = meter_stop
            if reason is not None:
                current_transaction.reason_stopped = reason

            current_transaction.save()

            return call_result.StopTransactionPayload()
        
        except DatabaseError as e:
            logging.error("Connection error with Django DB. The transaction details for # " + str(transaction_id) + " have not been saved.")
            return call_result.StopTransactionPayload()


    ##########################################################################################################################
    #################### ACTIONS INITIATED BY THE CSMS #######################################################################
    ##########################################################################################################################

    async def hard_reset(self):
        request = call.ResetPayload(
            type = ocpp_v16_enums.ResetType.hard
        )
        response = await self.call(request)
        if response is not None and response.status == ocpp_v16_enums.ResetStatus.accepted:
            return True
        else:
            return False

    async def soft_reset(self):
        request = call.ResetPayload(
            type = ocpp_v16_enums.ResetType.soft
        )
        response = await self.call(request)
        if response is not None and response.status == ocpp_v16_enums.ResetStatus.accepted:
            return True
        else:
            return False

##########################################################################################################################
##################### CSMS REST API ######################################################################################
##########################################################################################################################

# hardReset and softReset
@app.route("/ocpp/reset/<resetType>/<chargepoint_id>")
async def reset(resetType, chargepoint_id):
    if chargepoint_id in CHARGEPOINTS_V16:
        if resetType == "soft":
            success = await CHARGEPOINTS_V16[chargepoint_id].soft_reset()
            if success:
                return jsonify({"status": "success", "message": "Soft Reset succcessful"})
            else:
                return jsonify({"status": "error", "message": "Soft Reset failed"})
        elif resetType == "hard":
            success = await CHARGEPOINTS_V16[chargepoint_id].hard_reset()
            if success:
                return jsonify({"status": "success", "message": "Soft Reset succcessful"})
            else:
                return jsonify({"status": "error", "message": "Soft Reset failed"})
        else:
            return jsonify({"status": "error", "message": "Invalid Reset Type. Allowed values: hard, reset"})
    else:
        return jsonify({"status": "error", "message": "Charge Point does not exist"})



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

        new_cp = await sync_to_async(ChargepointModel.objects.create, thread_sensitive=True)(
            chargepoint_url_identity = charge_point_id,
            ocpp_version = "1.6-J"
        )

        await sync_to_async(new_cp.save, thread_sensitive=True)()

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