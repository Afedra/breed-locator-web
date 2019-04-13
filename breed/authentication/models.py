from __future__ import unicode_literals

import hashlib
import os.path
import urllib

from django.conf import settings
from django.contrib.gis.db import models
from django.db.models import deletion
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from breed.activities.models import Notification
from django.contrib.gis.geos import Point
from geoposition.fields import GeopositionField
from geoposition import Geoposition

FARMER = 'FARMER'
DOCTOR = 'DOCTOR'
JOB_TITLE = (
    (FARMER, 'Farmer'),
    (DOCTOR, 'Doctor'),
    )

class Profile(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=deletion.CASCADE)    
    location = GeopositionField()
    job_title = models.CharField(max_length=50, null=True, blank=True, choices=JOB_TITLE)
    
    class Meta:
        db_table = 'auth_profile'

    def __str__(self):
        return self.user.username

    def get_location(self):
        return Geoposition(self.location.latitude,self.location.longitude) 

    def get_picture(self):
        no_picture = '/static/img/user.png'
        try:
            filename = settings.MEDIA_ROOT + '/profile_pictures/' +\
                self.user.username + '.jpg'
            picture_url = settings.MEDIA_URL + 'profile_pictures/' +\
                self.user.username + '.jpg'
            if os.path.isfile(filename):
                return picture_url
            else:
                gravatar_url = 'http://www.gravatar.com/avatar/{0}?{1}'.format(
                    hashlib.md5(self.user.email.lower()).hexdigest(),
                    urllib.parse.urlencode({'d': no_picture, 's': '256'})
                    )
                return gravatar_url

        except Exception:
            return no_picture

    def get_screen_name(self):
        try:
            if self.user.get_full_name():
                return self.user.get_full_name()
            else:
                return self.user.username
        except:
            return self.user.username

    def notify_matched(self, breed):
        if self.user != breed.user:
            Notification(notification_type=Notification.MATCHED,
                         from_user=self.user, to_user=breed.user,
                         breed=breed).save()

    def unotify_matched(self, breed):
        if self.user != breed.user:
            Notification.objects.filter(notification_type=Notification.MATCHED,
                                        from_user=self.user, to_user=breed.user,
                                        breed=breed).delete()

    def notify_commented(self, breed):
        if self.user != breed.user:
            Notification(notification_type=Notification.COMMENTED,
                         from_user=self.user, to_user=breed.user,
                         breed=breed).save()

    def notify_also_commented(self, breed):
        comments = breed.get_comments()
        users = []
        for comment in comments:
            if comment.user != self.user and comment.user != breed.user:
                users.append(comment.user.pk)

        users = list(set(users))
        for user in users:
            Notification(notification_type=Notification.ALSO_COMMENTED,
                         from_user=self.user,
                         to_user=User(id=user), breed=breed).save()

    def notify_favorited(self, question):
        if self.user != question.user:
            Notification(notification_type=Notification.FAVORITED,
                         from_user=self.user, to_user=question.user,
                         question=question).save()

    def unotify_favorited(self, question):
        if self.user != question.user:
            Notification.objects.filter(
                notification_type=Notification.FAVORITED,
                from_user=self.user,
                to_user=question.user,
                question=question).delete()

    def notify_answered(self, question):
        if self.user != question.user:
            Notification(notification_type=Notification.ANSWERED,
                         from_user=self.user,
                         to_user=question.user,
                         question=question).save()

    def notify_accepted(self, answer):
        if self.user != answer.user:
            Notification(notification_type=Notification.ACCEPTED_ANSWER,
                         from_user=self.user,
                         to_user=answer.user,
                         answer=answer).save()

    def unotify_accepted(self, answer):
        if self.user != answer.user:
            Notification.objects.filter(
                notification_type=Notification.ACCEPTED_ANSWER,
                from_user=self.user,
                to_user=answer.user,
                answer=answer).delete()


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=settings.AUTH_USER_MODEL)
post_save.connect(save_user_profile, sender=settings.AUTH_USER_MODEL)
