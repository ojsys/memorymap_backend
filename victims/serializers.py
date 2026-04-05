from rest_framework import serializers
from .models import Victim, ConsentStatus


class VictimListSerializer(serializers.ModelSerializer):
    display_name = serializers.ReadOnlyField()
    effective_year = serializers.ReadOnlyField()

    class Meta:
        model = Victim
        fields = [
            'id', 'display_name', 'gender', 'community_ward',
            'effective_year', 'consent_status',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Never expose consent metadata to public — only admins
        request = self.context.get('request')
        if not (request and request.user and request.user.is_staff):
            data.pop('consent_status', None)
        return data


class VictimDetailSerializer(serializers.ModelSerializer):
    display_name = serializers.ReadOnlyField()
    effective_year = serializers.ReadOnlyField()

    class Meta:
        model = Victim
        fields = [
            'id', 'display_name', 'full_name', 'age_at_death', 'gender',
            'community_ward', 'date_of_death', 'year_of_death', 'cause_of_death',
            'biographical_note',
            'home_lat', 'home_lng',
            'incident_lat', 'incident_lng',
            'burial_lat', 'burial_lng',
            'source', 'consent_status', 'consent_date', 'consent_notes',
            'effective_year', 'created_at', 'updated_at',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        is_staff = request and request.user and request.user.is_staff
        if not is_staff:
            # Strip admin-only fields from public view
            for field in ['full_name', 'consent_status', 'consent_date', 'consent_notes']:
                data.pop(field, None)
        return data


class VictimWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Victim
        exclude = ['added_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['added_by'] = self.context['request'].user
        return super().create(validated_data)


class VictimGeoJSONSerializer(serializers.ModelSerializer):
    display_name = serializers.ReadOnlyField()
    effective_year = serializers.ReadOnlyField()

    class Meta:
        model = Victim
        fields = [
            'id', 'display_name', 'effective_year', 'gender', 'community_ward',
            'home_lat', 'home_lng',
            'incident_lat', 'incident_lng',
            'burial_lat', 'burial_lng',
        ]
