# Create your views here.

import json
from django.http import HttpResponse

def index(request):
    return HttpResponse('Welcome to 9GAG Wrapper!')    
