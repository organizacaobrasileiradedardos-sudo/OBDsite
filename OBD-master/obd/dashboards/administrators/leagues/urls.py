from django.urls import path
from . import views


app_name = 'league'
urlpatterns = [
    path('dashboard/public/obd/merit/ranking/view', views.orderofmerit, name='orderofmerit'),
    path('dashboard/public/obd/national/ranking/view', views.national_ranking, name='national_ranking'),
]
