from rest_framework import serializers
from statusnotification.models import Statusnotification


class StatusnotificationSerializer(serializers.ModelSerializer):
    connector = serializers.SlugRelatedField(many=False, read_only=True, slug_field="uuid")
    class Meta:
        model = Statusnotification
        fields = "__all__"
