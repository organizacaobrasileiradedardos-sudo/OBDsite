"""Utility helpers for champion capture.

These functions are used by the N01TournamentScraper to ensure that the necessary
User, Profile, League, Division and Champion objects exist.
"""

import datetime
from django.contrib.auth.models import User
from obd.dashboards.players.profiles.models import Profile
from obd.dashboards.administrators.leagues.models import League
from obd.dashboards.administrators.divisions.models import Division
from obd.dashboards.administrators.champions.models import Champion


def get_or_create_player(name: str, pin: str) -> User:
    """Return a User (and Profile) for the given name and PIN.

    If the user does not exist, it is created with a generated e‑mail address.
    The associated Profile is also created via the post_save signal, but we set the
    ``pin`` and ``nickname`` fields explicitly when the profile is newly created.
    """
    first, *last = name.split()
    last_name = " ".join(last) if last else ""
    user, created = User.objects.get_or_create(
        username=pin,
        defaults={
            "first_name": first,
            "last_name": last_name,
            "email": f"{pin}@example.com",
        },
    )
    if created:
        # The post_save signal creates an empty Profile; we fill the required fields.
        Profile.objects.filter(user=user).update(pin=pin, nickname=name)
    return user


def get_or_create_league(name: str, start_date: datetime.date) -> tuple[League, Division]:
    """Return a League and its principal Division.

    The function creates the League (and Division) if they do not already exist.
    Minimal required fields are provided; optional fields use sensible defaults.
    """
    slug = name.lower().replace(" ", "-")
    league, _ = League.objects.get_or_create(
        name=name,
        defaults={
            "slug": slug,
            "start_date": start_date,
            "end_date": start_date + datetime.timedelta(days=30),  # provisional
            "runoff": 1,
            "phase": 0,
            "scope": 2,  # Nacional (reasonable default)
            "status": True,
        },
    )
    # Ensure a principal division exists (name "Principal - League Name")
    # We must properly handle the unique constraints on 'name' and 'slug'
    from django.utils.text import slugify
    div_name = f"Principal - {league.name}"
    div_slug = slugify(div_name)
    
    division, _ = Division.objects.get_or_create(
        league=league,
        name=div_name,
        defaults={
            "formation": 1,
            "slug": div_slug
        },
    )
    return league, division


def register_champion(league: League, division: Division, champion_user: User, p2_user: User = None, p3_user: User = None) -> Champion:
    """Create or update a Champion record for the given league/division.

    Sets the first place (p1) and optionally second (p2) and third (p3) places.
    """
    champion, created = Champion.objects.get_or_create(
        league=league,
        division=division,
        defaults={
            "p1": champion_user,
            "p2": p2_user,
            "p3": p3_user,
        },
    )
    if not created:
        champion.p1 = champion_user
        if p2_user:
            champion.p2 = p2_user
        if p3_user:
            champion.p3 = p3_user
        champion.save()
    return champion
