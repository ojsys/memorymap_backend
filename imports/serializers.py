from rest_framework import serializers
from .models import BulkImport, BulkImportRow


class BulkImportRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulkImportRow
        fields = ['id', 'row_number', 'raw_data', 'is_valid', 'validation_errors', 'victim']


class BulkImportSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()
    rows = BulkImportRowSerializer(many=True, read_only=True)

    class Meta:
        model = BulkImport
        fields = [
            'id', 'original_filename', 'status',
            'uploaded_by', 'uploaded_by_name',
            'reviewed_by', 'reviewed_by_name',
            'reviewed_at', 'review_notes',
            'total_rows', 'valid_rows',
            'created_at', 'rows',
        ]
        read_only_fields = ['status', 'uploaded_by', 'reviewed_by', 'reviewed_at',
                            'total_rows', 'valid_rows', 'created_at']

    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.get_full_name() or obj.uploaded_by.username

    def get_reviewed_by_name(self, obj):
        if obj.reviewed_by:
            return obj.reviewed_by.get_full_name() or obj.reviewed_by.username
        return None


class BulkImportListSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = BulkImport
        fields = [
            'id', 'original_filename', 'status',
            'uploaded_by_name', 'total_rows', 'valid_rows', 'created_at',
        ]

    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.get_full_name() or obj.uploaded_by.username
