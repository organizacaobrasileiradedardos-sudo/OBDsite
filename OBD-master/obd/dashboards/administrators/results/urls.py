from django.urls import path
from . import views


app_name = 'results'
urlpatterns = [

    path('dashboard/admin/league/match/<int:match>/validate', views.validate, name='validate'),
    path('dashboard/admin/league/match/<int:match>/invalidate', views.invalidate, name='invalidate'),
    path('dashboard/admin/results/<slug:slug>/match/<int:match>/submit', views.index, name='submit'),
    path('dashboard/admin/results/<slug:slug>/ranking/show', views.ranking, name='ranking'),
    path('dashboard/admin/results/<slug:slug>/ranking/show/byadmin', views.ranking_by_admin, name='ranking_by_admin')
]