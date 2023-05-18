from rest_framework import serializers
from .models import Chargepoint


class ChargepointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chargepoint
        fields = "__all__"
