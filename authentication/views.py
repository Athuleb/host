
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import UserRegistrationSerializer
from django.contrib.auth.hashers import check_password
from .models import UserModel,OTP
from django.core.cache import cache
from django.db.models import Q
from rest_framework.decorators import api_view
from django.contrib.auth import logout
from django.contrib.auth import login
from .utils import generate_otp,global_response
from django.core.mail import send_mail
from django.conf import settings 
from django.views import View
from django.utils.decorators import method_decorator

from django.http import HttpResponse


class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():            
            userdata = serializer.validated_data
            print("userdata>>",userdata)
        
           
            email = userdata.get("email")
            password = userdata.get("password")
            user_type = userdata.get("user_type")
            cache.set( "user_credentials" ,{'Email':email,"password":password,'user_type':user_type},timeout=2592000)
            print("cache set",cache)

            if UserModel.objects.filter(Q(email=userdata.get('email')) | Q(username=userdata.get('username'))).exists():
                print("User with this username or email is already registered!!!!")
                return JsonResponse({'data': None,'message': "Invalid username or email .",'responseStatus': "fail"}, status=409)             
            user = UserModel(**userdata)
            user.set_password(userdata.get("password"))
            user.save()

            login(request, user)
            return JsonResponse({'data':user.username,'message' : "User registered successfully!" ,'responseStatus':"success"},status=200)
        
        print("Serializer Errors>>:", serializer.errors)  

        return JsonResponse({"data": serializer.errors, "message": "Invalid user data. Please check the form. ", "responseStatus": "fail", "status":400})


@csrf_exempt
@api_view(['POST'])
def cache_login(request):
    if request.method == "POST":
        cached_data = cache.get("user_credentials")
        if cached_data:
            email = cached_data.get("Email")
            password = cached_data.get("password")
            login_user_type = cached_data.get('user_type')
            print(f"Email: {email}, Password: {password} user type:{login_user_type}")

            try:
                user = UserModel.objects.get(email=email)
                print(f"cache  User found: {user}")
            except UserModel.DoesNotExist:
                return global_response(None, message="Invalid email or password", responseStatus="fail", status_code=404)
            if check_password(password, user.password):
                print(f"Password match for cache : {user.email},password:{password}")
                if login_user_type == user.user_type:
                    
                    return global_response(user.username, message="Login successful", responseStatus="success", status_code=200)
                else:
                    
                    return global_response(None, message="Invalid user type (business/personal)", responseStatus="fail", status_code=400)
            else:
                print(f"Password mismatch for user: {user.email}")
                return global_response(None, message="Invalid email or password", responseStatus="fail", status_code=401)
        else:
            print("No data found in cache.")
            return global_response(None,message="No cached data found",responseStatus="fail",status_code=404 )



@csrf_exempt
@api_view(['POST'])
def user_login(request):
    try:
        body = json.loads(request.body)
        email = body.get("email")
        password = body.get("password")
        login_user_type = body.get("user_type")
        print('email:', email, 'password:', password,"request usertype",login_user_type)
        if not email or not password:
            return global_response(None, message="Email and password are required", responseStatus="fail", status_code=400)
        try:
            user = UserModel.objects.get(email=email)
            print(f"User found: {user}")
        except UserModel.DoesNotExist:
            return global_response(None, message="Invalid email or password", responseStatus="fail", status_code=404)
                    
        if check_password(password, user.password):
            print(f"Password match for user: {user.email}")
            if login_user_type == user.user_type:
                return global_response(user.username, message="Login successful", responseStatus="success", status_code=200)
            else:
                return global_response(None, message="Invalid user type (business/personal)", responseStatus="fail", status_code=400)
        else:
            print(f"Password mismatch for user: {user.email}")
            return global_response(None, message="Invalid email or password", responseStatus="fail", status_code=401)
        
    except json.JSONDecodeError:
            return global_response(None, message="Invalid JSON format", responseStatus="fail", status_code=400)




@method_decorator(csrf_exempt, name='dispatch')
class ForgotPassword(View):

    def post(self, request, *args, **kwargs):
        action = self.kwargs.get('action')  
        if action == 'send_otp':
            return self.send_otp(request)
        elif action == 'verify_otp':
            return self.verify_otp(request)
        elif action == "reset_password":
            return self.reset_password(request)
        return JsonResponse({"response": "Invalid action"}, status=400)

    def send_otp(self, request):
        if request.method == 'POST':
            data = json.loads(request.body)
            email = data.get('email')
            username = data.get('username')
            user = UserModel.objects.filter(email=email, username=username).first()
            if not user:
                print('invalid user/exists')
                return JsonResponse({"message": "invalid user", "responseStatus": "fail"}, status=401)
            else:
                otp = generate_otp()
                OTP.objects.filter(email=email).delete()
                OTP.objects.create(email=email, otp=otp)
                model_otp = OTP.objects.all()
                print(f"Generated OTP: {otp}, model {model_otp}")
                
                try:
                    subject = "User Verification"
                    message = f"Your OTP for updating your password is {otp}. Please use this OTP to proceed with the update."
                    from_email = 'athultestmail0@gmail.com'
                    recipient_list =[email]
                    send_mail(subject, message, from_email, recipient_list)
                    print(f"OTP sent to {email}")
                    return JsonResponse({"data": otp, "message": f"OTP sent to {email}", "responseStatus": "success"}, status=200)
                except Exception as e:
                    print(f"Error sending email: {e}")
                    return JsonResponse({"message": "Error sending email", "responseStatus": "fail"}, status=400)

    def verify_otp(self, request):
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                received_otp = data.get('otp')
                email = data.get('email')
                print("email", email)
                stored_otp_obj = OTP.objects.filter(email=email).latest('created_at') if OTP.objects.filter(email=email).exists() else None

                print(f"Received OTP: {received_otp}, Original OTP: {stored_otp_obj.otp}, from {email}")

                if not stored_otp_obj:
                    return JsonResponse({"message": "OTP expired or not found", "responseStatus": "fail"}, status=400)
                stored_otp = stored_otp_obj.otp
                print("stored_otp>>>", stored_otp, email)
                if received_otp == stored_otp:
                    print("verified")
                    return JsonResponse({"data": email, "message": "OTP verified successfully", "responseStatus": "success"}, status=200)
                else:
                    print("failed")
                    return JsonResponse({"message": "Invalid OTP", "responseStatus": "fail"}, status=400)
            except Exception as e:
                print(e)
                return JsonResponse({"message": f"Error verifying OTP: {str(e)}", "responseStatus": "fail"}, status=500)

    def reset_password(self, request):
        if request.method == 'POST':
            try:
                data = json.loads(request.body.decode('utf-8'))
                password = data.get('password')
                email = data.get('email')
                print("password:", password, "email:", email)
                try:
                    user = UserModel.objects.get(email=email)
                    print("user found:", user.username,user.email)
                    user.set_password(password)  
                    user.save()
                    return JsonResponse(
                        {
                            "data": {'username':user.username},
                            "message": "Password updated successfully",
                            "responseStatus": "success",
                        },
                        status=200,
                    )
 
                except UserModel.DoesNotExist:
                    print("No user found with this email")
                    return JsonResponse({"message": "No user found with this email", "responseStatus": "fail"}, status=404)
            except json.JSONDecodeError:
                return JsonResponse({"message": "Invalid JSON", "responseStatus": "fail"}, status=400)
        return JsonResponse(
            {"message": "Method not allowed", "responseStatus": "fail"}, status=405
        )
