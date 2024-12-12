import random,string
from django.core.cache import cache

def generate_otp(length=6):
    otp = ''.join(random.choices(string.digits, k=length)) 
    return otp





