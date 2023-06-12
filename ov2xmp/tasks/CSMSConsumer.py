from channels.generic.websocket import AsyncJsonWebsocketConsumer


class CSMSConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        # Join the csms_updates channel group
        if self.channel_layer is not None:
            await self.channel_layer.group_add('csms_updates', self.channel_name)
            await self.accept()
        else:
            return False
    
    async def disconnect(self, close_code):
        # Leave the channel group
        if self.channel_layer is not None:
            await self.channel_layer.group_discard('csms_updates', self.channel_name)
        else:
            return False

    async def websocket_send(self, event):
        await self.send_json({"message": event["text"]})
