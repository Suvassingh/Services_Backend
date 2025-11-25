from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
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

        return Response({
            "message": "Signup successful",
            "user_id": user.id,
            "email": user.email,
            "name": user.first_name
        })
        
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def login_api(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(username=email, password=password)

    if user:
        return Response({
            "message": "Login successful",
            "user_id": user.id,
            "name": user.first_name,
            "email": user.email,
        })
    else:
        return Response({"error": "Invalid credentials"}, status=400)



# New API view to get user profile
@api_view(['GET'])
def get_profile_api(request, user_id):
    try:
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

    except Exception as e:
        return Response({"error": str(e)}, status=500)
# New API view to get user ID by email
@api_view(['GET'])
def get_user_id(request):
    email = request.GET.get("email")
    try:
        user = User.objects.get(email=email)
        return Response({"user_id": user.id})
    except:
        return Response({"error": "User not found"}, status=404)
