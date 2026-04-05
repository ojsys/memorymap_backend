from rest_framework import serializers
from .models import OralHistory


class OralHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OralHistory
        fields = '__all__'
