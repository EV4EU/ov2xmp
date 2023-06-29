from rest_framework import serializers
from .models import Connector


class ConnectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connector
        fields = "__all__"
