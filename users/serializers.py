# users/serializers.py

from rest_framework import serializers
from .models import User, VendorProfile, PickupLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'role', 'is_verified']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'phone', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            phone=validated_data['phone'],
            role=validated_data['role'],
        )
        return user


class VendorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = VendorProfile
        fields = ['id', 'user', 'shop_name', 'ward',
                  'latitude', 'longitude', 'qr_code']


class PickupLogSerializer(serializers.ModelSerializer):
    collector = UserSerializer(read_only=True)
    vendor = VendorProfileSerializer(read_only=True)
    vendor_id = serializers.PrimaryKeyRelatedField(
        queryset=VendorProfile.objects.all(), source='vendor', write_only=True
    )

    class Meta:
        model = PickupLog
        fields = [
            'id', 'collector', 'vendor', 'vendor_id',
            'declared_weight', 'verified_weight',
            'photo', 'qr_scanned',
            'collector_lat', 'collector_lng',
            'status', 'is_flagged', 'timestamp'
        ]
        read_only_fields = ['is_flagged', 'timestamp', 'collector']
