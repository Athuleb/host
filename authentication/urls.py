from django.urls import path
from .views import personal_login,RegisterUserView,send_otp,verify_otp


urlpatterns = [
    path('login/', personal_login, name='personal_login'),
    path('register/', RegisterUserView.as_view(), name='register-user'),
    path("forget-password/",send_otp,name='forget-password'),
    path('verify-otp/',verify_otp,name="verify_otp")
]
