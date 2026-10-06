from rest_framework import serializers
from .models import OralHistory


class OralHistorySerializer(serializers.ModelSerializer):
    victim_name = serializers.CharField(source='victim.display_name', read_only=True)

    class Meta:
        model = OralHistory
        fields = '__all__'
