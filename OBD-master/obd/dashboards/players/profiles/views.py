from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from obd.dashboards.administrators.fixtures.models import Fixture
from obd.dashboards.administrators.results.models import Result
from obd.dashboards.players.profiles.forms import ProfileForm
from obd.dashboards.players.profiles.models import Profile
from obd.dashboards.players.stats.models import Stat
import cloudinary
import cloudinary.uploader
import cloudinary.api

@login_required()
def config(request):
    if request.method == 'POST':
        return updateconfig(request)
    else:
        return showconfig(request)

def showconfig(request):
    return showprofile(request)


def updateconfig(request):
    form = ProfileForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(request, 'profile_view.html', {'form': form})

    # Update User Profile
    profile = Profile.objects.get(user=request.user)

    if form.cleaned_data['photo'] is not None:
        cloudinary_response = cloudinary.uploader.upload(form.cleaned_data['photo'],
                                                         public_id=f'boa/media/uploads/profiles/{profile.pin}',
                                                         gravity='face',
                                                         height='300',
                                                         width='300',
                                                         crop='thumb')

        profile.photo = cloudinary_response['url']

    profile.birth_date = form.cleaned_data['birthdate']
    profile.country = form.cleaned_data['country']
    profile.state = form.cleaned_data['state']
    profile.bio = form.cleaned_data['bio']
    profile.nickname = form.cleaned_data['nickname']
    profile.darts = form.cleaned_data['darts']
    profile.facebook = form.cleaned_data['facebook']
    profile.site = form.cleaned_data['site']
    profile.twitter = form.cleaned_data['social']


    profile.nakka = form.cleaned_data['nakka']
    profile.save()

    # Success feedback
    messages.success(request, 'Informações atualizadas com sucesso, ')
    return HttpResponseRedirect('/dashboard/player/profile/view')


def showprofile(request):
    return render(request, 'profile_view.html',
           {'form': ProfileForm(),
            'profile': Profile.objects.get(user=request.user)})

def publicprofile(request, pin, first, last):

    profile = Profile.objects.get(pin=pin)
    matches = Fixture.objects.filter(status=1, validation=1, players__profile=profile).order_by('-on_date')[:5]
    stat = Stat.objects.get(user=profile.user)
    total = stat.divAwinner + stat.divBwinner + stat.divCwinner + stat.divDwinner + stat.divOtherswinner

    labels = []
    data = []
    title = ''
    averages = Result.objects.filter(validation=1, player=profile.user, average__gt=0).order_by('-on_date')[:20]
    totals = averages.count()
    if totals > 0:
        for label in range(totals):
            label = label + 1
            labels.append(f'JG {label}')

        for average in averages:
            data.append(float(average.average))

        data = list(reversed(data))
        min_data = min(data)
        max_data = max(data)
        avg = profile.user.stat.bcmAvg
        title = f'Mín: {min_data}, Média: {avg}, Máx: {max_data}'

    context = {'total': total,
               'profile': profile,
               'stat': stat,
               'matches': matches,
               'labels': labels,
               'data': data,
               'title': title,
               'graph': totals}

    return render(request, 'user_public_profile.html', context)
