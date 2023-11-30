from rest_framework import serializers

from core.models import Territory


class TerritorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Territory
        fields = "__all__"
