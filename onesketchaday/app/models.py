import base64, uuid, os

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from .utils import *

import markdown

ID_LENGTH = 8

class UserManager(BaseUserManager):
    def create_user(self, telegramId, username, password=None, **extra_fields):
        if not telegramId:
            raise ValueError('Users must have a telegramId')
        if not username:
            raise ValueError('Users must have a username')
        user = self.model(telegramId=telegramId,
                          username=username.lower(),
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    
    def create_superuser(self, username, telegramId, password):
        user = self.create_user(telegramId, username, password)
        user.is_staff = True
        user.is_superuser = True
        user.is_a_participant = False
        self.is_competing = False
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    username            = models.CharField(max_length=20, unique=True)
    telegramId          = models.CharField(max_length=20, unique=True)
    is_staff            = models.BooleanField(default=False)

    is_a_participant     = models.BooleanField(default=True)
    is_competing        = models.BooleanField(default=True)

    objects             = UserManager()

    USERNAME_FIELD      = 'username'
    REQUIRED_FIELDS     = ['password']

    def __str__(self):
        return str(self.username)

class Post(models.Model):
    title               = models.CharField(max_length=100, null=True)
    description         = models.TextField(null=True, blank=True)

    owner               = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE, null=False)
    date                = models.DateTimeField(auto_now_add=True)

    image               = models.ImageField(null=True, blank=True, unique=True)
    likes               = models.IntegerField(default=0, editable=False)
    rating              = models.IntegerField(default=0, editable=False)

    timestamp           = models.IntegerField(null=True)
    id                  = models.CharField(max_length=ID_LENGTH+10, primary_key=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.timestamp:
            self.timestamp = getTimeStampFromDate(timezone.now())
            
        if not self.id:
            new_id = base64.b64encode(os.urandom(ID_LENGTH))
            self.id = str(new_id, "utf-8").replace('/', 's')

        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.title)
    
class Variable(models.Model):
    name                = models.CharField(max_length=50, primary_key=True)

    label               = models.CharField(max_length=200, null=True, blank=True)
    date                = models.DateTimeField(null=True, blank=True)
    integer             = models.IntegerField(null=True, blank=True)

    text                = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.name)
    
class MardownPost(models.Model):
    title               = models.CharField(max_length=100, null=True)
    
    contents            = models.TextField(null=True)
    html                = models.TextField(null=True, editable=False)
    date                = models.DateTimeField(auto_now_add=True)

    id                  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


    def save(self, *args, **kwargs):
        try:
            self.html = markdown.markdown(self.contents)
        except Exception as e:
            self.html = "Cannot convert post to html: " + str(e)

        super(MardownPost, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.title)
    

class Comment(models.Model):
    content = models.TextField(null=True)
    date = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")

    likes = models.ManyToManyField(User, related_name='comment_likes', blank=False)
    owner = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE, null=False)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return str(self.content)