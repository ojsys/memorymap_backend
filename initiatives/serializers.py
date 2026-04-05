from rest_framework import serializers
from .models import CommunityInitiative


class CommunityInitiativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityInitiative
        fields = '__all__'
