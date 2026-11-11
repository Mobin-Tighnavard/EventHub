from django.urls import path
from .views import RegisterApiView , MeView

urlpatterns = [
    path('register/',RegisterApiView.as_view(),name='register'),
    path('me/',MeView.as_view(),name='me')
]