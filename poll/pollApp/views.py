# -*- coding: utf-8 -*- 

from django.shortcuts import render_to_response
from models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
import random

text_error = ''

@csrf_exempt
def welcome(request, email_hash=None):
    request.session.set_expiry(0)
    if request.method == 'GET':
        if email_hash == None:
            form = AuthorForm()
            try:
                del request.session['_email_hash']
            except:
                pass
            text_error = ''
        else:
            try:
                Author.objects.get(email_hash=email_hash)
                request.session['_email_hash'] = email_hash
                return HttpResponseRedirect('/poll')
            except:
                return HttpResponseRedirect('/')
    elif request.method == 'POST':
        form = AuthorForm(request.POST)
        try:
            aut_form = form.save(commit=False)
            Author.objects.get(name__iexact=aut_form.name)
            request.session['_old_post'] = request.POST
            request.session['_param'] = 'name'
            return HttpResponseRedirect('/poll')
        except:
            try:
                Author.objects.get(email__iexact=aut_form.email)
                request.session['_old_post'] = request.POST
                request.session['_param'] = 'email'
                return HttpResponseRedirect('/poll')
            except:
                text_error = 'Please you check your name and email because \
                            you don\'t appear in the author list'

    response = render_to_response('login.html', 
                                  {'form': form, 'error': text_error},
                                  context_instance=RequestContext(request))
    return response

@csrf_exempt
def poll(request):
    if request.method == 'GET':
        email_hash = request.session.get('_email_hash', None)
        if email_hash != None:
            author = Author.objects.get(email_hash=email_hash)
        else:
            form = AuthorForm(request.session.get('_old_post'))
            aut_form = form.save(commit=False)
            param = request.session.get('_param')
            if param == 'name':
                author = Author.objects.get(name__iexact=aut_form.name)
            elif param == 'email':
                author = Author.objects.get(email__iexact=aut_form.email)
            else:
                return HttpResponseRedirect('/')

        request.session['_author'] = author.id
        rand = random.randint(0,1)
        if rand == 0:
            type_poll = 1
            flag_fig = True
            flag_info = True
            figure = 'author_' + str(author.upeople_id) + '.png'
        else:
            type_poll = 2
            flag_fig = False
            flag_info = False
            figure = ''
        
        response = render_to_response('poll.html',
                                      {'poll': type_poll,
                                       'flag_fig': flag_fig,
                                       'flag_info': flag_info,
                                       'figure': figure},
                                       context_instance=RequestContext(request))
        return response
    elif request.method == 'POST':
        form = Poll1Form(request.POST)
        poll_form = form.save(commit=False)
        author_id = request.session.get('_author')
        author=Author.objects.get(id=author_id)
        poll = Poll_author(author=author,
                           upeople_id=author.upeople_id,
                           resp1=poll_form.resp1,
                           resp2=poll_form.resp2,
                           resp3=poll_form.resp3,
                           resp5=poll_form.resp5,
                           info=poll_form.info,
                           type_poll=1)
        poll.save()
        return HttpResponseRedirect('/thanks')
    return HttpResponseRedirect('/')

@csrf_exempt
def poll2(request):
    try:
        del request.session['_sec_post']
        form = Poll2Form(request.session.get('_first_post'))
        first_post = form.save(commit=False)
        form = Poll2bForm(request.POST)
        second_post = form.save(commit=False)
        author_id = request.session.get('_author')
        author=Author.objects.get(id=author_id)
        poll = Poll_author(author=author,
                           upeople_id=author.upeople_id,
                           resp1=first_post.resp1,
                           resp2=first_post.resp2,
                           resp3=first_post.resp3,
                           resp4=second_post.resp4,
                           resp5=second_post.resp5,
                           info=second_post.info,
                           type_poll=2)
        poll.save()
        return HttpResponseRedirect('/thanks')
    except:
        request.session['_first_post'] = request.POST
        request.session['_sec_post'] = True
        author_id = request.session.get('_author')
        author = Author.objects.get(id=author_id)
        figure = 'author_' + str(author.upeople_id) + '.png'
        response = render_to_response('poll2.html',
                                      {'figure': figure},
                                      context_instance=RequestContext(request))
        return response

def thanks(request):
    request.session.flush()
    return render_to_response('thanks.html',
                              context_instance=RequestContext(request))