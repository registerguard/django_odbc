from django.conf.urls import patterns, include, url

from turin import views

urlpatterns = patterns('',
    url(r'^today', views.today, name='local_news'),
)