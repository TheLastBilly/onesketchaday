from . import views

from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('post/<str:pk>', views.getPost, name='getPost'),
    
    path('post/month/<str:pk>', views.getFocusedMonthPost, name='getFocusedMonthPost'),
    path('post/user/<str:pk>', views.getFocusedUserPost, name='getFocusedUserPost'),
    path('post/day/<str:pk>', views.getFocusedDayPost, name='getFocusedDayPost'),

    path('post/month/<str:pk>/<str:nature>', views.getFocusedMonthPost, name='getFocusedMonthPost'),
    path('post/user/<str:pk>/<str:nature>', views.getFocusedUserPost, name='getFocusedUserPost'),
    path('post/day/<str:pk>/<str:nature>', views.getFocusedDayPost, name='getFocusedDayPost'),

    path('', views.getTodaysPosts, name='getTodaysPosts'),
    path('404/', views.pageNotFound, name='pageNotFound'),
    path('500/', views.internalError, name='internalError'),
    
    path('day/<int:timestamp>', views.getPostsOfDay, name='getPostsOfDay'),
    path('day/<int:pk>', views.getPostsOfDay, name='getPostsOfDay'),
    
    path('month/<int:index>', views.getActiveDaysOfMonth, name='getActiveDaysOfMonth'),

    path('month/gallery/<int:index>', views.getGalleryOfMonth, name='getGalleryOfMonth'),
    path('month/gallery/<int:index>/<int:page>', views.getGalleryOfMonth, name='getGalleryOfMonth'),

    path('user/<str:index>', views.getPostsFromUser, name='getPostsFromUser'),
    path('user/<str:index>/<int:page>', views.getPostsFromUser, name='getPostsFromUser'),

    path('favicon', views.getFavicon, name='favicon'),
    
    path('updates', views.getUpdatesPage, name='updates'),
    path('about', views.getAboutPage, name='about'),
    path('participants', views.getParticipantsPage, name='participants'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)