from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render


@login_required()
@permission_required('profiles.has_admin_role', raise_exception=True)
def dashboard(request):
    return render(request, 'enviroment.html')