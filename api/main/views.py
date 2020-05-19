from django.http import JsonResponse
from django.shortcuts import redirect as redirect
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate, login as log

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from importlib import import_module
import json
from django.conf import settings

from .models import Post, Comment

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

def getSessionFromReq(request):
    data = request.GET.dict()
    sessKey = data.get('session-key')
    obj = SessionStore(session_key=sessKey)
    return obj

def getSessionKey(request):
    s = SessionStore()
    s.create()
    s['_auth_user_id'] = request.session['_auth_user_id']
    s.save()
    return s.session_key


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

    # added user id to session
    request.session['_auth_user_id']
    
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
    
    # added user id to session
    request.session['_auth_user_id']
    
    # returning success and sessionKey for session storage
    return JsonResponse({
        "success": True,
        "sessionKey": getSessionKey(request),
    })

def getPost(request, id):
    post = Post.objects.filter(pk=id)
    if not post.exists():
        return JsonResponse({"success": False, "message": "Post does not exist"})
    post = post.get()
    html = open(post.htmlDir, "r").read()

    return JsonResponse({
        "success": True,
        "title": post.title,
        "html": html,
        "date": post.date,
        "id": post.id
    })

def getLatestPosts(request, amount):
    posts = Post.objects.all()[::-1][:amount]
    retPosts = []
    for post in posts:
        content = getPost(request, post.id).content
        body_unicode = content.decode('utf-8')
        data = json.loads(body_unicode)
        retPosts.append(data)

    return JsonResponse({
        "success": True,
        "posts": retPosts
    })

@csrf_exempt
def createNewPost(request):
    session = getSessionFromReq(request)
    id = session['_auth_user_id']
    user = User.objects.filter(pk=id)

    data = request.body
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)

    title, html = data['title'], data['html']

    post = Post.objects.create(title=title)
    post.save()

    open("./html/"+str(post.id)+".html", "w").write(html)
    post.htmlDir = "./html/"+str(post.id)+".html"

    post.save()

    return JsonResponse({
        "success": True,
        "id": post.id
    })

@csrf_exempt
def editPost(request, id):
    session = getSessionFromReq(request)
    userId = session['_auth_user_id']
    user = User.objects.filter(pk=userId)

    data = request.body
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)

    title, html = data['title'], data['html']

    post = Post.objects.filter(id=id)
    if not post.exists():
        return JsonResponse({"success": False, "message": "Post does not exist"})
    post = post.get()
    if post.title != title:
        post.title = title
        post.save()
    open(post.htmlDir, "w").write(html)

    return JsonResponse({
        "success": True,
        "id": post.id
    })

def adminRedirect(request):
    return redirect("/admin")