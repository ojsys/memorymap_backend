from rest_framework import serializers
from .models import PublicSubmission


class PublicSubmissionCreateSerializer(serializers.ModelSerializer):
    """Used by the public submission form — no auth required."""
    class Meta:
        model = PublicSubmission
        fields = [
            'victim_name', 'victim_age', 'victim_gender', 'community_ward',
            'year_of_death', 'cause_of_death', 'story',
            'home_lat', 'home_lng',
            'submitter_name', 'submitter_relationship',
            'submitter_contact', 'submitter_consents',
        ]

    def validate_submitter_consents(self, value):
        if not value:
            raise serializers.ValidationError(
                'You must confirm that you have the authority to share this information.'
            )
        return value

    def validate_community_ward(self, value):
        if not value.strip():
            raise serializers.ValidationError('Community / ward is required.')
        return value.strip()

    def validate_story(self, value):
        if not value.strip():
            raise serializers.ValidationError('Please share what you know about this person.')
        return value.strip()


class PublicSubmissionAdminSerializer(serializers.ModelSerializer):
    """Full detail view for CVT / admin."""
    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = PublicSubmission
        fields = '__all__'

    def get_reviewed_by_name(self, obj):
        if obj.reviewed_by:
            return obj.reviewed_by.get_full_name() or obj.reviewed_by.username
        return None


class PublicSubmissionListSerializer(serializers.ModelSerializer):
    """Compact list for the verification queue."""
    class Meta:
        model = PublicSubmission
        fields = [
            'id', 'victim_name', 'community_ward', 'year_of_death',
            'submitter_relationship', 'submitter_consents',
            'status', 'created_at',
        ]
