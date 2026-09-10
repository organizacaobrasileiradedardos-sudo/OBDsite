"""
obd URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import: from my_app import views
    2. Add a URL to urlpatterns: path('', views.home, name='home')
Class-based views
    1. Add an import: from other_app.views import Home
    2. Add a URL to urlpatterns: path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns: path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.templatetags.static import static
from django.urls import include, path
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from obd.core.views import (  # Imports explícitos para clareza e evitar NameError
    index, 
    public_players, 
    public_leagues,
    refresh_league_stats,
    events_list,
    news_list,
    news_detail,
    documents_list,
    obd_organization
)
from obd.subscriptions.views import subscribe

# Includes de apps (use prefixos para evitar conflitos na raiz)
from obd.dashboards.administrators import urls as admin_urls
from obd.dashboards.administrators.enviroments import urls as enviroments_urls
from obd.dashboards.administrators.leagues import urls as leagues_urls
from obd.dashboards.players import urls as players_urls
from obd.dashboards.players.profiles import urls as profiles_urls
from obd.dashboards.administrators.champions import urls as champions_urls

urlpatterns = [
    path('', index, name='index'),  # Raiz do site - agora usa import explícito
    path('dashboard/players/', include(players_urls, namespace='players')),
    path('dashboard/administrators/', include(admin_urls, namespace='administrators')),
    path('dashboard/enviroments/', include(enviroments_urls, namespace='enviroments')),
    path('dashboard/profiles/', include(profiles_urls, namespace='profiles')),
    path('dashboard/leagues/', include(leagues_urls, namespace='league')),
    path('dashboard/champions/', include(champions_urls, namespace='champions')),
    path('subscribe/', subscribe),
    path('admin/', admin.site.urls),
    path('obd/players/', public_players, name='boaplayers'),
    path('obd/leagues/', public_leagues, name='boaleagues'),
    path('obd/leagues/atualizar/', refresh_league_stats, name='refresh_league_stats'),
    # Compatibilidade: antigas URLs /boa/... redirecionam para /obd/...
    path('boa/players/', RedirectView.as_view(pattern_name='boaplayers', permanent=True)),
    path('boa/leagues/', RedirectView.as_view(pattern_name='boaleagues', permanent=True)),
    # New URLs for Events, News, and Documents
    path('eventos/', events_list, name='events'),
    path('noticias/', news_list, name='news'),
    path('noticias/<int:pk>/', news_detail, name='news_detail'),
    path('documentos/', documents_list, name='documents'),
    path('obd/', obd_organization, name='obd_organization'),
    path('favicon.ico', RedirectView.as_view(url=static("media/logos/Logo_OBD_3.jpeg"))),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
