from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

import bleach
from breed.activities.models import Activity
from django.contrib.gis.geos import Point
from geoposition.fields import GeopositionField
from django.db.models import deletion

FEMALE = 'FEMALE'
MALE = 'MALE'
BREED_SEX = (
    (MALE, 'Male'),
    (FEMALE, 'Female'),
    )
UNKNOWN = "UNKNOWN"
ANKOLE = "ANKOLE"
FRESIAN = "FRESIAN"
JERSEY = "JERSEY"
ZEBU = "ZEBU"
BREED_TYPE = (
    (ANKOLE, 'Ankole'),
    (JERSEY, 'Jersey'),
    (ZEBU, 'Zebu'),
    (FRESIAN, 'Fresian'),
    (UNKNOWN, 'Unknown'),
    )

COW = "COW"
PIG = "PIG"

ANIMAL_TYPE = (
    (COW, 'Cow'),
    (PIG, 'Pig'),
    )
class Breed(models.Model):
    user = models.ForeignKey(User, on_delete=deletion.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    animal_type = models.CharField(max_length=50, choices=ANIMAL_TYPE,default=COW)
    breed_type = models.CharField(max_length=50, choices=BREED_TYPE,default=UNKNOWN)
    breed = models.TextField(max_length=255)
    parent = models.ForeignKey('Breed', null=True, related_name="+", blank=True, on_delete=deletion.CASCADE)
    accuracy = models.IntegerField(default=100)
    matches = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    sex = models.CharField(max_length=8, choices=BREED_SEX,default=MALE)
    photo = models.ImageField(upload_to="breeds",
                             max_length=500, null=True, blank=True,
                             verbose_name=_("photo"))

    class Meta:
        verbose_name = _('Breed')
        verbose_name_plural = _('Breed')
        ordering = ('-date',)

    def __str__(self):
        return self.breed

    @staticmethod
    def get_breeds(from_breed=None):
        if from_breed is not None:
            breeds = Breed.objects.filter(parent=None, id__lte=from_breed)
        else:
            breeds = Breed.objects.filter(parent=None)
        return breeds

    @staticmethod
    def get_breeds_after(breed):
        breeds = Breed.objects.filter(parent=None, id__gt=breed)
        return breeds

    def get_comments(self):
        return Breed.objects.filter(parent=self).order_by('date')

    def calculate_matches(self):
        matches = Activity.objects.filter(activity_type=Activity.MATCH,
                                        currentbreed=self.pk).count()
        self.matches = matches
        self.save()
        return self.matches

    def get_matches(self):
        matches = Activity.objects.filter(activity_type=Activity.MATCH,
                                        currentbreed=self.pk)
        return matches

    def get_match(self):
        matches = self.get_matches()
        matchers = []
        for match in matches:
            matchers.append(match.breed)
        return matchers

    def get_match_breed(self):
        matches = self.get_matches()
        matchers = []
        for match in matches:
            matchers.append(match.breed)
        return Breed.objects.filter(id__in=matchers)

    def get_matchers(self):
        matches = self.get_matches()
        matchers = []
        for match in matches:
            matchers.append(match.user)
        return matchers

    def calculate_comments(self):
        self.comments = Breed.objects.filter(parent=self).count()
        self.save()
        return self.comments

    def comment(self, user, breed):
        breed_comment = Breed(user=user, breed=breed, parent=self)
        breed_comment.save()
        self.comments = Breed.objects.filter(parent=self).count()
        self.save()
        return breed_comment

    def linkfy_breed(self):
        return bleach.linkify(escape(self.breed))
