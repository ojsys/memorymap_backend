from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .roles import ROLE_CHOICES, get_role, set_role


class StaffUserSerializer(serializers.ModelSerializer):
    role      = serializers.ChoiceField(choices=ROLE_CHOICES, write_only=True)
    full_name = serializers.SerializerMethodField()
    password  = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model  = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'full_name', 'email',
            'role', 'is_active', 'last_login', 'date_joined', 'password',
        ]
        read_only_fields = ['last_login', 'date_joined']

    def get_full_name(self, obj):
        return obj.get_full_name()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['role'] = get_role(instance)
        return data

    def validate(self, attrs):
        if self.instance is None and not attrs.get('password'):
            raise serializers.ValidationError({'password': 'A password is required for new staff.'})
        if attrs.get('password'):
            user = self.instance or User(
                username=attrs.get('username', ''),
                first_name=attrs.get('first_name', ''),
                last_name=attrs.get('last_name', ''),
                email=attrs.get('email', ''),
            )
            try:
                validate_password(attrs['password'], user)
            except Exception as e:
                raise serializers.ValidationError({'password': list(e.messages)})
        return attrs

    def create(self, validated_data):
        role     = validated_data.pop('role')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        set_role(user, role)
        return user

    def update(self, instance, validated_data):
        role     = validated_data.pop('role', None)
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        if role:
            set_role(instance, role)
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    """What a staff member may change about themselves."""
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email']


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password     = serializers.CharField()

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Your current password is incorrect.')
        return value

    def validate_new_password(self, value):
        try:
            validate_password(value, self.context['request'].user)
        except Exception as e:
            raise serializers.ValidationError(list(e.messages))
        return value
