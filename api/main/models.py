from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150)
    htmlDir = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, related_name='post', on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    name = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)