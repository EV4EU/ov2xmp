import asyncio
import logging
from datetime import datetime
import websockets
from django.core.management.base import BaseCommand
from asgiref.sync import sync_to_async

from chargepoint.models import Chargepoint as ChargepointModel

from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result
from ocpp.v16.enums import Action, RegistrationStatus

logging.basicConfig(level=logging.INFO)

CHARGEPOINTS_V16 = {}

class ChargePoint(cp):
    @on(Action.BootNotification)
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
            status=RegistrationStatus.accepted,
        )
    
    @on(Action.Heartbeat)
    def on_heartbeat(self):
        print("Got a Heartbeat!")
        return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        )


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
    server = await websockets.serve(on_connect, "0.0.0.0", 9016, subprotocols=["ocpp1.6"])

    logging.info("Server Started listening to new connections...")
    await server.wait_closed()


class Command(BaseCommand):
    # asyncio.run() is used when running this example with Python >= 3.7v
    def handle(self, *args, **kwargs):
        asyncio.run(main())