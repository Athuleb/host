from django.urls import path
from .views import DestinationListView,FindWeather,SearchResult,GalleryView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('top-destinations/', DestinationListView.as_view(), name='destination-list'),
    path('weather/', FindWeather.as_view(), name='find_weather'),
    path('search/',SearchResult.as_view(),name="search-result"),
    path('gallery/', GalleryView.as_view(), name='gallery-view')
    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)