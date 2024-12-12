from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import DestinationImages,Gallery
from .serializer import DestModel,GallerySerializer
from rest_framework import status
from django.core.mail import send_mail
from django.http import JsonResponse
import json
from django.conf import settings



class DestinationListView(viewsets.ModelViewSet):
    queryset = DestinationImages.objects.all()
    serializer_class = DestModel

class GalleryView(APIView):
    def get(self, request):
        url = 'https://api.pexels.com/v1/search'
        headers = {
            'Authorization': settings.PEXELS_API_KEY
        }
        params = {
            'query': 'India nature locations',
            'per_page': 110 
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  
            data = response.json()
            print("data>>>?",data)
            return Response(data, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            return Response({'error': f'Error fetching images: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FindWeather(APIView):

    def generate_recommendation(self, weather_desc, temp):
        conditions = {
            "rain": lambda: "It looks like rain today! You might want to bring an umbrella. Maybe stay cozy indoors.",
            "clear": lambda: "It's clear and warm outside! Perfect for a walk in the park. Don't forget your sunscreen!" if temp > 25 else None,
            "freezing": lambda: "It's freezing outside! Dress warmly and stay safe." if temp < 0 else None,
            "cloud": lambda: "It's cloudy today. A good day for indoor activities or perhaps a light stroll.",
            "storm": lambda: "Severe storms are expected. It's best to stay indoors and avoid traveling.",
            "snow": lambda: "Snow is falling! Great for building snowmen or skiing, but be careful on the roads.",
            "fog": lambda: "Fog is present. Drive safely and keep your visibility in mind.",
            "wind": lambda: "It's windy but warm! A perfect day for kite flying or outdoor sports." if temp > 20 else "It's windy and cool. Dress in layers if you head outside.",
            "thunderstorm": lambda: "Thunderstorms are predicted. Stay indoors and avoid open fields.",
            "hail": lambda: "Hail is possible. Seek shelter if you're outdoors!",
            "hot": lambda: "It's quite hot outside. Stay hydrated and avoid direct sunlight for too long." if temp > 30 else None,
            "moderate": lambda: "The temperature is just right. A fantastic day for outdoor activities!" if 20 <= temp <= 30 else None,
    }
        for condition, message in conditions.items():
            if condition in weather_desc:
               recommendations = message()
               if recommendations:
                return recommendations

        return " ".join(recommendations)
    
    def post(self, request):
        city_name = request.data.get('city')
        if city_name:
            city_name = city_name[0].upper() + city_name[1:].lower()
            print("upper===>",city_name)
        if not city_name:
            return Response({"error": "City name is required."})
        
        api_key = 'b68b447356aa4452b2cb05b15857b435'
        url = f"http://api.openweathermap.org/data/2.5/weather?appid={api_key}&q={city_name}"

        try:
            response = requests.get(url)
            response.raise_for_status()  
            data = response.json()

            print('data===>',data)
            
            if data["cod"] != 200:
                print('error===>',data)
                return Response({"error": "City not found."})

            main = data["main"]
            weather = data["weather"][0]

            current_temperature = main["temp"] - 273.15
            pressure= main['pressure']
            print("pressure==>",pressure)
            weather_description = weather["description"]
            print("response===>",weather_description,"temp==",current_temperature)

        
            visibility = data["visibility"]
            wind_speed = data["wind"]["speed"]
            wind_direction_deg = data["wind"]["deg"]

    
            visibility_km = visibility / 1000
            wind=f"{wind_speed}<speed dir>{wind_direction_deg}dir"
            print(f"wind==={wind} visibility_km==={visibility_km},")


            recommendation = self.generate_recommendation(weather_description, current_temperature)
            reco = f"we recommented {recommendation}"
            return Response({
                     "city": city_name,
                     "temperature": f"{current_temperature:.2f}°C",
                     "pressure": pressure,
                     "description": weather_description,
                     "recommendation": reco,
                     "visibility": f"{visibility_km:.2f} km",
                     "wind": {
                         "speed": f"{wind_speed:.2f} m/s",
                         "direction": {
                             "degrees": wind_direction_deg,
                         }
                      }
                    }, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response({"error": f"Error fetching data: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class sendFeedbackClass(APIView):
    def post(self,request):
    
        try:
            data = json.loads(request.body)
            
            message = data.get('msg') 
            from_email = data.get('email')
            first_name = data.get('fname')
            second_name = data.get('sname')
            print("data",message,from_email,first_name,second_name)
            
            if not message or not from_email:
                return JsonResponse({"error": "Missing message or email."}, status=400)
            
            subject = f"Feedback from {first_name} {second_name} {from_email}"

            recipient = ['athulbalaneb@gmail.com','binilbalan.e.k@gmail.com']
            
           
            send_mail(subject, message, from_email, recipient)
            
            return JsonResponse({"success": "Feedback sent successfully!"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class SearchResult(APIView):
    def post(self,request):
        try:
            data = request.data.get('query', '')
            print('data...>>',data)
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{data}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                summary = data.get("extract", "No description available.")
                image_url = data.get("thumbnail", {}).get("source")  
                print("summary>>>",summary,"image>>",image_url)
                return JsonResponse({"message": "Query received successfully","summary":summary,"image_url":image_url}, status=200)
        except Exception as e:
            return JsonResponse({"error": f"Error fetching data: {e}"})

