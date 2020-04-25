from django.http import JsonResponse
from django.contrib.auth import authenticate, login as log
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.views.decorators.csrf import csrf_exempt

import json

def getSessionFromReq(request):
    data = request.GET.dict()
    sessKey = data.get('session-key')
    obj = Session.objects.filter(session_key=sessKey).get()
    return obj.get_decoded()

def getSessionKey(request):
    return request.session.session_key

def login(request):
    if request.method != "GET":
        return JsonResponse({"success": False, 'message': "invalid request method"})
    
    data = request.GET.dict()

    username, password = data['username'], data['password']

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"success": False, 'message': "authentication failed"})
    
    log(request, user)
    
    return JsonResponse({
        "success": True,
        "sessionKey": getSessionKey(request),
    })

@csrf_exempt
def signup(request):
    if request.method != "POST":
        return JsonResponse({"success": False, 'message': "invalid request method"})
    
    data = request.body
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)

    username, password, email, firstName, lastName = data['username'], data['password'], data['email'], data['firstName'], data['lastName']

    user = User.objects.create_user(email=email, username=username, password=password, first_name=firstName, last_name=lastName)
    user.save()

    print(user.username)

    user = authenticate(username=username, password=password)
    log(request, user)
    
    return JsonResponse({
        "success": True,
        "session-key": getSessionKey(request),
    })
    