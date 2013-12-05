# -*- coding: utf-8 -*- 

from django.shortcuts import render_to_response
from models import Author, Poll_author, AuthorForm, PollForm
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext

text_error = ''

@csrf_exempt
def welcome(request):
    request.session.set_expiry(0)
    if request.method == 'GET':
        form = AuthorForm()
        text_error = ''
    elif request.method == 'POST':
        form = AuthorForm(request.POST)
        try:
            aut_form = form.save(commit=False)
            Author.objects.get(name=aut_form.name)
            request.session['_old_post'] = request.POST
            request.session['_param'] = 'name'
            return HttpResponseRedirect('/poll')
        except:
            try:
                Author.objects.get(email=aut_form.email)
                request.session['_old_post'] = request.POST
                request.session['_param'] = 'email'
                return HttpResponseRedirect('/poll')
            except:
                text_error = 'Por favor comprueba el nombre e email pues no \
                            nos apareces en la lista de autores.'

    response = render_to_response('login.html', 
                                  {'form': form, 'error': text_error},
                                  context_instance=RequestContext(request))
    return response

@csrf_exempt
def poll(request):
    if request.method == 'GET':
        form = AuthorForm(request.session.get('_old_post'))
        aut_form = form.save(commit=False)
        param = request.session.get('_param')
        if param == 'name':
            author = Author.objects.get(name=aut_form.name)
        elif param == 'email':
            author = Author.objects.get(email=aut_form.email)
        else:
            return HttpResponseRedirect('/')
        
        request.session['_author'] = author.id
        form_poll = PollForm()
        figure = 'author_' + str(author.id) + '.png'
        response = render_to_response('poll.html',
                                      {'form': form_poll, 'figure': figure},
                                      context_instance=RequestContext(request))
        return response
    elif request.method == 'POST':
        form = PollForm(request.POST)
        poll_form = form.save(commit=False)
        author_id = request.session.get('_author')
        poll = Poll_author(author=Author.objects.get(id=author_id),
                           resp1=poll_form.resp1,
                           resp2=poll_form.resp2,
                           resp3=poll_form.resp3,
                           info=poll_form.info)
        poll.save()
        return HttpResponseRedirect('/thanks')
    return HttpResponseRedirect('/')

def thanks(request):
    return render_to_response('thanks.html',
                              context_instance=RequestContext(request))