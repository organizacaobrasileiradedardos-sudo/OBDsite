from django.urls import path
from . import views


app_name = 'league'
urlpatterns = [
    path('dashboard/admin/league', views.index, name='index'),
    path('dashboard/admin/league/create', views.index, name='create'),
    path('dashboard/admin/league/<slug:slug>/remove', views.deleteleague, name='remove'),
    path('dashboard/admin/league/<slug:slug>/setsubscription', views.setsubscription, name='setsubscription'),
    path('dashboard/admin/league/<slug:slug>/setformation', views.setformation, name='setformation'),
    path('dashboard/admin/league/<slug:slug>/start', views.startleague, name='start'),
    path('dashboard/admin/league/<slug:slug>/playoffs', views.setplayoffs, name='playoffs'),
    path('dashboard/admin/league/<slug:slug>/finish', views.finishleague, name='finish'),
    path('dashboard/admin/league/<slug:slug>/inactive', views.inactiveleague, name='inactive'),
    path('dashboard/admin/league/<slug:slug>/players', views.viewplayersonleague, name='players'),
    path('dashboard/public/obd/merit/ranking/view', views.orderofmerit, name='orderofmerit'),
    path('dashboard/admin/league/<slug:slug>/<str:pin>/<int:bcmDiv>', views.setdivision, name='setdivision'),
    path('dashboard/admin/match/<int:match>/walkover/<int:win>/<int:los>/application', views.walkover, name='walkover'),
    path('dashboard/admin/match/<int:match>/draw/application', views.draw, name='draw'),
    path('dashboard/admin/league/management', views.manageleagues, name='management'),
]
