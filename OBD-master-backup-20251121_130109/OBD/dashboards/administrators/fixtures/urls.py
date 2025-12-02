from django.urls import path
from . import views


app_name = 'fixtures'
urlpatterns = [
    path('dashboard/admin/league/<slug:slug>/fixtures/view', views.player, name='player')
]