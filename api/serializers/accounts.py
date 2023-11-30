from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    work_phone = serializers.SerializerMethodField()
    cell_phone = serializers.SerializerMethodField()

    def get_work_phone(self, obj):
        if phone := obj.get_work_phone():
            return str(phone)
        return None

    def get_cell_phone(self, obj):
        if phone := obj.get_cell_phone():
            return str(phone)
        return None

    class Meta:
        model = User
        fields = ("id", "email", "full_name", "initials", "work_phone", "cell_phone")
