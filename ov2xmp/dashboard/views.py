from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
# Create your views here.
def index(request):
    return render(request, 'dashboard/index.html', {"title": "Dashboard"})
