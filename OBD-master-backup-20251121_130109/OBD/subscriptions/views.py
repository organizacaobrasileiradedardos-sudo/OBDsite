from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from brasilonline.subscriptions.forms import SubscriptionUserForm
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from brasilonline.dashboards.players.profiles.models import Profile
from brasilonline.core.obdlib.token import HashObd



def subscribe(request):
    if request.method == 'POST':
        return CreateNewMember(request)
    else:
        return MemberSubscriptionPage(request)


def CreateNewMember(request):
    form = SubscriptionUserForm(request.POST)
    if not form.is_valid():
        return render(request, 'subscription.html', {'form': form})

    # Create User
    username = form.cleaned_data['username'].lower()
    email = form.cleaned_data['email'].lower()
    password = form.cleaned_data['password']
    password2 = form.cleaned_data['password2']
    user = User.objects.create_user(username, email, password)
    user.first_name = form.cleaned_data['first_name'].capitalize()
    user.last_name = form.cleaned_data['last_name'].capitalize()
    user.save()

    # Adding standards perms to User.
    content_type = ContentType.objects.get_for_model(Profile, for_concrete_model=True)
    has_player_role = Permission.objects.filter(content_type=content_type, codename='has_player_role').first()
    can_play_league = Permission.objects.filter(content_type=content_type, codename='can_play_league').first()
    user.user_permissions.add(has_player_role)
    user.user_permissions.add(can_play_league)


    # Creating Slug link for user/profile access.
    profile = Profile.objects.get(user=user)
    hash = HashObd(form.cleaned_data['email'], form.cleaned_data['username'], form.cleaned_data['first_name']).encript()
    profile.pin = hash
    profile.slug = slugify(profile.pin+'-'+user.first_name+' '+user.last_name)
    profile.save()

    # Send E-Mail to new member with a CC List to OBD Org.
    _send_email('Confirmação de Associação ao OBD',
                settings.DEFAULT_FROM_EMAIL,
                form.cleaned_data['email'],
                'subscription_email.txt',
                form.cleaned_data)

    # Save form to DB
    # Subscription.objects.create(**form.cleaned_data)

    # Success feedback
    messages.success(request, form.cleaned_data['first_name'])
    return HttpResponseRedirect('/subscribe/')


def MemberSubscriptionPage(request):
    logout(request)
    return render(request, 'subscription.html', {'form': SubscriptionUserForm()})


def _send_email(subject, from_, to, template_name, context):
    body = render_to_string(template_name, context)
    send_mail(subject, body, from_, [from_, to])
