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
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
import obd.core.views
from obd.updates.views import updateinfo
from obd.subscriptions.views import subscribe
from obd.dashboards.administrators import urls
from obd.dashboards.administrators.enviroments import urls
from obd.dashboards.administrators.leagues import urls
from obd.dashboards.players import urls
from obd.dashboards.players.profiles import urls
from obd.dashboards.administrators.fixtures import urls
from obd.dashboards.administrators.results import urls
from obd.dashboards.administrators.champions import urls


urlpatterns = [
    path('', obd.core.views.index, name='index'),
    path('brdardos/go/', obd.core.views.brdardos, name='brdardos'),
    path('', include(obd.dashboards.players.urls, namespace='players')),
    path('', include(obd.dashboards.administrators.urls, namespace='administrators')),
    path('', include(obd.dashboards.administrators.enviroments.urls, namespace='enviroments')),
    path('', include(obd.dashboards.players.profiles.urls, namespace='profiles')),
    path('', include(obd.dashboards.administrators.leagues.urls, namespace='league')),
    path('', include(obd.dashboards.administrators.fixtures.urls, namespace='fixtures')),
    path('', include(obd.dashboards.administrators.results.urls, namespace='results')),
    path('', include(obd.dashboards.administrators.champions.urls, namespace='champions')),
    path('updates/', updateinfo),
    path('subscribe/', subscribe),
    path('admin/', admin.site.urls),
    path('boa/players/', obd.core.views.public_players, name='boaplayers'),
    path('boa/leagues/', obd.core.views.public_leagues, name='boaleagues'),
    path('boa/leagues/<slug:slug>/details', obd.core.views.public_league_view, name='boaleagueview'),
    path('boa/leagues/divisions/<slug:slug>/details', obd.core.views.public_division_view, name='boadivisionview'),
    path('dashboard/public/result/<slug:slug>/match/<int:match>/view', obd.core.views.public_result, name='result'),
    # New URLs for Events, News, and Documents
    path('eventos/', obd.core.views.events_list, name='events'),
    path('noticias/', obd.core.views.news_list, name='news'),
    path('documentos/', obd.core.views.documents_list, name='documents'),
    path('favicon.ico', RedirectView.as_view(url='/static/media/logos/LOGO_OBD.png')),
]

# Serve media files in development
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
