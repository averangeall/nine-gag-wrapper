# Create your views here.

import json
from django.http import HttpResponse
from dictionary import NineDict

dictt = NineDict()

def index(request):
    return HttpResponse('Welcome to 9GAG Wrapper!')    

def get_recomm_words(request, gag_id):
    return HttpResponse(json.dumps(dictt.get_recomm(gag_id)))

def query_word(request):
    gag_id = int(request.GET.get('gag_id', None))
    word = request.GET.get('word', '')
    return HttpResponse(json.dumps(dictt.get_defis(word, gag_id)))
