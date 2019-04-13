from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils.html import escape


class Activity(models.Model):
    FAVORITE = 'F'
    MATCH = 'M'
    UP_VOTE = 'U'
    DOWN_VOTE = 'D'
    ACTIVITY_TYPES = (
        (FAVORITE, 'Favorite'),
        (MATCH, 'MATCH'),
        (UP_VOTE, 'Up Vote'),
        (DOWN_VOTE, 'Down Vote'),
        )

    user = models.ForeignKey(User, on_delete=models.deletion.CASCADE)
    activity_type = models.CharField(max_length=1, choices=ACTIVITY_TYPES)
    date = models.DateTimeField(auto_now_add=True)
    breed = models.IntegerField(null=True, blank=True)
    currentbreed = models.IntegerField(null=True, blank=True)
    question = models.IntegerField(null=True, blank=True)
    answer = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'

    def __str__(self):
        return self.activity_type


class Notification(models.Model):
    MATCHED = 'M'
    COMMENTED = 'C'
    FAVORITED = 'F'
    ANSWERED = 'A'
    ACCEPTED_ANSWER = 'W'
    ALSO_COMMENTED = 'S'
    NOTIFICATION_TYPES = (
        (MATCHED, 'Matched'),
        (COMMENTED, 'Commented'),
        (FAVORITED, 'Favorited'),
        (ANSWERED, 'Answered'),
        (ACCEPTED_ANSWER, 'Accepted Answer'),
        (ALSO_COMMENTED, 'Also Commented'),
        )

    _MATCH_TEMPLATE = '<a href="/{0}/">{1}</a> matched your breed: <a href="/breeds/{2}/">{3}</a>'  # noqa: E501
    _COMMENTED_TEMPLATE = '<a href="/{0}/">{1}</a> commented on your breed: <a href="/breeds/{2}/">{3}</a>'  # noqa: E501
    _FAVORITED_TEMPLATE = '<a href="/{0}/">{1}</a> favorited your question: <a href="/questions/{2}/">{3}</a>'  # noqa: E501
    _ANSWERED_TEMPLATE = '<a href="/{0}/">{1}</a> answered your question: <a href="/questions/{2}/">{3}</a>'  # noqa: E501
    _ACCEPTED_ANSWER_TEMPLATE = '<a href="/{0}/">{1}</a> accepted your answer: <a href="/questions/{2}/">{3}</a>'  # noqa: E501
    _ALSO_COMMENTED_TEMPLATE = '<a href="/{0}/">{1}</a> also commentend on the breed: <a href="/breeds/{2}/">{3}</a>'  # noqa: E501

    from_user = models.ForeignKey(User, related_name='+', on_delete=models.deletion.CASCADE)
    to_user = models.ForeignKey(User, related_name='+', on_delete=models.deletion.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    breed = models.ForeignKey('breeds.Breed', null=True, blank=True, on_delete=models.deletion.CASCADE)
    question = models.ForeignKey('questions.Question', null=True, blank=True, on_delete=models.deletion.CASCADE)
    answer = models.ForeignKey('questions.Answer', null=True, blank=True, on_delete=models.deletion.CASCADE)
    notification_type = models.CharField(max_length=8,
                                         choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ('-date',)

    def __str__(self):
        if self.notification_type == self.MATCHED:
            return self._MATCH_TEMPLATE.format(
                escape(self.from_user.username),
                escape(self.from_user.profile.get_screen_name()),
                self.breed.pk,
                escape(self.get_summary(self.breed.breed))
                )
        elif self.notification_type == self.COMMENTED:
            return self._COMMENTED_TEMPLATE.format(
                escape(self.from_user.username),
                escape(self.from_user.profile.get_screen_name()),
                self.breed.pk,
                escape(self.get_summary(self.breed.breed))
                )
        elif self.notification_type == self.FAVORITED:
            return self._FAVORITED_TEMPLATE.format(
                escape(self.from_user.username),
                escape(self.from_user.profile.get_screen_name()),
                self.question.pk,
                escape(self.get_summary(self.question.title))
                )
        elif self.notification_type == self.ANSWERED:
            return self._ANSWERED_TEMPLATE.format(
                escape(self.from_user.username),
                escape(self.from_user.profile.get_screen_name()),
                self.question.pk,
                escape(self.get_summary(self.question.title))
                )
        elif self.notification_type == self.ACCEPTED_ANSWER:
            return self._ACCEPTED_ANSWER_TEMPLATE.format(
                escape(self.from_user.username),
                escape(self.from_user.profile.get_screen_name()),
                self.answer.question.pk,
                escape(self.get_summary(self.answer.description))
                )
        elif self.notification_type == self.ALSO_COMMENTED:
            return self._ALSO_COMMENTED_TEMPLATE.format(
                escape(self.from_user.username),
                escape(self.from_user.profile.get_screen_name()),
                self.breed.pk,
                escape(self.get_summary(self.breed.breed))
                )
        else:
            return 'Ooops! Something went wrong.'

    def get_summary(self, value):
        summary_size = 50
        if len(value) > summary_size:
            return '{0}...'.format(value[:summary_size])

        else:
            return value
