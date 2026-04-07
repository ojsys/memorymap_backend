from rest_framework import serializers
from .models import Victim, ConsentStatus


class VictimListSerializer(serializers.ModelSerializer):
    display_name = serializers.ReadOnlyField()
    effective_year = serializers.ReadOnlyField()
    # Annotated in the viewset queryset
    has_oral_history = serializers.BooleanField(read_only=True, default=False)
    is_mapped = serializers.SerializerMethodField()

    class Meta:
        model = Victim
        fields = [
            'id', 'display_name', 'age_at_death', 'gender', 'community_ward',
            'effective_year', 'consent_status', 'has_oral_history', 'is_mapped',
        ]

    def get_is_mapped(self, obj):
        return any([obj.home_lat, obj.incident_lat, obj.burial_lat])


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
            for field in ['full_name', 'consent_date', 'consent_notes']:
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
