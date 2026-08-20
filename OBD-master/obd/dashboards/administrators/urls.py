"""obd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views


app_name = 'administrators'
urlpatterns = [
    path('dashboard/admin/', views.dashboard, name='dashboard'),
    path('dashboard/admin/players/view', views.members, name='members'),
    path('dashboard/admin/logout', views.logoutAdm, name='logout'),
    path('dashboard/admin/scraping/', views.scraping_dashboard, name='scraping_dashboard'),
    path('dashboard/admin/scraping/run/', views.run_capture, name='run_capture'),
    path('dashboard/admin/scraping/prize/<int:tournament_id>/', views.update_tournament_prize, name='update_tournament_prize'),
    path('dashboard/admin/order-of-merit/', views.order_of_merit_dashboard, name='order_of_merit_dashboard'),
    path('dashboard/admin/order-of-merit/import/', views.import_order_of_merit, name='import_order_of_merit'),
    path('dashboard/admin/national-ranking/', views.national_ranking_dashboard, name='national_ranking_dashboard'),
    path('dashboard/admin/national-ranking/import/', views.import_national_ranking, name='import_national_ranking'),
    path('dashboard/admin/merge-players/', views.merge_players_dashboard, name='merge_players_dashboard'),
    path('dashboard/admin/merge-players/execute/', views.merge_players_execute, name='merge_players_execute'),
]
