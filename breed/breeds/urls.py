from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.add, name='add'),
    url(r'^(\d+)/$', views.breed, name='breed'),
    url(r'^(\d+)/find/$', views.find, name='find'),
    url(r'^statistics/$', views.statistics, name='statistics'),
    url(r'^match/$', views.match, name='match'),
    url(r'^comment/$', views.comment, name='comment'),
    url(r'^load/$', views.load, name='load'),
    url(r'^check/$', views.check, name='check'),
    url(r'^load_new/$', views.load_new, name='load_new'),
    url(r'^update/$', views.update, name='update'),
    url(r'^track_comments/$', views.track_comments, name='track_comments'),
    url(r'^remove/$', views.remove, name='remove_breed'),
]

