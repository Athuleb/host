import socket
import random,string
from django.core.cache import cache
from django.http import JsonResponse

def generate_otp(length=6):
    otp = ''.join(random.choices(string.digits, k=length)) 
    return otp

def global_response(data=None, message="", responseStatus="", status_code=""):
    response = {"response": {"data": data,"message": message,},"responseStatus": responseStatus}
    return JsonResponse(response, status=status_code)
    


