
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import UserRegistrationSerializer
from django.contrib.auth.hashers import check_password
from .models import UserModel
from django.core.cache import cache
from django.db.models import Q
from rest_framework.decorators import api_view
from django.contrib.auth import logout
from django.contrib.auth import login
from .utils import generate_otp
from django.core.mail import send_mail
from django.conf import settings 





class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            print('serializer>>>>',serializer.validated_data)
            email = serializer.validated_data.get('email')
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            # email = serializer.validated_data.get('email')
            # cache.set( "user_credentials" ,{'Email':email,"password":password},timeout=60)
            if UserModel.objects.filter(Q(email=email) | Q(username=username)).exists():
                print("User with this username or email is already registered.>>>>>")
                return Response(
                    {'error':"User with this username or email is already registered."},
                    status = status.HTTP_400_BAD_REQUEST
                )
            serializer.save()
            user = UserModel.objects.get(username=username)
            loginuser = serializer.save()
            login(request, loginuser)
            return Response(
                {"message": "User registered successfully!",'user': {'name': user.username,}},
                status=status.HTTP_201_CREATED
            )
        print("Serializer Errors:", serializer.errors)  
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
#
# @permission_classes([IsAuthenticated])
@csrf_exempt
def personal_login(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            email = body.get("email")
            password = body.get("password")
            login_user_type = body.get("user_type")
            print('email:', email, 'password:', password,"request usertype",login_user_type)
            if not email or not password:
                return JsonResponse({"error":"Email and password are required"},status=400)

            try:
                user = UserModel.objects.get(email=email)                
            except UserModel.DoesNotExist:
                print("User with this email does not exist")
                return JsonResponse({"error": "User with this email does not exist"}, status=404)
            
            if check_password(password,user.password):
                if login_user_type == user.user_type:
                    return JsonResponse(
                        {"message": "Login successful", "user": user.username, "user_type": user.user_type},
                        status=200
                    )
                else:
                    return JsonResponse({"error":"invalid user type business / personal"} ,status=404)
            else:
                return JsonResponse({"error": "Invalid email or password"}, status=401)
            

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    # If not a POST request
    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
@csrf_exempt
def send_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        username = data.get('username')
        user = UserModel.objects.filter(Q(email=email) | Q(username=username))
        if not user.exists():
            return JsonResponse({"response":"inivalied user"})
        else:
            otp = generate_otp()
            print(otp)
            # subject = 'Your OTP for Password Reset'
            # message = f'Your OTP for resetting your password is: {otp}'
            # from_email = settings.EMAIL_HOST_USER  
            # recipient_list = [email]
            try:
                # send_mail(subject, message, from_email, recipient_list)
                print(f"OTP sent to {email}")
            except Exception as e:
                print(f"Error sending email: {e}")
                return JsonResponse({"response": "error", "message": f"Error sending email {e}"})

            return JsonResponse({"response":otp})
        
@csrf_exempt
def verify_otp(request):
    if request.method == "POST":
        received_otp = json.loads(request.body)
        print("verify data",received_otp)
        return JsonResponse({"response":received_otp}) 

 

