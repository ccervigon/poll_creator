# -*- coding: utf-8 -*- 

from django.db import models
from django.forms import ModelForm
from django.utils.translation import gettext as _

# Create your models here.
class Author(models.Model):
    name = models.CharField(max_length=40, blank=True)
    email = models.CharField(max_length=40, blank=True)
    
class Poll_author(models.Model):
    author = models.ForeignKey(Author)
    resp1 = models.TextField(blank=True)
    resp2 = models.TextField(blank=True)
    resp3 = models.TextField(blank=True)
    info = models.BooleanField()

class AuthorForm(ModelForm):
    class Meta:
        model = Author

class PollForm(ModelForm):
    class Meta:
        model = Poll_author
        exclude = ['author']