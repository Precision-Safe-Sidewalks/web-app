from rest_framework import serializers

from third_party.models import ArcGISItem


class ArcGISItemSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        item_id = validated_data.pop("item_id")
        item, _ = ArcGISItem.objects.update_or_create(
            item_id=item_id, defaults=validated_data
        )
        return item

    class Meta:
        model = ArcGISItem
        fields = "__all__"
        extra_kwargs = {"item_id": {"validators": []}}
