import base64, uuid, os
from typing import Type
from time import strftime

from django.conf import settings
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from .utils import *

import markdown

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Users must have a username')
        user = self.model(username=username.lower(),
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    
    def create_superuser(self, username, password):
        user = self.create_user(username, password)
        user.is_staff = True
        user.is_superuser = True
        user.is_a_participant = False
        self.is_competing = False
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    username            = models.CharField(max_length=20, unique=True)
    profile_picture     = models.ImageField(null=True, blank=True)
    biography           = models.TextField(null=True, blank=True)
    started_on          = models.DateTimeField(default=None, null=True, blank=True, verbose_name=u'start date')

    discord_username    = models.CharField(max_length=255, blank=True)
    discord_id          = models.BigIntegerField(null=True, blank=True)

    is_staff            = models.BooleanField(default=False)

    is_a_participant    = models.BooleanField(default=True)
    is_competing        = models.BooleanField(default=True)

    objects             = UserManager()

    USERNAME_FIELD      = 'username'
    REQUIRED_FIELDS     = ['password']
    
    id                  = models.CharField(max_length=ID_LENGTH, default=getRandomBase64String, primary_key=True, editable=False)

    def delete(self):
        self.delete_profile_picture()
        super(User, self).delete()
    
    def get_page(self):
        from django.urls import reverse
        return settings.SITE_URL + reverse('participants')
    
    def delete_profile_picture(self):
        absolutePath = ""
        if self.profile_picture:
            absolutePath = self.profile_picture.storage.base_location + "/" + self.profile_picture.field.upload_to + "/" + self.profile_picture.name
        if os.path.exists(absolutePath):
            os.remove(absolutePath)
        self.profile_picture = None
        self.save()
        

    def __str__(self):
        return str(self.username)

class Post(models.Model):
    title               = models.CharField(max_length=100, null=True)
    description         = models.TextField(null=True, blank=True)

    owner               = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE, null=False)
    date                = models.DateTimeField(auto_now_add=True, null=True)

    image               = models.ImageField(null=True, blank=True)
    video               = models.FileField(null=True, blank=True)
    likes               = models.ManyToManyField(User, blank=True)
    clicks              = models.BigIntegerField(null=True, blank=True)

    is_nsfw             = models.BooleanField(default=False)

    timestamp           = models.IntegerField(null=True)
    id                  = models.CharField(max_length=ID_LENGTH, default=getRandomBase64String, primary_key=True, editable=False)

    def update_timestamp(self, save=True):
        self.timestamp = getTimeStampFromDate(timezone.localtime(self.date))
        if save:
            super(Post, self).save()

    def increase_click_count(self):
        if not self.clicks:
            self.clicks = 0
        self.clicks += 1

        super(Post, self).save()
        
    def save(self, *args, **kwargs):
        if not self.timestamp:
            self.update_timestamp(save=False)
        if not self.clicks:
            self.clicks = 0

        super(Post, self).save(*args, **kwargs)

    def get_page(self):
        from django.urls import reverse
        return settings.SITE_URL + reverse('getPost', kwargs={"pk" : self.id})

    def delete(self):
        targets = []

        if self.image:
            targets.append(self.image)
        if self.video:
            targets.append(self.video)

        for target in targets:
            absolutePath = target.storage.base_location + "/" + target.field.upload_to + "/" + target.name
            if os.path.exists(absolutePath):
                os.remove(absolutePath)
        super(Post, self).delete()

    # Get's focused template context
    def getFocusedContext(self,
        title : str             = None, 
        transition_url : str    = None,
        posts                   = None
    ):
        if posts:
            next, previous = findPreviousAndLastPosts(posts, self)
        else:
            next, previous = None, None

        return self.getContext(
            title = title, 
            next = next, 
            previous = previous,
            transition_url = transition_url
        )

    # Get's template context
    def getContext(self,
        title : str             = None,
        next : 'Post'           = None, 
        previous : 'Post'       = None,
        show_nsfw : bool        = None,
        transition_url : str    = None, 
        focused_url : str       = None
    ):
        post = self
        post.date = timezone.localtime(self.date)
        context = {
            "post" : self,
            "title" : self.title if not title else title,
            "show_nsfw" : show_nsfw,
            "next" : next,
            "previous": previous,
            "transition_url" : transition_url,
            "focused_url" : focused_url
        }

        return context

    def __str__(self):
        if self.title and len(self.title) > 0:
            return str(self.title)
        else:
            return "NO TITLE"
    
    def get_local_time(self):
        return timezone.localtime(self.date)
    
class Variable(models.Model):
    name                = models.CharField(max_length=50, primary_key=True)

    label               = models.CharField(max_length=200, null=True, blank=True)
    date                = models.DateTimeField(null=True, blank=True)
    integer             = models.IntegerField(null=True, blank=True)
    file                = models.FileField(null=True, blank=True)

    text                = models.TextField(null=True, blank=True)

    def read(self, type):
        if type is int and self.integer:
            return self.integer
        
        elif type is str:
            if self.label:
                return self.label
            elif self.text:
                return self.text
        
        elif type is date:
            return self.date
        
        raise TypeError

    def __str__(self):
        return str(self.name)
    
class MarkdownPost(models.Model):
    title               = models.CharField(max_length=100, null=True, unique=True)
    label               = models.CharField(max_length=100, null=True, blank=True)
    
    contents            = models.TextField(null=True)
    date                = models.DateTimeField(auto_now_add=True)

    id                  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def save(self, *args, **kwargs):
        super(MarkdownPost, self).save(*args, **kwargs)

    def get_html(self):
        try:
            html = markdown.markdown("# " + self.title + "\n" + "*" + self.date.strftime("%A %d, %B %Y") + "*" + "\n\n" + self.contents)
        except Exception as e:
            html = "Cannot convert post to html: " + str(e)
        
        return html

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
