# -*- coding: utf-8 -*- 

from django.db import models
from django.forms import ModelForm
from django.utils.translation import gettext as _

# Create your models here.
class Author(models.Model):
    name = models.CharField(max_length=40, blank=True)
    email = models.CharField(max_length=40, blank=True)
    email_hash = models.TextField(blank=True)
    upeople_id = models.IntegerField()
    
class Poll_author(models.Model):
    author = models.ForeignKey(Author)
    upeople_id = models.IntegerField()
    resp1 = models.TextField(blank=True)
    resp2 = models.TextField(blank=True)
    resp3 = models.TextField(blank=True)
    resp4 = models.TextField(blank=True)
    resp5 = models.TextField(blank=True)
    info = models.BooleanField()
    type_poll = models.IntegerField()

class AuthorForm(ModelForm):
    class Meta:
        model = Author
        exclude = ['email_hash', 'upeople_id']

class Poll1Form(ModelForm):
    class Meta:
        model = Poll_author
        exclude = ['author', 'upeople_id', 'resp4', 'type_poll']

class Poll2Form(ModelForm):
    class Meta:
        model = Poll_author
        exclude = ['author', 'upeople_id', 'resp4', 'resp5', 'info', 'type_poll']

class Poll2bForm(ModelForm):
    class Meta:
        model = Poll_author
        fields = ['resp4', 'resp5', 'info']