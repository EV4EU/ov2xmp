from rest_framework import serializers
from .models import Heartbeat


class HeartbeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Heartbeat
        fields = "__all__"
