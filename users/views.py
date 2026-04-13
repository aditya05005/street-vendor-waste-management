# users/views.py

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from math import radians, cos, sin, asin, sqrt

from .models import User, VendorProfile, PickupLog
from .serializers import (
    RegisterSerializer, UserSerializer,
    VendorProfileSerializer, PickupLogSerializer
)


# ─── Haversine (GPS fence check) ────────────────────────────────────────────

def haversine(lat1, lng1, lat2, lng2):
    """Returns distance in meters between two GPS points."""
    R = 6371000
    lat1, lng1, lat2, lng2 = map(radians, [
        float(lat1), float(lng1), float(lat2), float(lng2)
    ])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    return R * 2 * asin(sqrt(a))


# ─── Auth ────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User created'}, 
                         status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)

    if user is None:
        return Response({'error': 'Invalid credentials'},
                         status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'role': user.role,
        'user': UserSerializer(user).data
    })


# ─── Vendor ──────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vendor_list(request):
    """Collectors call this to get the list of vendors in their ward."""
    ward = request.query_params.get('ward')
    vendors = VendorProfile.objects.all()
    if ward:
        vendors = vendors.filter(ward=ward)
    serializer = VendorProfileSerializer(vendors, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vendor_by_qr(request, qr_code):
    """Resolve a scanned QR code to a vendor."""
    try:
        vendor = VendorProfile.objects.get(qr_code=qr_code)
        return Response(VendorProfileSerializer(vendor).data)
    except VendorProfile.DoesNotExist:
        return Response({'error': 'Invalid QR code'}, 
                         status=status.HTTP_404_NOT_FOUND)


# ─── PickupLog ───────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_pickup(request):
    """Collector submits a pickup. GPS fence + 10kg check happen here."""
    serializer = PickupLogSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, 
                         status=status.HTTP_400_BAD_REQUEST)

    vendor = serializer.validated_data['vendor']
    c_lat = request.data.get('collector_lat')
    c_lng = request.data.get('collector_lng')
    verified_weight = request.data.get('verified_weight', 0)

    # GPS fence — flag if collector is >100m away from vendor
    is_flagged = False
    if c_lat and c_lng:
        distance = haversine(c_lat, c_lng, vendor.latitude, vendor.longitude)
        if distance > 100:
            is_flagged = True

    # 10kg rule — photo required
    if float(verified_weight) > 10 and not request.FILES.get('photo'):
        return Response(
            {'error': 'Photo is required for pickups above 10kg'},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer.save(
        collector=request.user,
        is_flagged=is_flagged,
        status='collected'
    )
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_pickups(request):
    """Collector sees their own pickup history."""
    logs = PickupLog.objects.filter(
        collector=request.user
    ).order_by('-timestamp')
    serializer = PickupLogSerializer(logs, many=True)
    return Response(serializer.data)
