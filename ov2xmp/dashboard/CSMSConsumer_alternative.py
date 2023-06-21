from channels.generic.websocket import AsyncJsonWebsocketConsumer
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result, call, enums
#from ocpp.v16.enums import Action, RegistrationStatus
import ocpp.v16.enums as ocpp_v16_enums
from ov2xmp.dashboard.management.commands.csms import ChargePoint
from asgiref.sync import sync_to_async
from chargepoint.models import Chargepoint as ChargepointModel
from datetime import datetime
from dataclasses import asdict
from ocpp.messages import pack, unpack

CHARGEPOINTS_V16 = {}


class CSMSConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):

        if "ocpp1.6" in self.scope['subprotocols']:
            self.id = self.scope['path_remaining']
            
            new_chargepoint = await sync_to_async(ChargepointModel.objects.filter, thread_sensitive=True)(pk=self.id)

            if not (await sync_to_async(new_chargepoint.exists, thread_sensitive=True)()):
                await ChargepointModel.objects.acreate(chargepoint_id = self.id, ocpp_version="1.6-J")
            
            await self.accept()
        else:
            self.close(1002)

        # Join the csms_updates channel group
        #if self.channel_layer is not None:
        #    await self.channel_layer.group_add('csms_updates', self.channel_name)
        #    await self.accept()
        #else:
        #    return False
    
    def decode_json(self, text_data):
        return unpack(text_data)

    def encode_json(self, content):
        return pack(content)

    async def disconnect(self, close_code):
        # Leave the channel group
        print(close_code)
        if self.channel_layer is not None:
            await self.channel_layer.group_discard('csms_updates', self.channel_name)
        else:
            return False

    async def receive_json(self, content, **kwargs):
        if content.action == "BootNotification":
            payload = call_result.BootNotificationPayload(
                current_time=datetime.utcnow().isoformat(),
                interval=10,
                status=ocpp_v16_enums.RegistrationStatus.accepted,
            )
        elif content.action == "Heartbeat":
            payload = call_result.HeartbeatPayload(
                current_time=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "Z"
            )
        else:
            print("RECEIVED UNEXPECTED MESSAGE")
        
        self.send_json(content.create_call_result(asdict(payload)))

    async def websocket_send(self, event):
        await self.send_json({"message": event["text"]})
