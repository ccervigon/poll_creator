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
    
class Survey_author(models.Model):
    author = models.ForeignKey(Author)
    upeople_id = models.IntegerField()
    resp1 = models.TextField(blank=True)
    resp2 = models.TextField(blank=True)
    resp3 = models.TextField(blank=True)
    resp4 = models.TextField(blank=True)
    resp5 = models.TextField(blank=True)
    info = models.BooleanField()
    type_survey = models.IntegerField()

class AuthorForm(ModelForm):
    class Meta:
        model = Author
        exclude = ['email_hash', 'upeople_id']

class Survey1Form(ModelForm):
    class Meta:
        model = Survey_author
        exclude = ['author', 'upeople_id', 'type_survey']

class Survey2Form(ModelForm):
    class Meta:
        model = Survey_author
        exclude = ['author', 'upeople_id', 'resp4', 'resp5', 'info', 'type_survey']

class Survey2bForm(ModelForm):
    class Meta:
        model = Survey_author
        fields = ['resp4', 'resp5', 'info']