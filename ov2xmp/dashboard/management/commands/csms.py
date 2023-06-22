import asyncio
import logging
from websockets.server import serve
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError, ConnectionClosed
from django.core.management.base import BaseCommand
from asgiref.sync import sync_to_async
from websockets.typing import Subprotocol

from chargepoint.models import Chargepoint as ChargepointModel
from chargepoint.models import OcppProtocols

from flask import Flask, jsonify, request
import threading

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

CHARGEPOINTS_V16 = {}
CHARGEPOINTS_V201 = {}

from dashboard.management.commands.ChargePoint16 import ChargePoint16
# from dashboard.management.commands.ChargePoint201 import ChargePoint201

##########################################################################################################################
##################### CSMS REST API ######################################################################################
##########################################################################################################################

# Reset (hard or soft)
@app.route("/ocpp16/reset/<chargepoint_id>", methods=["POST"])
async def reset(chargepoint_id):
    if chargepoint_id in CHARGEPOINTS_V16 and request.json is not None:
        resetType = request.json["reset_type"]
        result = await CHARGEPOINTS_V16[chargepoint_id].reset(resetType)
        return jsonify(result)
    else:
        return jsonify({"status": "Charge Point does not exist"})


# RemoteStartTransaction  
@app.route("/ocpp16/remotestarttransaction/<chargepoint_id>", methods=["POST"])
async def remote_start_transaction(chargepoint_id):
    if chargepoint_id in CHARGEPOINTS_V16 and request.json is not None:
        connector_id = request.json['connector_id']
        id_tag = request.json['id_tag']
        charging_profile = request.json['charging_profile']
        result = await CHARGEPOINTS_V16[chargepoint_id].remote_start_transaction(id_tag, connector_id, charging_profile)
        return jsonify(result)
    else:
        return jsonify({"status": "Charge Point does not exist"})


# RemoteStopTransaction  
@app.route("/ocpp16/remotestoptransaction/<chargepoint_id>", methods=["POST"])
async def remote_stop_transaction(chargepoint_id):
    if chargepoint_id in CHARGEPOINTS_V16 and request.json is not None:
        transaction_id = request.json['transaction_id']
        result = await CHARGEPOINTS_V16[chargepoint_id].remote_stop_transaction(transaction_id)
        return jsonify(result)
    else:
        return jsonify({"status": "Charge Point does not exist"})


# ReserveNow
@app.route("/ocpp16/reservenow/<chargepoint_id>", methods=["POST"])
async def reserve_now(chargepoint_id):
    if chargepoint_id in CHARGEPOINTS_V16 and request.json is not None:
        connector_id = request.json['connector_id']
        id_tag = request.json['id_tag']
        expiry_date = request.json['expiry_date']
        reservation_id = request.json['reservation_id']
        result = await CHARGEPOINTS_V16[chargepoint_id].reserve_now(connector_id, id_tag, expiry_date, reservation_id)
        return jsonify(result)
    else:
        return jsonify({"status": "Charge Point does not exist"})


# CancelReservation
@app.route("/ocpp16/cancelreservation/<chargepoint_id>", methods=["POST"])
async def cancel_reservation(chargepoint_id):
    if chargepoint_id in CHARGEPOINTS_V16 and request.json is not None:
        reservation_id = request.json['reservation_id']
        result = await CHARGEPOINTS_V16[chargepoint_id].cancel_reservation(reservation_id)
        return jsonify(result)
    else:
        return jsonify({"status": "Charge Point does not exist"})


# ChangeAvailability
@app.route("/ocpp16/changeavailability/<chargepoint_id>", methods=["POST"])
async def change_availability(chargepoint_id):
    if chargepoint_id in CHARGEPOINTS_V16 and request.json is not None:
        connector_id = request.json['connector_id']
        availability_type = request.json['type']
        result = await CHARGEPOINTS_V16[chargepoint_id].change_availability(connector_id, availability_type)
        return jsonify(result)
    else:
        return jsonify({"status": "Charge Point does not exist"})

# ChangeConfiguration
@app.route("/ocpp16/changeconfiguration/<chargepoint_id>", methods=["POST"])
async def change_configuration(chargepoint_id):
    if chargepoint_id in CHARGEPOINTS_V16 and request.json is not None:
        key = request.json['key']
        value = request.json['value']
        result = await CHARGEPOINTS_V16[chargepoint_id].change_configuration(key, value)
        return jsonify(result)
    else:
        return jsonify({"status": "Charge Point does not exist"})


# ClearCache
@app.route("/ocpp16/clearcache/<chargepoint_id>", methods=["POST"])
async def clear_cache(chargepoint_id):
    if chargepoint_id in CHARGEPOINTS_V16:
        result = await CHARGEPOINTS_V16[chargepoint_id].clear_cache()
        return jsonify(result)
    else:
        return jsonify({"status": "Charge Point does not exist"})


# UnlockConnector
@app.route("/ocpp16/unlockconnector/<chargepoint_id>", methods=["POST"])
async def unlock_connector(chargepoint_id):
    if chargepoint_id in CHARGEPOINTS_V16 and request.json is not None:
        connector_id = request.json['connector_id']
        result = await CHARGEPOINTS_V16[chargepoint_id].unlock_connector(connector_id)
        return jsonify(result)
    else:
        return jsonify({"status": "Charge Point does not exist"})


# GetConfiguration
@app.route("/ocpp16/getconfiguration/<chargepoint_id>", methods=["POST"])
async def get_configuration(chargepoint_id):
    if chargepoint_id in CHARGEPOINTS_V16 and request.json is not None:
        keys = request.json['keys']
        result = await CHARGEPOINTS_V16[chargepoint_id].get_configuration(keys)
        return jsonify(result)
    else:
        return jsonify({"status": "Charge Point does not exist"})


##########################################################################################################################
##########################################################################################################################
##########################################################################################################################

async def on_connect(websocket, path):
    # For every new charge point that connects, create a ChargePoint instance and start listening for messages.
    charge_point_id = None
    try:
        try:
            requested_protocols = websocket.request_headers["Sec-WebSocket-Protocol"]
        except KeyError:
            logging.error("Client hasn't requested any Subprotocol. Closing Connection")
            return await websocket.close()
        
        if websocket.subprotocol == "ocpp1.6":
            logging.info("Protocols Matched: %s", websocket.subprotocol)

            charge_point_id = path.strip("/")
            cp = ChargePoint16(charge_point_id, websocket)
            
            CHARGEPOINTS_V16.update({charge_point_id: cp})

            new_chargepoint = await sync_to_async(ChargepointModel.objects.filter, thread_sensitive=True)(pk=charge_point_id)

            if not (await sync_to_async(new_chargepoint.exists, thread_sensitive=True)()):
                await ChargepointModel.objects.acreate(chargepoint_id = charge_point_id, 
                                                       ocpp_version=OcppProtocols.ocpp16,
                                                       ip_address=websocket.remote_address[0],
                                                       websocket_port=websocket.remote_address[1])
            else:
                await new_chargepoint.aupdate(connected=True)

            await cp.start()
            '''
            elif websocket.subprotocol == "ocpp2.0.1":
                logging.info("Protocols Matched: %s", websocket.subprotocol)
                charge_point_id = path.strip("/")

                cp = ChargePoint201(charge_point_id, websocket)
                CHARGEPOINTS_V201.update({charge_point_id: cp})

                new_chargepoint = await sync_to_async(ChargepointModel.objects.filter, thread_sensitive=True)(pk=charge_point_id)

                if not (await sync_to_async(new_chargepoint.exists, thread_sensitive=True)()):
                    await ChargepointModel.objects.acreate(chargepoint_id = charge_point_id, 
                                                        ocpp_version=OcppProtocols.ocpp201,
                                                        ip_address=websocket.remote_address[0],
                                                        websocket_port=websocket.remote_address[1])
                else:
                    await new_chargepoint.aupdate(connected=True)
            '''
        else:
            logging.warning(
                "Protocols Mismatched | Expected Subprotocols: %s,"
                " but client supports  %s | Closing connection",
                websocket.available_subprotocols,
                requested_protocols,
            )
            return await websocket.close()

    except ConnectionClosedOK or ConnectionClosedError or ConnectionClosed as e:
        if charge_point_id is not None:
            logging.error("Disconnected from CP: " + charge_point_id)
            chargepoint = await sync_to_async(ChargepointModel.objects.filter, thread_sensitive=True)(pk=charge_point_id)
            await chargepoint.aupdate(connected=False)


async def main():

    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5688, debug=True, use_reloader=False)).start()

    async with serve(on_connect, "0.0.0.0", 9016, subprotocols=[Subprotocol("ocpp1.6"), Subprotocol("ocpp2.0.1")]):
        logging.info("Server Started listening to new connections...")
        await asyncio.Future()


class Command(BaseCommand):
    # asyncio.run() is used when running this example with Python >= 3.7v
    def handle(self, *args, **kwargs):
        asyncio.run(main())