from django.urls import path
from . import views


app_name = 'champions'
urlpatterns = [
    path('boa/league/all/champions', views.champions, name='boachampions'),
]
