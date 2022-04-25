from datetime import date, time
from email.utils import localtime
from nis import cat
from django.core.exceptions import *
from django.utils import timezone
import os, base64
from calendar import monthrange

ID_LENGTH = 10

def getStartDate():
    from .models import Variable
    start = Variable.objects.filter(name="StartDate").first()
    if not start:
        raise ObjectDoesNotExist("Variable \"StartDate\" was not defined")
    
    return start.read(date)

def getPostsAfterStartedOn(q):
    posts = []
    for post in q:
        if post.owner.started_on <= post.date:
            posts.append(post)
    
    return posts

def getDaysFromStartDate():
    return getDaysFromStartDateToTimestamp(getTimeStampFromDate(timezone.localdate()))

def getTimeRemainingForSession():
    currentTime = timezone.localtime()
    endTime = timezone.localtime(getStartDate())
    endTime.replace(day=currentTime.day, month=currentTime.month, year=currentTime.year)
    
    if currentTime > endTime:
        endTime += timezone.timedelta(days=1)

    secondsRemaining = (endTime - currentTime).seconds

    hours = int(secondsRemaining/3600)
    secondsRemaining -= hours*3600
    
    minutes = int(secondsRemaining/60)
    secondsRemaining -= minutes*60

    seconds = secondsRemaining

    return hours, minutes, seconds

def getDaysFromStartDateToTimestamp(timestamp):
    start = getStartDate()
    offset = timezone.datetime(start.year, start.month, start.day)
    target = getDateFromTimestamp(timestamp)
    return (target - offset).days + 1

def getTimeStampFromDate(date):
    return getTimeStamp(date.year, date.month, date.day)

def getTimeStamp(year, month, day):
    return int(year)*10000 + int(month)*100 + int(day)

def getTodaysTimestamp():
    return getTimeStampFromDate(timezone.localdate())

def getDateFromTimestamp(timestamp):
    year = int(timestamp/10000)
    month = int((timestamp - year*10000)/100)
    day = int(timestamp - int(timestamp/100)*100)

    if year > 3000:
        year = 3000
    if year < 2000:
        year = 2000
    
    if month < 1:
        month = 1
    if month > 12:
        month = 12

    maxDays = monthrange(year, month)[-1]
    if day > maxDays:
        day = maxDays
    if day < 1:
        day = 1

    return timezone.datetime(year, month, day)

def validateTimeStamp(timestamp):
    return getTimeStampFromDate(getDateFromTimestamp(timestamp))

def findPreviousAndNextPosts(posts, post):
    posts_len = len(posts)
    previous_page = next_page = None

    i = 0
    for p in posts:
        if post == p:
            break
        i += 1
    
    if i < posts_len-1:
        previous_page = posts[i+1].id
    if i > 0 and posts_len > i:
        next_page = posts[i-1].id
    
    return previous_page, next_page

def findPreviousAndNextTimestamps(timestamp):
    next = previous = current = None

    from .models import Post
    posts = Post.objects.all().order_by('timestamp')
    for post in posts:
        if post.timestamp == timestamp:
            continue
        
        if current is not None and post.timestamp != current:
            if current < timestamp:
                previous = current
            
            if not next and current > timestamp:
                next = current
                break
        
        current = post.timestamp

    return previous, next

def getRandomBase64String(lenght=ID_LENGTH):
    new_id = base64.b64encode(os.urandom(lenght))
    return str(new_id, "utf-8").replace('/', 's')[:lenght]
