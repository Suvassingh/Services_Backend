from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile
from .serializers import UserProfileSerializer


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def signup_api(request):

    name = request.data.get('name')
    email = request.data.get('email')
    phone = request.data.get('phone')
    password = request.data.get('password')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    profile_image = request.data.get('profile_image')

    if User.objects.filter(username=email).exists():
        return Response({"error": "Account already exists"}, status=400)

    user = User.objects.create_user(
        username=email, email=email, password=password, first_name=name
    )

    profile = UserProfile.objects.create(
        user=user,
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        profile_image=profile_image
    )

    return Response({"message": "Signup successful"})


@api_view(['POST'])
def login_api(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(username=email, password=password)

    if not user:
        return Response({"error": "Invalid credentials"}, status=400)

    return Response({
        "message": "Login successful",
        "user_id": user.id,
        "name": user.first_name,
        "email": user.email,
    })
