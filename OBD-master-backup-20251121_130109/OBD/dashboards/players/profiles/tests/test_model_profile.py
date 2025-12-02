"""
from django.test import TestCase
from django.utils.timezone import now
from brasilonline.dashboards.players.profiles.models import Profile
from django.contrib.auth.models import User


class ProfileModelTest(TestCase):
    def setUp(self):
        self.obj = Profile(
            user=User.objects.get(pk=1),
            pin='1234',
            nickname='TheKabra',
            birth_date=now().date(),
            bio='This is the Profiler User',
            country='Brazil',
            state='Bahia',
            darts='Unicorn 23g',
            site='www.mysite.com',
            facebook='www.myfacebook.com/id',
            twitter='www.mytwitter.com/id',
            webcamdarts='My WebCam Nick',
            nakka='My Nakka Nick',
            lidarts='My Lidarts Nick',
            dartconnect='My DartConnect ID'
        )
        self.obj.save()

    def test_profile_model_exists(self):
        self.assertTrue(Profile.objects.exists())
"""