from django.urls import path
from .api_views import signup_api, login_api,get_profile_api,get_user_id,profile_update_api, forgot_password_api, reset_password_api
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup/', signup_api),
    path('login/', login_api),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('get-user-id/', get_user_id),
    path('profile/<int:user_id>/', get_profile_api),
    path('profile-update/<int:user_id>/', profile_update_api, name='profile_update'),
    path('forgot-password/', forgot_password_api),
    path('reset-password/<uid>/<token>/', reset_password_api),

    
]
