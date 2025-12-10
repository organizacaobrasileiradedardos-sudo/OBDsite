from django.urls import path
from . import views


app_name = 'champions'
urlpatterns = [
    path('obd/league/all/champions', views.champions, name='boachampions'),
]
