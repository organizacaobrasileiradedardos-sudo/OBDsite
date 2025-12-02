"""brasilonline URL Configuration

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


app_name = 'players'
urlpatterns = [
    path('dashboard/player/', views.dashboard, name='dashboard'),
    path('dashboard/player/login', views.loginuser, name='login'),
    path('dashboard/player/login/recovery/password', views.recoverypassword, name='recoverypassowrd'),
    path('dashboard/player/logout', views.logoutuser, name='logout'),
    path('dashboard/player/access', views.currentlogin, name='access'),
    path('dashboard/player/access/admin/audit', views.audit, name='audit'),
    path('dashboard/player/access/my/matches', views.player_audit, name='player_audit'),
    path('dashboard/player/view/my/matches', views.mygames, name='mygames'),
    path('dashboard/player/view/leagues', views.userleagues, name='leagues'),
    path('dashboard/player/league/<slug:slug>/signup', views.signupleague, name='signup'),
    path('dashboard/player/league/<slug:slug>/signoff', views.signoffleague, name='signoff')
]
