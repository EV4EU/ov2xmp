from rest_framework import serializers
from .models import IdTag


class IdTagSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field="username")
    class Meta:
        model = IdTag
        fields = "__all__"
