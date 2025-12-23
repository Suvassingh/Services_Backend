
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
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

       
        if not email:
            return Response({"error": "Email is required"}, status=400)
        if not password:
            return Response({"error": "Password is required"}, status=400)

        
        if User.objects.filter(username=email).exists():
            return Response({"error": "Account with this email already exists"}, status=400)

     
        user = User.objects.create_user(
            username=email, 
            email=email, 
            password=password, 
            first_name=name or '',
        )

      
        profile = user.profile
        profile.phone = phone or ''
        if latitude:
            profile.latitude = float(latitude)
        if longitude:
            profile.longitude = float(longitude)
        if profile_image:
            profile.profile_image = profile_image
        profile.save()

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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_id(request):
    email = request.GET.get("email")
    try:
        user = User.objects.get(email=email)
        return Response({"user_id": user.id})
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def profile_update_api(request, user_id):
    try:
       
        if request.user.id != int(user_id):
            return Response({"error": "Not authorized to update this profile"}, status=403)
            
        user = User.objects.get(id=user_id)
        profile = user.profile

        if 'name' in request.data:
            user.first_name = request.data['name']
            user.save()

        if 'phone' in request.data:
            profile.phone = request.data['phone']
        
        if 'latitude' in request.data and request.data['latitude']:
            profile.latitude = float(request.data['latitude'])
        if 'longitude' in request.data and request.data['longitude']:
            profile.longitude = float(request.data['longitude'])
        if 'custom_location' in request.data:
            profile.custom_location = request.data['custom_location']
        
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
    
    
    
@api_view(['POST'])
def forgot_password_api(request):
    email = request.data.get('email')

    if not email:
        return Response({"error": "Email is required"}, status=400)

    try:
        user = User.objects.get(email=email)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)

        reset_link = f"http://127.0.0.1:8000/api/reset-password/{uid}/{token}/"


        send_mail(
            subject="Reset Your Password",
            message=f"""
Hello {user.first_name},

Click the link below to reset your password:

{reset_link}

If you didn’t request this, ignore this email.
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"message": "Password reset email sent"})

    except User.DoesNotExist:
        return Response({"error": "No account found with this email"}, status=404)





@api_view(['GET', 'POST'])
def reset_password_api(request, uid, token):
    try:
        user_id = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=user_id)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return HttpResponse("Invalid or expired link", status=400)

        if request.method == 'GET':
            return HttpResponse(f"""
                <html>
                <body style="font-family:Arial;padding:20px">
                    <h2>Reset Password</h2>
                    <form method="POST">
                        <input type="password" name="password" placeholder="New password" required /><br><br>
                        <button type="submit">Reset Password</button>
                    </form>
                </body>
                </html>
            """)

        if request.method == 'POST':
            password = request.data.get('password') or request.POST.get('password')
            user.set_password(password)
            user.save()

            return HttpResponse("""
                <h3>Password reset successful</h3>
                <p>You can now return to the app and login.</p>
            """)

    except Exception:
        return HttpResponse("Invalid reset link", status=400)
