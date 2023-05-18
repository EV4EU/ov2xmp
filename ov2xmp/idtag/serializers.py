from rest_framework import serializers
from .models import IdTag


class IdTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdTag
        fields = "__all__"
