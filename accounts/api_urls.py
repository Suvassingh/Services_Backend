from django.urls import path
from .api_views import signup_api, login_api,get_profile_api,get_user_id

urlpatterns = [
    path('signup/', signup_api),
    path('login/', login_api),
    path('get-user-id/', get_user_id),
    path('profile/<int:user_id>/', get_profile_api),

    
]
