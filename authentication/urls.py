from django.urls import path
from .views import user_login,token_login,RegisterUserView,ForgotPassword


urlpatterns = [
    path('login/', user_login, name='personal_login'),
    path('token-login/',token_login,name='token_login'),
    path('register/', RegisterUserView.as_view(), name='register-user'),
    path("forget-password/",ForgotPassword.as_view(),{'action':'send_otp'},name='forget-password'),
    path('validate-otp/',ForgotPassword.as_view(),{'action':'verify_otp'},name="verify_otp"),
    path('reset-password/',ForgotPassword.as_view(),{'action':'reset_password'},name="reset-password"),
]
