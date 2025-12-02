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
from django.contrib import admin
from django.urls import include, path
import brasilonline.core.views
from brasilonline.updates.views import updateinfo
from brasilonline.subscriptions.views import subscribe
from brasilonline.dashboards.administrators import urls
from brasilonline.dashboards.administrators.enviroments import urls
from brasilonline.dashboards.administrators.leagues import urls
from brasilonline.dashboards.players import urls
from brasilonline.dashboards.players.profiles import urls
from brasilonline.dashboards.administrators.fixtures import urls
from brasilonline.dashboards.administrators.results import urls
from brasilonline.dashboards.administrators.champions import urls


urlpatterns = [
    path('', brasilonline.core.views.index, name='index'),
    path('brdardos/go/', brasilonline.core.views.brdardos, name='brdardos'),
    path('', include(brasilonline.dashboards.players.urls, namespace='players')),
    path('', include(brasilonline.dashboards.administrators.urls, namespace='administrators')),
    path('', include(brasilonline.dashboards.administrators.enviroments.urls, namespace='enviroments')),
    path('', include(brasilonline.dashboards.players.profiles.urls, namespace='profiles')),
    path('', include(brasilonline.dashboards.administrators.leagues.urls, namespace='league')),
    path('', include(brasilonline.dashboards.administrators.fixtures.urls, namespace='fixtures')),
    path('', include(brasilonline.dashboards.administrators.results.urls, namespace='results')),
    path('', include(brasilonline.dashboards.administrators.champions.urls, namespace='champions')),
    path('updates/', updateinfo),
    path('subscribe/', subscribe),
    path('admin/', admin.site.urls),
    path('boa/players/', brasilonline.core.views.public_players, name='boaplayers'),
    path('boa/leagues/', brasilonline.core.views.public_leagues, name='boaleagues'),
    path('boa/leagues/<slug:slug>/details', brasilonline.core.views.public_league_view, name='boaleagueview'),
    path('boa/leagues/divisions/<slug:slug>/details', brasilonline.core.views.public_division_view, name='boadivisionview'),
    path('dashboard/public/result/<slug:slug>/match/<int:match>/view', brasilonline.core.views.public_result, name='result'),
    # New URLs for Events, News, and Documents
    path('eventos/', brasilonline.core.views.events_list, name='events'),
    path('noticias/', brasilonline.core.views.news_list, name='news'),
    path('documentos/', brasilonline.core.views.documents_list, name='documents'),
]

# Serve media files in development
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
