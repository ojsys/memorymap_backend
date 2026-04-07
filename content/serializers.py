from rest_framework import serializers
from .models import SiteContent


class SiteContentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SiteContent
        fields = ['key', 'label', 'section', 'value', 'updated_at']
        read_only_fields = ['key', 'label', 'section', 'updated_at']
