
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def signup_api(request):
    try:
        name = request.data.get('name', '')
        email = request.data.get('email')
        password = request.data.get('password')
        phone = request.data.get('phone')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        profile_image = request.data.get('profile_image')

        # Validate required fields
        if not email:
            return Response({"error": "Email is required"}, status=400)
        if not password:
            return Response({"error": "Password is required"}, status=400)

        # Check if user already exists
        if User.objects.filter(username=email).exists():
            return Response({"error": "Account with this email already exists"}, status=400)

        # Create user
        user = User.objects.create_user(
            username=email, 
            email=email, 
            password=password, 
            first_name=name or '',
        )

        # Update the profile that was automatically created by the signal
        profile = user.profile
        profile.phone = phone or ''
        if latitude:
            profile.latitude = float(latitude)
        if longitude:
            profile.longitude = float(longitude)
        if profile_image:
            profile.profile_image = profile_image
        profile.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "message": "Signup successful",
            "user_id": user.id,
            "email": user.email,
            "name": user.first_name,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        })
        
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def login_api(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(username=email, password=password)

    if user:
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "message": "Login successful",
            "user_id": user.id,
            "name": user.first_name,
            "email": user.email,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        })
    else:
        return Response({"error": "Invalid credentials"}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile_api(request, user_id):
    try:
    
        if request.user.id != user_id:
            return Response({"error": "Not authorized to view this profile"}, status=403)
            
        user = User.objects.get(id=user_id)
        profile = user.profile

        return Response({
            "user_id": user.id,
            "name": user.first_name,
            "email": user.email,
            "phone": profile.phone,
            "latitude": profile.latitude,
            "longitude": profile.longitude,
            "profile_image": profile.profile_image.url if profile.profile_image else None,
        })

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# Protect this view as well
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_id(request):
    email = request.GET.get("email")
    try:
        user = User.objects.get(email=email)
        return Response({"user_id": user.id})
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    
# In your Django views.py
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def profile_update_api(request, user_id):
    try:
        # Check if the authenticated user is updating their own profile
        if request.user.id != int(user_id):
            return Response({"error": "Not authorized to update this profile"}, status=403)
            
        user = User.objects.get(id=user_id)
        profile = user.profile

        # Update user fields
        if 'name' in request.data:
            user.first_name = request.data['name']
            user.save()

        # Update profile fields
        if 'phone' in request.data:
            profile.phone = request.data['phone']
        
        # Handle location data
        if 'latitude' in request.data and request.data['latitude']:
            profile.latitude = float(request.data['latitude'])
        if 'longitude' in request.data and request.data['longitude']:
            profile.longitude = float(request.data['longitude'])
        if 'custom_location' in request.data:
            profile.custom_location = request.data['custom_location']
        
        # Handle profile image
        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']
        
        profile.save()

        return Response({
            "message": "Profile updated successfully",
            "user_id": user.id,
            "name": user.first_name,
            "email": user.email,
            "phone": profile.phone,
            "latitude": profile.latitude,
            "longitude": profile.longitude,
            "custom_location": profile.custom_location,
            "profile_image": profile.profile_image.url if profile.profile_image else None,
        })

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)