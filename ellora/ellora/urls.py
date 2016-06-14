from django.conf.urls import patterns, url
from ellora import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),)
        #url(r'^compute/$', views.get_json_text, name='compute'))
        
