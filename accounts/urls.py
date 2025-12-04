from django.urls import path
from .views import signup_api, login_api

urlpatterns = [
    path('api/accounts/signup/', signup_api, name='signup_api'),
    path('api/accounts/login/', login_api, name='login_api'),
    
]
