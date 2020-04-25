from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate, login as log

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

import json

def getSessionFromReq(request):
    data = request.GET.dict()
    sessKey = data.get('session-key')
    obj = Session.objects.filter(session_key=sessKey).get()
    return obj.get_decoded()

def getSessionKey(request):
    return request.session.session_key


def login(request):
    # checking if user exists
    try:
        session = getSessionFromReq(request)
        session['_auth_user_id']
        return JsonResponse({"success": False, 'message': "user already logged in"})
    except: pass

    # confirming request method
    if request.method != "GET":
        return JsonResponse({"success": False, 'message': "invalid request method"})
    
    # getting data
    data = request.GET.dict()
    username, password = data['username'], data['password']
    
    # checking if user exists
    user = authenticate(request, username=username, password=password)
    if user is None:
        # authentication failed
        return JsonResponse({"success": False, 'message': "authentication failed"})
    
    # logging user in
    log(request, user)
    
    # authentication success returning session key to client
    return JsonResponse({
        "success": True,
        "sessionKey": getSessionKey(request),
    })

@csrf_exempt
def signup(request):
    # checking if user is already logged in
    try:
        session = getSessionFromReq(request)
        session['_auth_user_id']
        return JsonResponse({"success": False, 'message': "user already logged in"})
    except: pass

    # confirming request method
    if request.method != "POST":
        return JsonResponse({"success": False, 'message': "invalid request method"})
    
    # serializing data from request body
    data = request.body
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)

    # unpacking data from serialized body
    username, password, email, firstName, lastName = data['username'], data['password'], data['email'], data['firstName'], data['lastName']

    # checking if user with that username already exists
    try: 
        User.objects.filter(username=username).get()
        return JsonResponse({"success": False, "message": "user with that username already exists"})
    except: pass
    
    # creating user object
    user = User.objects.create_user(email=email, username=username, password=password, first_name=firstName, last_name=lastName)
    user.save()
    
    # logging in user
    user = authenticate(username=username, password=password)
    log(request, user)
    
    # returning success and sessionKey for session storage
    return JsonResponse({
        "success": True,
        "sessionKey": getSessionKey(request),
    })
    