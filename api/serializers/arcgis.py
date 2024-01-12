from rest_framework import serializers

from third_party.models import ArcGISItem


class ArcGISItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArcGISItem
        fields = "__all__"
