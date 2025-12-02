from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from obd.dashboards.administrators.divisions.models import Division
from obd.dashboards.administrators.fixtures.models import Fixture

@login_required()
def player(request, slug):
    matches = Fixture.objects.filter(division=Division.objects.get(slug=slug), players=request.user)
    return render(request, 'user_matches_show.html', {'matches': matches})


# Pending validation
@login_required()
def pending(request, slug):
    matches = Fixture.objects.filter(division=Division.objects.get(slug=slug), satus=1, validation=0).exclude(submited_by=request.user.username)
    return render(request, 'user_matches_show.html', {'matches': matches})

@login_required()
def all_pending(request, slug):
    matches = Fixture.objects.filter(satus=0, validation=0).exclude(submited_by=request.user.username)
    total_pending = matches.count()
    return render(request, 'user_matches_show.html', {'matches': matches, 'total_pending': total_pending})