from django.shortcuts import render


def updateinfo(request):
    return render(request, 'update.html')
