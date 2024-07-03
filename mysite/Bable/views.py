# Copyright Aden Handasyde 2019

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.db.models import F, Q, Count
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from .models import *
# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm
from .forms import *
#from instantiatetotality import *
from django.core.mail import EmailMessage


from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.forms import formset_factory, modelformset_factory
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse
from django.conf import settings

from django.utils import timezone

from unidecode import unidecode
from django.template import defaultfilters

from .serializers import *
from rest_framework import status
from rest_framework import viewsets, permissions, authentication
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils.text import slugify
from django.template.loader import render_to_string
#from weasyprint import HTML

from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _


from rest_framework.generics import CreateAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated # new import

# Create your views here.
from Bable.models import Post
from Bable.serializers import PostSerializer

#from coinbase_commerce.client import Client

from django.http import StreamingHttpResponse
import datetime
import time




# Stripe Auth here
from django.http import HttpResponseRedirect

import stripe
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator

from django.contrib.auth.mixins import LoginRequiredMixin

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

'''
@login_required
def stream(request):
	loggedinuser = User.objects.get(username=request.user.username)
	loggedinanon = Anon.objects.get(username=loggedinuser)
	now = datetime.datetime.now()
	def event_stream():
		while True:
			time.sleep(1)
			notifications = loggedinanon.notifications.filter(new=True)
			if not notifications:
				yield 'retry: 100000\n\n'
				break
			else:
				yield 'retry: 100000\n\n'
				yield 'data: {}'.format(notifications.count())

	return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


@login_required
def stream_unseen(request):
	loggedinuser = User.objects.get(username=request.user.username)
	loggedinanon = Anon.objects.get(username=loggedinuser)
	def event_stream():
		while True:
			time.sleep(1)
			notifications = loggedinanon.notifications.filter(new=True)
			recent_notification = notifications.filter(sent=False).order_by('creation_date').first()
			if not recent_notification:
				yield 'retry: 100000\n\n'
				break
			else:
				yield 'retry: 100000\n\n'
				yield 'data: {}'.format(recent_notification.text)
	return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


def send_notification(author, text):
    Notification.objects.create(
        author=author, text=text
    )
'''

from django.http import HttpResponseRedirect, JsonResponse

def grabvoteid(request):
	if request.GET.get('name'):
		q = request.GET['name']
		if Votes.objects.filter(the_vote_name__startswith=q):
			data = Votes.objects.filter(the_vote_name__startswith=q).order_by('-creation_date').values_list('id',flat=True).first()
			json = data
			return JsonResponse(json, safe=False)
		return JsonResponse([], safe=False)
	else:
		data = Votes.objects.all().order_by('-creation_date').values_list('id',flat=True).first()
		json = list(data)
		return JsonResponse(json, safe=False)



def autocomplete_votestyles(request):
	if request.GET.get('q'):
		q = request.GET.get('q')
		if Votes.objects.filter(the_vote_name__startswith=q):
			data = Votes.objects.filter(the_vote_name__startswith=q).order_by('-creation_date').values_list('the_vote_name',flat=True)
			json = list(data)
			return JsonResponse(json, safe=False)
		return JsonResponse([], safe=False)
	else:
		data = Votes.objects.all().order_by('-creation_date').values_list('the_vote_name',flat=True)
		json = list(data)
		return JsonResponse(json, safe=False)

def tower_time(request):
	ip = request.META.get('REMOTE_ADDR')
	timeSpent = request.POST['timeSpent']
	density = request.POST.getlist('density[]', False)
	post_ids = request.POST.getlist('ids[]', False)
	scrollHeight = request.POST['scrollHeight']
	clientHeight = request.POST['clientHeight']
	loggedinanon_scroll_type = request.POST['scroll_type']
	#print(density)
	#print(ip)
	duration = request.POST['duration']
	page_density = Page_Density.objects.create(ip=ip, time_spent=timeSpent, scroll_height=scrollHeight, client_height=clientHeight, duration=duration, scroll_type=loggedinanon_scroll_type)
	for post_id in post_ids:
		page_density.post_ids.add(Post_id.objects.create(the_posts_id=post_id))
	for dense in density:
		page_density.density.add(Densitivity.objects.create(dense=float(dense)//1))
	page_density.save()
	if request.user.is_authenticated:
		loggedinanon = Anon.objects.get(username=request.user)
		loggedinanon.home_page_density.add(page_density)
		loggedinanon.save()
	print("success")
	return HttpResponse("")


@login_required
def home_view(request):
	loggedinuser = User.objects.get(username=request.user.username)
	loggedinanon = Anon.objects.get(username=loggedinuser)

	if request.method == 'POST':
		charge_form = BreadForm(request.POST)
		if charge_form.is_valid():
			amount = charge_form.cleaned_data['amount']
			new_invoice = Invoice.objects.create(amount=charge_form.cleaned_data['amount'], item_name='Coinbase', author=request.user.username)
	else:
		amount = 5.00
	client = Client(api_key=settings.COINBASE_COMMERCE_API_KEY)
	domain_url = 'https://www.babylonpolice.com/B/'
	product = {
		'name': 'Ad credits',
		'description': 'A really good deal.',
		'local_price': {
			'amount': str(amount),
			'currency': 'USD'
		},
		'pricing_type': 'fixed_price',
		'redirect_url': domain_url+reverse('Bable:tob_user_view', kwargs={'user': request.user.username}),
		'cancel_url': domain_url+reverse('Bable:tob_user_view', kwargs={'user': request.user.username}),
	}
	charge = client.charge.create(**product)
	# 'charge': charge,
	return render(request, 'home.html', {
		'charge': charge,
	})


# Create your views here.
class ListPostAPIView(ListAPIView):
    """This endpoint list all of the available Posts from the database"""
    permission_classes = (IsAuthenticated,) #permission classes
    queryset = Post.objects.all()[:10]
    serializer_class = PostSerializer


class ListCreatePostAPIView(ListCreateAPIView):
    """This endpoint allows for creation of a Post"""
    permission_classes = (permissions.AllowAny,)#permission classes
    queryset = Post.objects.all()[:10]
    serializer_class = PostSerializer

class ListCreateWordAPIView(ListCreateAPIView):
    """This endpoint allows for creation of a Post"""
    permission_classes = (IsAuthenticated,)#permission classes
    queryset = Word.objects.all()[:10]
    serializer_class = WordSerializer

class ListCreateSponsorAPIView(ListCreateAPIView):
    """This endpoint allows for creation of a Post"""
    permission_classes = (IsAuthenticated,)#permission classes
    queryset = Sponsor.objects.all()[:10]
    serializer_class = SponsorSerializer


class ListCreateAngelNumberAPIView(ListCreateAPIView):
    """This endpoint allows for creation of a Post"""
    permission_classes = (permissions.AllowAny,)#permission classes
    queryset = AngelNumber.objects.all()[:10]
    serializer_class = AngelNumberSerializer

def ShowAngelNumber(request, number):
	angel_number = AngelNumber.objects.get(numbers=int(number))
	if request.user.is_authenticated:
		loggedinanon = Anon.objects.get(username=request.user)
		loggedinauthor = Author.objects.get(username=request.user.username)
		if angel_number.attributions.filter(author=loggedinauthor).first():
			attribution = angel_number.attributions.filter(author=loggedinauthor).first().words
		else:
			attribution = "Okay"
			

		return HttpResponse('number: '+number+', description: '+angel_number.description+', display: '+attribution)
	return HttpResponse('number: '+number+', description: '+angel_number.description)



OPEN_AI_API_KEY = settings.OPEN_AI_API_KEY
from openai import OpenAI
import json
def barcode_ai(request, numbers):
	client = OpenAI(api_key=OPEN_AI_API_KEY)

	it = 0
	double_count = 0
	triple_count = 0
	double = []
	triple = []
	if numbers[it] == numbers[1]:
		double[double_count] = it
		double_count += 1
	while it < len(numbers) - 2:
		if numbers[it] == numbers[it+1] == numbers[it+2]:
			triple[triple_count] = it
			triple_count += 1
		if numbers[it+1] == numbers[it+2]:
			double[double_count] = it+1
			double_count += 1
		it += 1
	angel_numbers = []
	if not AngelNumber.objects.first():
		for a in range(10):
			AngelNumber.objects.create(digits=1, numbers=a, description="This number"+str(a)+" means something special to do with how it sounds")
	for d in double:
		angel_numbers.append(AngelNumber.obejcts.get(numbers=numbers[d]))
	for t in triple:
		angel_numbers.append(AngelNumber.objects.get(numbers=numbers[t]))
	for n in numbers:
		print(n)
		angel_numbers.append(AngelNumber.objects.get(numbers=n))
	context = {}
	json_data = json.dumps(context)
	for a in angel_numbers:
		print(json.loads(json_data))
		json_data = json.dumps([json.loads(json_data),{"role":"user","content": a.description,}])
	chat_completion = client.chat.completions.create(messages=[({"role": "user","content": "I have the following content about a given numerological number:",},context,{"role": "user","content": "Write me a single sentence that fits this number: "+numbers,})],model="gpt-3.5-turbo",)

	return HttpResponse(chat_completion.choices[0].message.content)



class ListCreateExampleAPIView(ListCreateAPIView):
    """This endpoint allows for creation of a Post"""
    permission_classes = (IsAuthenticated,)#permission classes
    queryset = Example.objects.all()[:10]
    serializer_class = ExampleSerializer

class UpdatePostAPIView(UpdateAPIView):
    """This endpoint allows for updating a specific Post by passing in the id of the Post to update"""
    permission_classes = (IsAuthenticated,)#permission classes
    queryset = Post.objects.all()[:10]
    serializer_class = PostSerializer


class DeletePostAPIView(DestroyAPIView):
    """This endpoint allows for deletion of a specific Post from the database"""
    permission_classes = (IsAuthenticated,)#permission classes
    queryset = Post.objects.all()[:10]
    serializer_class = PostSerializer



class AuthorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


    queryset = Author.objects.all()[:100]
    serializer_class = AuthorSerializer

    def list(self, request):
        queryset = Author.objects.all()
        serializer = AuthorSerializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Author.objects.all()
        author = get_object_or_404(queryset, pk=pk)
        serializer = AuthorSerializer(author, context={'request': request})
        return Response(serializer.data)

from rest_framework.decorators import action


def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Allow: *"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")



class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    #authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]



    permission_classes = [permissions.AllowAny, ]
    queryset = Post.objects.all()[:10]
    serializer_class = PostSerializer

    def list(self, request):
        queryset = Post.objects.all()
        serializer = PostSerializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Post.objects.all()
        post = get_object_or_404(queryset, pk=pk)
        serializer = PostSerializer(post, context={'request': request}, many=True)
        return Response(serializer.data)


#CHANGING ANON PREFERENCES
@login_required
def change_anon_sort(request, sort):
	user_anon = Anon.objects.get(username=request.user)
	if sort == 'dictionaries':
		user_anon.anon_sort = 0
		user_anon.save()
	elif sort == 'saved_dictionaries':
		user_anon.anon_sort = 1
		user_anon.save()
	elif sort == 'examples':
		user_anon.anon_sort = 2
		user_anon.save()
	elif sort == 'tasks':
		user_anon.anon_sort = 3
		user_anon.save()
	elif sort == 'latest':
		user_anon.anon_sort = 4
		user_anon.save()
	elif sort == 'posted_comments':
		user_anon.anon_sort = 5
		user_anon.save()
	elif sort == 'saved_comments':
		user_anon.anon_sort = 6
		user_anon.save()
	elif sort == 'posts':
		user_anon.anon_sort = 7
		user_anon.save()
	elif sort == 'spaces':
		user_anon.anon_sort = 8
		user_anon.save()
	elif sort == 'saved_spaces':
		user_anon.anon_sort = 9
		user_anon.save()

	return redirect('Bable:'+request.COOKIES['current'])

@login_required
def change_anon_sort(request, sort):
	user_anon = Anon.objects.get(username=request.user)
	if sort == 'dictionaries':
		user_anon.anon_sort = 0
		user_anon.save()
	elif sort == 'saved_dictionaries':
		user_anon.anon_sort = 1
		user_anon.save()
	elif sort == 'examples':
		user_anon.anon_sort = 2
		user_anon.save()
	elif sort == 'tasks':
		user_anon.anon_sort = 3
		user_anon.save()
	elif sort == 'latest':
		user_anon.anon_sort = 4
		user_anon.save()
	elif sort == 'posted_comments':
		user_anon.anon_sort = 5
		user_anon.save()
	elif sort == 'saved_comments':
		user_anon.anon_sort = 6
		user_anon.save()
	elif sort == 'posts':
		user_anon.anon_sort = 7
		user_anon.save()
	elif sort == 'spaces':
		user_anon.anon_sort = 8
		user_anon.save()
	elif sort == 'saved_spaces':
		user_anon.anon_sort = 9
		user_anon.save()

	return redirect('Bable:'+request.COOKIES['current'])



@login_required
def change_comment_sort(request, sort):
	user_anon = Anon.objects.get(username=request.user)
	if sort == 'dictionaries':
		user_anon.comment_sort = 0
		user_anon.save()
	elif sort == '-dictionaries':
		user_anon.comment_sort = 1
		user_anon.save()
	elif sort == 'words':
		user_anon.comment_sort = 2
		user_anon.save()
	elif sort == '-words':
		user_anon.comment_sort = 3
		user_anon.save()
	elif sort == 'sponsors':
		user_anon.comment_sort = 4
		user_anon.save()
	elif sort == '-sponsors':
		user_anon.comment_sort = 5
		user_anon.save()
	elif sort == 'uniques':
		user_anon.comment_sort = 6
		user_anon.save()
	elif sort == '-uniques':
		user_anon.comment_sort = 7
		user_anon.save()
	elif sort == 'viewcount':
		user_anon.comment_sort = 8
		user_anon.save()
	elif sort == 'unseen':
		user_anon.comment_sort = 9
		user_anon.save()
	elif sort == 'latest':
		user_anon.comment_sort = 10
		user_anon.save()
	elif sort == 'stalest':
		user_anon.comment_sort = 11
		user_anon.save()
	elif sort == 'discussed':
		user_anon.comment_sort = 12
		user_anon.save()
	elif sort == 'final':
		user_anon.comment_sort = 13
		user_anon.save()
	elif sort == 'voters':
		user_anon.comment_sort = 14
		user_anon.save()



	return base_redirect(request, 0)

@login_required
def change_post_sort(request, sort):
	user_anon = Anon.objects.get(username=request.user)
	if sort == 'viral':
		user_anon.post_sort = 0
		user_anon.save()
	elif sort == 'early':
		user_anon.post_sort = 1
		user_anon.save()
	elif sort == 'freshest':
		user_anon.post_sort = 2
		user_anon.save()
	elif sort == 'eldest':
		user_anon.post_sort = 3
		user_anon.save()
	elif sort == 'uniques':
		user_anon.post_sort = 4
		user_anon.save()
	elif sort == 'voters':
		user_anon.post_sort = 5
		user_anon.save()
	elif sort == 'broadness':
		user_anon.post_sort = 6
		user_anon.save()
	elif sort == 'intricacy':
		user_anon.post_sort = 7
		user_anon.save()
	elif sort == 'talkative':
		user_anon.post_sort = 8
		user_anon.save()
	elif sort == 'homes':
		user_anon.post_sort = 9
		user_anon.save()
	elif sort == 'encouraged':
		user_anon.post_sort = 10
		user_anon.save()
	elif sort == 'votes':
		user_anon.post_sort = 11
		user_anon.save()
	elif sort == 'unvoted':
		user_anon.post_sort = 12
		user_anon.save()


	return base_redirect(request, 0)

@login_required
def change_example_sort(request, sort):
	user_anon = Anon.objects.get(username=request.user)
	if sort == 'freshest':
		user_anon.example_sort = 0
		user_anon.save()
	elif sort == 'oldest':
		user_anon.example_sort = 1
		user_anon.save()
	elif sort == 'precision':
		user_anon.example_sort = 2
		user_anon.save()
	elif sort == 'votes':
		user_anon.example_sort = 3
		user_anon.save()
	elif sort == 'unseen':
		user_anon.example_sort = 4
		user_anon.save()
	elif sort == 'views':
		user_anon.example_sort = 5
		user_anon.save()


	return base_redirect(request, 0)

@login_required
def change_attribute_sort(request, sort):
	user_anon = Anon.objects.get(username=request.user)
	if sort == 'latest':
		user_anon.attribute_sort = 0
		user_anon.save()
	elif sort == 'eldest':
		user_anon.attribute_sort = 1
		user_anon.save()
	elif sort == 'votes':
		user_anon.attribute_sort = 2
		user_anon.save()
	elif sort == '-votes':
		user_anon.attribute_sort = 3
		user_anon.save()
	elif sort == 'views':
		user_anon.attribute_sort = 4
		user_anon.save()
	elif sort == '-views':
		user_anon.attribute_sort = 5
		user_anon.save()

	return base_redirect(request, 0)

@login_required
def change_word_sort(request, sort):
	user_anon = Anon.objects.get(username=request.user)
	if sort == 'alphabetical':
		user_anon.word_sort = 0
		user_anon.save()
	elif sort == 'latest':
		user_anon.word_sort = 1
		user_anon.save()
	elif sort == 'eldest':
		user_anon.word_sort = 2
		user_anon.save()
	elif sort == 'pronunciations':
		user_anon.word_sort = 3
		user_anon.save()
	elif sort == 'attributes':
		user_anon.word_sort = 4
		user_anon.save()
	elif sort == 'similarities':
		user_anon.word_sort = 5
		user_anon.save()
	elif sort == 'translations':
		user_anon.word_sort = 6
		user_anon.save()
	elif sort == 'examples':
		user_anon.word_sort = 7
		user_anon.save()
	elif sort == 'relations':
		user_anon.word_sort = 8
		user_anon.save()
	elif sort == 'sponsor':
		user_anon.word_sort = 9
		user_anon.save()
	elif sort == 'viewcount':
		user_anon.word_sort = 10
		user_anon.save()
	elif sort == '-viewcount':
		user_anon.word_sort = 11
		user_anon.save()
	elif sort == 'price':
		user_anon.word_sort = 12
		user_anon.save()
	elif sort == '-price':
		user_anon.word_sort = 13
		user_anon.save()
	elif sort == 'spaces':
		user_anon.word_sort = 14
		user_anon.save()
	elif sort == 'stories':
		user_anon.word_sort = 15
		user_anon.save()
	elif sort == 'voters':
		user_anon.word_sort = 16
		user_anon.save()
	elif sort == '-voters':
		user_anon.word_sort = 17
		user_anon.save()

	return base_redirect(request, 0)



	return base_redirect(request, 0)

@login_required
def change_dictionary_sort(request, sort):
	user_anon = Anon.objects.get(username=request.user)
	if sort == 'freshest':
		user_anon.dictionary_sort = 0
		user_anon.save()
	elif sort == 'stalest':
		user_anon.dictionary_sort = 1
		user_anon.save()
	elif sort == 'common':
		user_anon.dictionary_sort = 2
		user_anon.save()
	elif sort == 'prized':
		user_anon.dictionary_sort = 3
		user_anon.save()
	elif sort == 'oldest':
		user_anon.dictionary_sort = 4
		user_anon.save()
	elif sort == 'newest':
		user_anon.dictionary_sort = 5
		user_anon.save()
	elif sort == 'dispersed':
		user_anon.dictionary_sort = 6
		user_anon.save()
	elif sort == 'origin':
		user_anon.dictionary_sort = 7
		user_anon.save()
	elif sort == 'words':
		user_anon.dictionary_sort = 8
		user_anon.save()
	elif sort == 'votes':
		user_anon.dictionary_sort = 9
		user_anon.save()
	elif sort == 'translations':
		user_anon.dictionary_sort = 10
		user_anon.save()
	elif sort == 'sentences':
		user_anon.dictionary_sort = 11
		user_anon.save()
	elif sort == 'renditions':
		user_anon.dictionary_sort = 12
		user_anon.save()
	elif sort == 'analyses':
		user_anon.dictionary_sort = 13
		user_anon.save()
	elif sort == 'viewcount':
		user_anon.dictionary_sort = 14
		user_anon.save()

	return base_redirect(request, 0)

#SORTING OF LISTED VIEWABLES
def sort_examples(examples, sort, count, length):
	if sort == 0:
		return examples.order_by('-latest_change_date')[count:count+length]
	elif sort == 1:
		return examples.order_by('latest_change_date')[count:count+length]
	elif sort == 2:
		return examples.annotate(q_words=Count('words', distinct=True)).order_by('words')[count:count+length]
	elif sort == 3:
		return examples.annotate(q_dictionaries=Count('dictionaries', distinct=True)).order_by('dictionaries')[count:count+length]
	elif sort == 4:
		return examples.order_by('views')[count:count+length]
	elif sort == 5:
		return examples.order_by('-views')[count:count+length]
	return examples.order_by('-views')[count:count+length]	

def sort_dictionaries(dictionaries, sort, count, length):
	count = int(count)
	if sort == 0:
		return dictionaries.order_by('-latest_change_date')[count:count+length]
	elif sort == 1:
		return dictionaries.order_by('latest_change_date')[count:count+length]
	elif sort == 2:
		return dictionaries.order_by('-price')[count:count+length]
	elif sort == 3:
		return dictionaries.order_by('price')[count:count+length]
	elif sort == 4:
		return dictionaries.order_by('-creation_date')[count:count+length]
	elif sort == 5:
		return dictionaries.order_by('creation_date')[count:count+length]
	elif sort == 6:
		return dictionaries.order_by('-traded_date')[count:count+length]
	elif sort == 7:
		return dictionaries.order_by('traded_date')[count:count+length]
	elif sort == 8:
		return dictionaries.annotate(q_words=Count('words', distinct=True)).order_by('q_words')[count:count+length]
	elif sort == 9:
		return dictionaries.annotate(q_votes=Count('votes', distinct=True)).order_by('q_votes')[count:count+length]
	elif sort == 10:
		return dictionaries.annotate(q_transl=Count('true_translations', distinct=True)).order_by('q_transl')[count:count+length]
	elif sort == 11:
		return dictionaries.annotate(q_sentences=Count('sentences', distinct=True)).order_by('q_sentences')[count:count+length]
	elif sort == 12:
		return dictionaries.annotate(q_renditions=Count('renditions', distinct=True)).order_by('q_renditions')[count:count+length]
	elif sort == 13:
		return dictionaries.annotate(q_analyses=Count('analyses', distinct=True)).order_by('q_analyses')[count:count+length]
	return dictionaries.order_by('viewcount')[count:count+length]

def sort_sponsors(sponsors, sponsor_sort, count, length):
	count = int(count)
	if sponsor_sort ==  0:
		return sponsors.order_by('the_sponsorship_phrase')[count:count+length]
	elif sponsor_sort == 1:
		return sponsors.order_by('-the_sponsorship_phrase')[count:count+length]
	elif sponsor_sort == 2:
		return sponsors.order_by('latest_change_date')[count:count+length]
	elif sponsor_sort == 3:
		return sponsors.order_by('-latest_change_date')[count:count+length]
	elif sponsor_sort == 4:
		return sponsors.order_by('-price')[count:count+length]
	elif sponsor_sort == 5:
		return sponsors.order_by('price')[count:count+length]
	elif sponsor_sort == 6:
		return sponsors.order_by('-allowable_expenditure')[count:count+length]
	elif sponsor_sort == 7:
		return sponsors.order_by('allowable_expenditure')[count:count+length]
	elif sponsor_sort == 8:
		return sponsors.order_by('votes')[count:count+length]
	elif sponsor_sort == 9:
		return sponsors.order_by('-votes')[count:count+length]
	elif sponsor_sort == 10:
		return sponsors.order_by('-views')[count:count+length]
	elif sponsor_sort == 11:
		return sponsors.order_by('views')[count:count+length]

def sort_comments(posts_comments, comment_sort, count, length):
	count = int(count)
	comment = posts_comments.first()
	if comment:
		if comment_sort == 0:
			if comment.sum_dictionaries:
				posts_comments.order_by('sum_dictionaries')[count:count+length]
			else:
				return posts_comments.annotate(sum_dictionaries=Count('dictionaries', distinct=True)).values('sum_dictionaries').order_by('sum_dictionaries')[count:count+length]
		elif comment_sort == 1:
			if comment.sum_dictionaries:
				posts_comments.order_by('sum_dictionaries')[count:count+length]
			else:
				return posts_comments.annotate(sum_dictionaries=Count('dictionaries', distinct=True)).values('sum_dictionaries').order_by('-sum_dictionaries')[count:count+length]
		elif comment_sort == 2:
			if comment.sum_words:
				posts_comments.order_by('sum_words')[count:count+length]
			else:
				return posts_comments.annotate(sum_words=Count('words', distinct=True)).values('sum_words').order_by('sum_words')[count:count+length]
		elif comment_sort == 3:
			if comment.sum_words:
				posts_comments.order_by('sum_words')[count:count+length]
			else:
				return posts_comments.annotate(sum_words=Count('words', distinct=True)).values('sum_words').order_by('-sum_words')[count:count+length]
		elif comment_sort == 4:
			if comment.sum_sponsors:
				posts_comments.order_by('sum_sponsors')[count:count+length]
			else:
				return posts_comments.annotate(sum_sponsors=Count('sponsors', distinct=True)).values('sum_sponsors').order_by('sum_sponsors')[count:count+length]
		elif comment_sort == 5:
			if comment.sum_sponsors:
				posts_comments.order_by('sum_sponsors')[count:count+length]
			else:
				return posts_comments.annotate(sum_sponsors=Count('sponsors', distinct=True)).values('sum_sponsors').order_by('-sum_sponsors')[count:count+length]
		elif comment_sort == 6:
			if comment.sum_votes:
				posts_comments.order_by('sum_votes')[count:count+length]
			else:
				return posts_comments.annotate(sum_votes=Count('votes', distinct=True)).values('sum_votes').order_by('sum_votes')[count:count+length]
		elif comment_sort == 7:
			if comment.sum_votes:
				posts_comments.order_by('sum_votes')[count:count+length]
			else:
				return posts_comments.annotate(sum_votes=Count('votes', distinct=True)).values('sum_votes').order_by('-sum_votes')[count:count+length]
		elif comment_sort == 8:
			return posts_comments.order_by('viewcount')[count:count+length]
		elif comment_sort == 9:
			return posts_comments.order_by('-viewcount')[count:count+length]
		elif comment_sort == 10:
			return posts_comments.order_by('-latest_change_date')[count:count+length]
		elif comment_sort == 11:
			return posts_comments.order_by('latest_change_date')[count:count+length]
		elif comment_sort == 12:
			if posts_comments.first().sum_dictionaries:
				posts_comments.order_by('sum_dictionaries')[count:count+length]
			else:
				return posts_comments.annotate(sum_has_commented=Count('has_commented', distinct=True)).values('sum_has_commented').order_by('sum_has_commented')[count:count+length]
		elif comment_sort == 13:
			if comment.sum_dictionaries:
				posts_comments.order_by('sum_dictionaries')[count:count+length]
			else:
				return posts_comments.annotate(sum_has_commented=Count('has_commented', distinct=True)).values('sum_has_commented').order_by('-sum_has_commented')[count:count+length]
		elif comment_sort == 14:
			if comment.sum_dictionaries:
				posts_comments.order_by('sum_dictionaries')[count:count+length]
			else:
				return posts_comments.annotate(sum_has_voted=Count('has_voted', distinct=True)).values('sum_has_voted').order_by('sum_has_voted')[count:count+length]
	return posts_comments

def sort_spaces(spaces, sort, count, length):
	count = int(count)
	if sort == 0:
		return spaces.order_by('-viewcount')[count:count+length]
	elif sort == 1:
		return spaces.order_by('viewcount')[count:count+length]
	elif sort == 2:
		return spaces.order_by('-latest_change_date')[count:count+length]
	elif sort == 3:
		return spaces.order_by('latest_change_date')[count:count+length]
	elif sort == 4:
		return spaces.annotate(q_posts=Count('posts', distinct=True)).order_by('q_posts')[count:count+length]
	elif sort == 5:
		return spaces.annotate(q_votes=Count('votes', distinct=True)).order_by('q_votes')[count:count+length]
	elif sort == 6:
		return spaces.annotate(q_sponsors=Count('sponsors', distinct=True)).order_by('q_sponsors')[count:count+length]
	elif sort == 7:
		return spaces.annotate(q_voters=Count('appoved_voters', distinct=True)).order_by('q_voters')[count:count+length]


def sort_posts(posts, sort, count, length):
	count = int(count)
	if sort == 0:
		return posts.order_by('-viewcount')[count:count+length]
	elif sort == 1:
		return posts.order_by('viewcount')[count:count+length]
	elif sort == 2:
		return posts.order_by('-latest_change_date')[count:count+length]
	elif sort == 3:
		return posts.order_by('latest_change_date')[count:count+length]
	elif sort == 11:
		return posts.order_by('-votes_count')[count:count+length]
	elif sort == 12:
		return posts.order_by('votes_count')[count:count+length]
	return posts.order_by('viewcount')[count:count+length]

'''
	elif sort == 4:
		if posts.first().sum_has_viewed:
			posts.order_by('sum_has_viewed')[count:count+length]
		else:
			return posts.annotate(sum_has_viewed=Count('has_viewed', distinct=True)).values('sum_has_viewed').order_by('sum_has_viewed')[count:count+length]
	elif sort == 5:
		if posts.first().sum_has_voted:
			posts.order_by('sum_has_voted')[count:count+length]
		else:
			return posts.annotate(sum_has_voted=Count('has_voted', distinct=True)).values('sum_has_voted').order_by('sum_has_voted')[count:count+length]
	elif sort == 6:
		if posts.first().sum_dictionaries:
			posts.order_by('sum_dictionaries')[count:count+length]
		else:
			return posts.annotate(sum_dictionaries=Count('dictionaries', distinct=True)).values('sum_dictionaries').order_by('sum_dictionaries')[count:count+length]
	elif sort == 7:
		if posts.first().sum_words:
			posts.order_by('sum_words')[count:count+length]
		else:
			return posts.annotate(sum_words=Count('words', distinct=True)).values('sum_words').order_by('sum_words')[count:count+length]
	elif sort == 8:
		if posts.first().sum_comments:
			posts.order_by('sum_comments')[count:count+length]
		else:
			return posts.annotate(sum_comments=Count('comments', distinct=True)).values('sum_comments').order_by('sum_comments')[count:count+length]
	elif sort == 9:
		if posts.first().sum_spaces:
			posts.order_by('sum_spaces')[count:count+length]
		else:
			return posts.annotate(sum_spaces=Count('spaces', distinct=True)).values('sum_spaces').order_by('sum_spaces')[count:count+length]
	elif sort == 10:
		if posts.first().sum_sponsors:
			posts.order_by('sum_sponsors')[count:count+length]
		else:
			return posts.annotate(sum_sponsors=Count('sponsors', distinct=True)).values('sum_sponsors').order_by('sum_sponsors')[count:count+length]
	'''


def sort_words(words, sort, count, length):
	count = int(count)
	if sort == 0:
		return words.order_by('the_word_itself')[count:count+length]
	elif sort == 1:
		return words.order_by('-latest_change_date')[count:count+length]
	elif sort == 2:
		return words.order_by('creation_date')[count:count+length]
	elif sort == 3:
		return words.annotate(q_pronunciations=Count('pronunciations', distinct=True)).order_by('q_pronunciations')[count:count+length]
	elif sort == 4:
		return words.annotate(q_attributes=Count('attributes', distinct=True)).order_by('q_attributes')[count:count+length]
	elif sort == 5:
		return words.annotate(q_similarities=Count('similarities', distinct=True)).order_by('q_similarities')[count:count+length]
	elif sort == 6:
		return words.annotate(q_translations=Count('translations', distinct=True)).order_by('q_translations')[count:count+length]
	elif sort == 7:
		return words.annotate(q_examples=Count('examples', distinct=True)).order_by('q_examples')[count:count+length]
	elif sort == 8:
		return words.annotate(q_relations=Count('relations', distinct=True)).order_by('q_relations')[count:count+length]
	elif sort == 9:
		return words.annotate(q_sponsors=Count('sponsors', distinct=True)).order_by('q_sponsors')[count:count+length]
	elif sort == 10:
		return words.order_by('viewcount')[count:count+length]
	elif sort == 11:
		return words.order_by('-viewcount')[count:count+length]
	elif sort == 12:
		for word in words:
			for sponsor in word.sponsors:
				test = sponsor.price_limit
				if test > highest_price:
					highest_price = test
			word.price_limit = highest_price
		return words.order_by('price_limit')[count:count+length]
	elif sort == 13:
		for word in words:
			for sponsor in word.sponsors:
				test = sponsor.price_limit
				if test > highest_price:
					highest_price = test
			word.price_limit = highest_price
		return words.order_by('-price_limit')[count:count+length]
	elif sort == 14:
		return words.annotate(q_spaces=Count('spaces', distinct=True)).order_by('q_spaces')[count:count+length]
	elif sort == 15:
		return words.annotate(q_stories=Count('stories', distinct=True)).order_by('q_ssponsors')[count:count+length]
	elif sort == 16:
		return words.annotate(q_votes=Count('votes', distinct=True)).order_by('q_votes')[count:count+length]
	elif sort == 17:
		return words.annotate(q_votes=Count('votes', distinct=True)).order_by('-q_votes')[count:count+length]
	return words.order_by('-viewcount')[count:count+length]

def tob_vote(request, vote_id):
	the_votes = Votes.objects.get(id=int(vote_id))
	return redirect('Bable:tob_users_vote', user=the_votes.author.username, vote=the_votes.id)


def tob_wallet(request, vote_id):
	vote_id = str(int(vote_id))
	if vote_id == "1234567890":
		user_test = Anon.objects.get(username__username='test')
		user_test.false_wallet += 100000
		user_test.save()

		'''
		user_test = Anon.objects.get(username__username='morrisonhaze')
		user_test.false_wallet += 100000
		user_test.save()
		user_test = Anon.objects.get(username__username='WOLFBROWN')
		user_test.false_wallet += 100000
		user_test.save()
		user_test = Anon.objects.get(username__username='Pudzy')
		user_test.false_wallet += 100000
		user_test.save()
		user_test = Anon.objects.get(username__username='hello')
		user_test.false_wallet += 100000
		user_test.save()
		user_test = Anon.objects.get(username__username='TacticalPsychosis')
		user_test.false_wallet += 200000
		user_test.save()
		'''
		
		
	return redirect('Bable:tob_user_view_count', user='Administrator', count=0)

import re

@login_required
def tob_email(request, token_id, count=0):
		count = int(count)
		if count > 25:
			mcount = count - 25
		else:
			mcount = 0
		count100 = count + 25
		if (token_id == "3456789") and (request.user.username == "test"):
			user_test = Anon.objects.get(username__username='test')
			user_test.false_wallet += 100000
			user_test.save()

			valid_email_users = []

			for user in User.objects.all().order_by('id')[count:count + count100]:
				if re.match(r"[^@]+@[^@]+\.[^@]+", user.email):
					if len(valid_email_users) < 25:
						valid_email_users.append({'email': user.email, 'username': user.username, 'id': user.id})

			all_anons = valid_email_users
			the_response = render(request, 'tob_view_emails.html', {"all_anons": all_anons, "count": count, "mcount": mcount, "count100": count100, })
			the_response.set_cookie('current', 'tob_email')
			the_response.set_cookie('count', count)
			return the_response
		return base_redirect(request, 0)

def tob_dic(request, dictionary_id):
	the_dic = Dictionary.objects.get(id=int(dictionary_id))
	return redirect('Bable:tob_users_dic', user=the_dic.author.username, dictionary=the_dic.the_dictionary_itself, count=0)

@login_required
def apply_votestyle(request):
	if request.method == 'POST':
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		apply_votestyle_form = ApplyVotestyleForm(request, data=request.POST)
		the_votes = Votes.objects.get(id=int(request.POST.get('the_vote_style')))
		if the_votes in loggedinanon.applied_votestyles.all():
			loggedinanon.applied_votestyles.remove(the_votes)
		else:
			loggedinanon.applied_votestyles.add(the_votes)

	return base_redirect(request, 0)

@login_required
def apply_votes(request):
	if request.method == 'POST':
		loggedinauthor = Author.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=request.user)
		create_votes_form = CreateVotesForm(request, data=request.POST)
		the_votes, x = Votes.objects.get_or_create(the_vote_name=request.POST.get('the_vote_name'), author=loggedinauthor, url2=request.POST.get('url2'))
		the_vote_styles_space = Space.objects.filter(saved_spaces=loggedinanon).filter(the_space_itself__the_word_itself=request.POST.get('the_vote_style'))
		for space in the_vote_styles_space:
			the_votes.the_vote_style = space.to_source()
			the_votes_source = Votes_Source.objects.create(author=space.to_source().author, the_vote_name=space.to_source().the_space_itself)
			the_votes_source.the_vote_style.add(Word_Source.objects.get(the_word_itself=space.to_source().the_space_itself.the_word_itself, home_dictionary=space.to_source().dictionary.to_full().the_dictionary_itself, author=loggedinauthor))
			the_votes_source.save()

			space.to_source().allowed_to_view_authors.add(loggedinauthor)
			the_votes.save()
			space.to_source().votessource.add(the_votes_source)
			space.save()

		the_votes.save()
		loggedinanon.created_votestyles.add(the_votes)
		loggedinanon.save()
	return base_redirect(request, 0)

@login_required
def apply_votes_to_votestyle(request, voteid):
	if request.method == 'POST':
		loggedinauthor = Author.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=request.user)
		create_votes_form = CreateVotesForm(request, data=request.POST)
		if create_votes_form.is_valid():
			the_votes = Votes.objects.get(id=int(voteid))
			the_vote_styles = Space.objects.filter(saved_spaces=loggedinanon).filter(the_space_itself__the_word_itself=create_votes_form.cleaned_data['the_vote_style'][0])
			for vote in the_vote_styles:
				the_votes.the_vote_style.add(vote.to_source())
			the_votes.save()
	return base_redirect(request, 0)

@login_required
def exclude_votes(request):
	if request.method == 'POST':
		loggedinanon = Anon.objects.get(username=request.user)
		exclude_votes_form = ExcludeVotesForm(request)
		if exclude_votes_form.is_valid():
			if Space.objects.get(saved_spaces=loggedinanon, the_space_itself__the_word_itself=exclude_votes_form.cleaned_data["the_vote_style"]):
				the_space = Space.objects.get(saved_spaces=loggedinanon, the_space_itself__the_word_itself=exclude_votes_form.cleaned_data["the_vote_style"])
				the_votes = Votes.objects.filter(saved_votestyles=loggedinanon, the_vote_style__the_space_itself__the_word_itself__in=exclude_votes_form.cleaned_data["the_vote_style"])
				for vote in the_votes:
					if vote in loggedinanon.saved_votestyles.all():
						loggedinanon.excluded_votestyles.remove(vote)
					else:
						loggedinanon.excluded_votestyles.add(vote)
			else:
				the_votes = Votes.objects.get(saved_votestyles=loggedinanon, the_vote_name=exclude_votes_form.cleaned_data["the_vote_style"])
				if the_votes in loggedinanon.saved_votestyles.all():
					loggedinanon.excluded_votestyles.remove(the_votes)
				else:
					loggedinanon.excluded_votestyles.add(the_votes)


	return base_redirect(request, 0)


@login_required
def apply_dic(request):
	if request.method == 'POST':
		loggedinanon = Anon.objects.get(username=request.user)
		apply_dic_form = ApplyDictionaryForm(request)
		if apply_dic_form.is_valid():
			the_dic = Dictionary.objects.get(purchased_dictionaries=loggedinanon, the_dictionary_itself=apply_dic_form.cleaned_data["the_dictionary_itself"])
			if the_dic in loggedinanon.applied_dictionaries.all():
				loggedinanon.applied_dictionaries.remove(the_dic)
			else:
				loggedinanon.applied_dictionaries.add(the_dic)
	return base_redirect(request, 0)

@login_required
def exclude_dic(request):
	if request.method == 'POST':
		loggedinanon = Anon.objects.get(username=request.user)
		exclude_dic_form = ExcludeDictionaryAuthorForm(request.POST)
		if exclude_dic_form.is_valid():
			the_author = Author.objects.get(username=exclude_dic_form.cleaned_data["username"])
			if the_author in loggedinanon.excluded_dic_authors.all():
				loggedinanon.excluded_dic_authors.remove(the_author)
			else:
				loggedinanon.excluded_dic_authors.add(the_author)



	return base_redirect(request, 0)


#TUTORIAL FOR CREATION
def become_god(request):
	# After you create your account, you have to create an Anon if you want to save any Sorting Preferences,
	# After that you need to create an Author if you want to leave a History,
	# Then you can save, buy or rent a dictionary of terms, each term can have a number of Spaces,
	# Each Space is the home of a voting system, and if someone creates it, posting or moderating bots, public or private.
	# Posts can be submitted to multiple spaces (marked), however this doesn't always prevent reposts.
	# Votes can be used to train Artificial Intelligence for adjusting sorting algorithms, 
	# however that's free for anyone to use, like the rest of the data, given that the post is open to your viewing.

	# Some dictionaries have Pre-requisite Dictionaries, this means you'll have to buy multiple things to unlock them.
	# That means, people can have layers of spaces, comments and jokes on your material that you can't even see.
	# Yes, they may be talking about you, behind your back. They can also host their own private and invite-only discussions.
	# As can you.

	# Your password is not stored in our database, so it can't be stolen in a hack.
	# Because we are displaying the content back to users, encryption is un-necessary
	# Because AI can generate infinite things that could be censored, we won't censor anything. 
	# All advertising is link-based, not tracker-based, we don't care about your identity,
	# as long as someone buys the product, you deserve a majority proportion.
	# If you post a lot, or are viewed by a lot of people, or create dictionaries,
	# you can earn the points to buy other dictionaries,

	# Dictionaries can be for different languages, cultures, (secret) societies, clubs, fiction or non-fiction.
	# Not only do they hold the keys to understanding a worldview and it's stories,
	# But they also unlock the spaces for content generated by AI trained on your very own perception and interests.

	# You may have as many hive-minds as you like.
	# All content is a reflection of your imagination and the ability to code.

	# When exploring Dictionaries it can be useful to save 'Tasks' to show where you are up to.
	# 

	# excluding a votestyle enables a dictionary to take it in as a True_translation_before, which can be applied to pre-edit list-displays
	return render(request, 'become_god.html')


def roadmap(request):

	return render(request, 'roadmap.html', {})

#CREATION OF USER'S OBJECTS
@login_required
def create_task(request):
	user_anon = Anon.objects.filter(username=request.user)
	user_author = Author.objects.filter(username=request.user.username)
	task_form = TaskForm(request.POST)
	if task_form.is_valid():
		new_task = Task.objects.create(the_owner=user_author, the_task_itself=task_form.cleaned_data['the_task_itself'], priority=task_form.cleaned_data['priority'])
	return base_redirect(request, 0)
#current


@login_required
def create_word(request):
	user_anon = Anon.objects.get(username=request.user)
	user_author = Author.objects.get(username=request.user.username)
	# equivalent to create_task method, but validity not cared for.
	updated_data = request.POST.copy()
	new_word_dic_itself = defaultfilters.slugify(unidecode(updated_data["home_dictionary"]))
	new_word_word_itself = defaultfilters.slugify(unidecode(updated_data["the_word_itself"]))
	home_dic_s = Dictionary_Source.objects.get(the_dictionary_itself=new_word_dic_itself, author=user_author)
	home_dic = Dictionary.objects.get(the_dictionary_itself=new_word_dic_itself, author=user_author)
	#word_form = WordForm(request.POST)
	#word_form.home_dictionary = Dictionary_Source.objects.get(the_dictionary_itself=request.POST.home_dictionary)
	if new_word_dic_itself and new_word_word_itself:
		if new_word_dic_itself in user_anon.dictionaries.all().values_list('the_dictionary_itself', flat=True):
			if new_word_word_itself in home_dic_s.words.all().values_list('the_word_itself', flat=True):
				return redirect('Bable:tob_users_dic_word_count', user=request.user.username, dictionary=new_word_dic_itself, word=new_word_word_itself, count=0)
			new_word = Word.objects.create(the_word_itself=new_word_word_itself, home_dictionary=home_dic_s, author=user_author)
			new_word.ap_voters.add(user_author)
			new_word.save()
			home_dic.words.add(new_word)
			home_dic.save()
			new_word_s = Word_Source.objects.create(the_word_itself=new_word_word_itself, home_dictionary=new_word_dic_itself, author=user_author)
			home_dic_s.words.add(new_word_s)
			home_dic_s.save()
			return redirect('Bable:tob_users_dic_word_count', user=request.user.username, dictionary=new_word_dic_itself, word=new_word_word_itself, count=0)
	return base_redirect(request, 0)

@login_required
def submit_font(request, word_id):
	user_anon = Anon.objects.get(username=request.user)
	user_author = Author.objects.get(username=request.user.username)
	# equivalent to create_task method, but validity not cared for.
	updated_data = request.POST.copy()
	fontform = FontForm(request.POST)
	#word_form.home_dictionary = Dictionary_Source.objects.get(the_dictionary_itself=request.POST.home_dictionary)
	if fontform.is_valid():
		fontedword = Word.objects.get(id=word_id)
		fontedword.fontsize = fontform.cleaned_data["fontsize"]
		fontedword.fontstyle = fontform.cleaned_data["fontstyle"]
		fontedword.fontype = fontform.cleaned_data["fontype"]
		fontedword.save()

	return base_redirect(request, 0)


@login_required
def create_dic(request):
	loggedinanon = Anon.objects.get(username=request.user)
	loggedinauthor = Author.objects.get(username=request.user.username)

	dic_form = DictionaryForm(request.POST)
	if dic_form.is_valid():
		if Dictionary.objects.filter(the_dictionary_itself=defaultfilters.slugify(unidecode(dic_form.cleaned_data['the_dictionary_itself'])), author=loggedinauthor):
			error = 'duplicate name error'
			return base_redirect(request, error)
		new_dic = Dictionary.objects.create(the_dictionary_itself=defaultfilters.slugify(unidecode(dic_form.cleaned_data['the_dictionary_itself'])), author=loggedinauthor, public=dic_form.cleaned_data['public'], for_sale=dic_form.cleaned_data['for_sale'], entry_fee=dic_form.cleaned_data['entry_fee'], continuation_fee=dic_form.cleaned_data['continuation_fee'], invite_only=dic_form.cleaned_data['invite_only'])
		loggedinanon.dictionaries.add(new_dic)
		loggedinanon.purchased_dictionaries.add(new_dic)
		loggedinanon.sum_dictionaries += 1
		loggedinanon.save()
		new_dic.purchase_orders.add(Purchase_Order.objects.create(author=loggedinauthor))
		Dictionary_Source.objects.create(the_dictionary_itself=new_dic.the_dictionary_itself, author=loggedinauthor).purchasers.add(loggedinauthor)
		return redirect('Bable:tob_users_dic', dictionary=new_dic.the_dictionary_itself, user=request.user.username, count=0)
	else:
		print(dic_form.cleaned_data)
		return HttpResponse(dic_form.errors)
	return redirect('Bable:tob_user_view_count', user=request.user.username, count=0)

@login_required
def create_space(request):
	loggedinanon = Anon.objects.get(username=request.user)
	loggedinauthor = Author.objects.get(username=request.user.username)

	space_data = request.POST.copy()

	word_source_for_ss = Word_Source.objects.filter(the_word_itself=defaultfilters.slugify(unidecode(space_data['the_space_itself'])), author=loggedinauthor).first()
	dic_source_for_ss = Dictionary_Source.objects.get(the_dictionary_itself=word_source_for_ss.home_dictionary, author=loggedinauthor)

	new_source_space = SpaceSource.objects.create(the_space_itself=word_source_for_ss, dictionary=dic_source_for_ss, author=loggedinauthor)
	new_source_space.allowed_to_view_authors.add(loggedinauthor)
	new_source_space.save()
	if request.POST.get('for_sale') == 'on':
		for_sale = True
	else:
		for_sale = False
	if request.POST.get('public') == 'on':
		public = True
	else:
		public = False

	if request.POST.get('invite_only') == 'on':
		invite_only = True
	else:
		invite_only = False

	if request.POST.get('invite_active') == 'on':
		invite_active = True
	else:
		invite_active = False

	if request.POST.get('free_sponsorships') == 'on':
		free_sponsorships = True
	else:
		free_sponsorships = False

	if request.POST.get('anyone_can_edit') == 'on':
		anyone_can_edit = True
	else:
		anyone_can_edit = False
	if request.POST.get('elected_sponsorships') == 'on':
		elected_sponsorships = True
	else:
		elected_sponsorships = False

	new_space = Space.objects.create(the_space_itself=Word.objects.get(the_word_itself=defaultfilters.slugify(unidecode(space_data['the_space_itself'])), home_dictionary=dic_source_for_ss, author=loggedinauthor), author=loggedinauthor, sidebar=request.POST.get('sidebar'), public=public, for_sale=for_sale, free_sponsorships=free_sponsorships, anyone_can_edit=anyone_can_edit, elected_sponsorships=elected_sponsorships, entry_fee=request.POST.get('entry_fee'), continuation_fee=request.POST.get('continuation_fee'), invite_only=invite_only, invite_active=invite_active, invite_code=request.POST.get('invite_code'))
	new_space.approved_voters.add(loggedinauthor)
	new_space.save()
	spaces_home_word = Word.objects.get(author=loggedinauthor, the_word_itself=defaultfilters.slugify(unidecode(space_data['the_space_itself'])), home_dictionary=dic_source_for_ss)
	spaces_home_word.spaces.add(new_source_space)
	spaces_home_word.save()
	loggedinanon.spaces.add(new_space)
	loggedinanon.save()
	return redirect('Bable:tob_users_space', user=request.user.username, space_id=new_space.id, count=0)


# Safe
def delete_own_dic(request, user, dictionary):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.filter(the_dictionary_itself=dictionary).first() # or the_dictionary_itself=

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		# wallet function... could become crypto/blockchain, but it is infeasible.
		if loggedinanon.username.username == user_anon.username.username:
			if get_object_or_404(Dictionary_Source, author=loggedinauthor, the_dictionary_itself=dictionary): # add .first()?
				users_dic_source = Dictionary_Source.objects.get(author=loggedinauthor, the_dictionary_itself=dictionary)
				if users_dic_source.words:
					for word in users_dic_source.words.all():
						users_dic_source.words.remove(word)
						word.delete()
				if users_dic.wordgroups:
					for wordgr in users_dic.wordgroups.all():
						users_dic.wordgroups.remove(wordgr)
						wordgr.delete()
				if users_dic.true_translations:
					for tran in users_dic.true_translations.all():
						users_dic.true_translations.remove(tran)
						tran.delete()
				if users_dic.sentences:
					for sent in users_dic.sentences.all():
						users_dic.sentences.remove(sent)
						for rendition in sent.renditions.all():
							rendition.delete()
						sent.delete()
				if users_dic.analyses:
					for analy in users_dic.analyses.all():
						users_dic.analysis.remove(analy)
						analy.delete()
				if users_dic.words:
					for word in users_dic.words.all():
						users_dic.words.remove(word)
				users_dic_source.delete()
			if Anon.objects.filter(purchased_dictionaries__the_dictionary_itself=dictionary, purchased_dictionaries__author=loggedinauthor):
				for an in Anon.objects.filter(purchased_dictionaries__the_dictionary_itself=dictionary, purchased_dictionaries__author=loggedinauthor):
					an.purchased_dictionaries.remove(users_dic)
			if Post.objects.filter(dictionaries__the_dictionary_itself=dictionary):
				for po in Post.objects.filter(dictionaries__the_dictionary_itself=dictionary):
					po.dictionaries.remove(users_dic)
			users_dic.delete()
			loggedinanon.sum_dictionaries -= 1
			loggedinanon.save()


		else:
			return HttpResponse("Hey, it's not yours to delete.")
	else:
		return HttpResponse("Oi, you're not logged in.")

	return base_redirect(request, 0)



def delete_bought_dic(request, user, dictionary):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.purchased_dictionaries.all().filter(the_dictionary_itself=dictionary).first() # or the_dictionary_itself=

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		# wallet function... could become crypto/blockchain, but it is infeasible.
		if loggedinanon.username.username == user_anon.username.username:
			if get_object_or_404(Dictionary_Source, author=loggedinauthor, the_dictionary_itself=dictionary): # add .first()?
				users_dic_source = Dictionary_Source.objects.get(author=loggedinauthor, the_dictionary_itself=dictionary)
				if users_dic_source.words:
					for word in users_dic_source.words.all():
						users_dic_source.words.remove(word)
						word.delete()
				if users_dic.wordgroups:
					for wordgr in users_dic.wordgroups.all():
						users_dic.wordgroups.remove(wordgr)
						wordgr.delete()
				if users_dic.true_translations:
					for tran in users_dic.true_translations.all():
						users_dic.true_translations.remove(tran)
						tran.delete()
				if users_dic.sentences:
					for sent in users_dic.sentences.all():
						users_dic.sentences.remove(sent)
						for rendition in sent.renditions.all():
							rendition.delete()
						sent.delete()
				if users_dic.analyses:
					for analy in users_dic.analyses.all():
						users_dic.analysis.remove(analy)
						analy.delete()
				if users_dic.words:
					for word in users_dic.words.all():
						users_dic.words.remove(word)
				users_dic_source.delete()
			if Anon.objects.filter(purchased_dictionaries__the_dictionary_itself=dictionary, purchased_dictionaries__author=loggedinauthor):
				for an in Anon.objects.filter(purchased_dictionaries__the_dictionary_itself=dictionary, purchased_dictionaries__author=loggedinauthor):
					an.purchased_dictionaries.remove(users_dic)
			if Post.objects.filter(dictionaries__the_dictionary_itself=dictionary):
				for po in Post.objects.filter(dictionaries__the_dictionary_itself=dictionary):
					po.dictionaries.remove(users_dic)
			users_dic.delete()


		else:
			return HttpResponse("Hey, it's not yours to delete.")
	else:
		return HttpResponse("Oi, you're not logged in.")

	return base_redirect(request, 0)

###
def delete_own_word(request, user, dictionary, word):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	user_author = Author.objects.get(username=user)
	users_dic = user_anon.dictionaries.filter(the_dictionary_itself=dictionary).first() # or the_dictionary_itself=
	dics_word = Word.objects.get(home_dictionary=users_dic.to_source(), author=user_author, the_word_itself=word)

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		# wallet function... could become crypto/blockchain, but it is infeasible.
		if loggedinanon.username.username == user_anon.username.username:
			if Word.objects.get(home_dictionary=users_dic.to_source(), the_word_itself=word): # add .first()?
				users_dic.words.remove(dics_word)
				if dics_word.to_source():
					users_dic.to_source().words.remove(dics_word.to_source())
					dics_word.to_source().delete()
				dics_word.delete()
				# MAY NEED TO REMOVE ON IF CLAUSE OF EXISTENCE FOR EACH THAT CAN CONTAIN A Comment_Source
				request.COOKIES['current'] = 'tob_users_dic'
	return base_redirect(request, 0)

def delete_own_word_id(request, word_id):
	dics_word = Word.objects.get(id=int(word_id))

	return redirect('Bable:delete_own_word', dics_word.home_dictionary.author.username, dics_word.home_dictionary.the_dictionary_itself, dics_word.the_word_itself)

# which is true comment, or the source comment.
def delete_own_com(request, com, which):
	user_themself = User.objects.get(username=request.user.username)
	user_anon = Anon.objects.get(username=user_themself)
	com = int(com)
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		# wallet function... could become crypto/blockchain, but it is infeasible.
		if loggedinanon.username.username == user_anon.username.username:
			if which == 'source':
				if Comment_Source.objects.filter(author=loggedinauthor, id=com): # add .first()?
					users_com_source = Comment_Source.objects.filter(author=loggedinauthor, id=com)
					users_com_source.delete()
				else:
					return base_redirect(request, "Not your comment to delete")

			else:
				if Comment.objects.filter(author=loggedinauthor, id=com):
					users_com = Comment.objects.filter(author=loggedinauthor, id=com).first()
					users_com.delete()

				# MAY NEED TO REMOVE ON IF CLAUSE OF EXISTENCE FOR EACH THAT CAN CONTAIN A Comment_Source
	return redirect('Bable:tob_user_view_count', user=request.user.username, count=0)


def delete_own_attr(request, user, dic, word, attr):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.filter(the_dictionary_itself=dic).first() # or the_dictionary_itself=

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		if loggedinanon.username.username == user_anon.username.username:
			users_word = users_dic.words.filter(the_word_itself=word).first()
			if users_word: # first?
				users_att = users_word.attributes.get(id=int(attr))
				if users_att:
					users_word.attributes.remove(users_att)
					Attribute.objects.get(id=int(attr)).delete()


	return redirect('Bable:tob_users_dic_word_attribute', user=user, dictionary=dic, word=word, attribute=0)


def delete_own_attr_def(request, user, dic, word, attr, defin):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.filter(the_dictionary_itself=dic).first() # or the_dictionary_itself=

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		if loggedinanon.username.username == user_anon.username.username:
			users_word = users_dic.words.filter(the_word_itself=word).first()
			if users_word: # first?
				users_att = users_word.attributes.filter(attribute__id=int(attr)).first()
				if users_att:
					users_def = users_att.definitions.filter(definition__id=int(defin)).first()
					if users_def:
						users_att.remove(users_def)
						Definition.objects.get(definition__id=int(defin)).delete()


	return redirect('Bable:tob_users_dic_word_attribute', user=user, dictionary=dic, word=word)


def delete_own_attr_syn(request, user, dic, word, attr, syn):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.filter(the_dictionary_itself=dic).first() # or the_dictionary_itself=

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		if loggedinanon.username.username == user_anon.username.username:
			users_word = users_dic.words.filter(the_word_itself=word).first()
			if users_word: # first?
				users_att = users_word.attributes.filter(attribute__id=int(attr)).first()
				if users_att:
					users_syn = users_att.homonyms.filter(homonym__id=int(syn)).first()
					if users_syn:
						users_att.remove(users_syn)
						Synonym.objects.get(homonym__id=int(syn)).delete()


	return redirect('Bable:tob_users_dic_word_attribute', user=user, dictionary=dic, word=word)


def delete_own_attr_ant(request, user, dic, word, attr, ant):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.filter(the_dictionary_itself=dic).first() # or the_dictionary_itself=

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		if loggedinanon.username.username == user_anon.username.username:
			users_word = users_dic.words.filter(the_word_itself=word).first()
			if users_word: # first?
				users_att = users_word.attributes.filter(attribute__id=int(attr)).first()
				if users_att:
					users_ant = users_att.antonyms.filter(homonym__id=int(ant)).first()
					if users_ant:
						users_att.remove(users_ant)
						Antonym.objects.get(homonym__id=int(ant)).delete()


	return redirect('Bable:tob_users_dic_word_attribute', user=user, dictionary=dic, word=word)


#needs testing
def delete_own_attr_hom(request, user, dic, word, attr, hom):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.filter(the_dictionary_itself=dic).first() # or the_dictionary_itself=

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		if loggedinanon.username.username == user_anon.username.username:
			users_word = users_dic.words.filter(the_word_itself=word).first()
			if users_word: # first?
				users_att = users_word.attributes.filter(attribute__id=int(attr)).first()
				if users_att:
					users_hom = users_att.homonyms.filter(homonym__id=int(hom)).first()
					if users_hom:
						users_att.remove(users_hom)
						Homonym.objects.get(homonym__id=int(hom)).delete()


	return redirect('Bable:tob_users_dic_word_attribute', user=user, dictionary=dic, word=word)

def delete_own_pron(request, user, dic, word, pron):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.filter(the_dictionary_itself=dic).first() # or the_dictionary_itself=

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		if loggedinanon.username.username == user_anon.username.username:
			users_word = users_dic.words.filter(the_word_itself=word).first()
			if users_word: # first?
				users_pron = users_word.pronunciations.get(id=int(pron))
				if users_pron:
					users_word.pronunciations.remove(users_pron)
					IPA_pronunciation.objects.get(id=int(pron)).delete()


	return redirect('Bable:tob_users_dic_word_pronunciations', user=user, dictionary=dic, word=word, pronunciation=0)

def delete_own_simi(request, user, dic, word, simi):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.filter(the_dictionary_itself=dic).first() # or the_dictionary_itself=

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		if loggedinanon.username.username == user_anon.username.username:
			users_word = users_dic.words.filter(the_word_itself=word).first()
			if users_word: # first?
				users_simi = users_word.similarities.get(id=int(simi))
				if users_simi:
					users_word.similarities.remove(users_simi)
					Simulacrum.objects.get(id=int(simi)).delete()

	request.COOKIES['similarity'] = 0
	return base_redirect(request, 0)

def delete_own_conn(request, user, dic, word, simi, conn):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.filter(the_dictionary_itself=dic).first() # or the_dictionary_itself=

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		if loggedinanon.username.username == user_anon.username.username:
			users_word = users_dic.words.filter(the_word_itself=word).first()
			if users_word: # first?
				users_simi = users_word.similarities.get(id=int(simi))
				if users_simi:
					users_conn = users_simi.connexion.get(id=int(conn))
					if users_conn:
						users_simi.connexia.remove(users_conn)
						Connexion.objects.get(id=int(conn)).delete()

	request.COOKIES['similarity'] = 0
	return base_redirect(request, 0)

def delete_own_trans(request, user, dic, word, trans):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.filter(the_dictionary_itself=dic).first() # or the_dictionary_itself=

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		if loggedinanon.username.username == user_anon.username.username:
			users_word = users_dic.words.filter(the_word_itself=word).first()
			if users_word: # first?
				users_tran = users_word.translations.get(id=int(trans))
				if users_tran:
					users_word.translations.remove(users_tran)
					Translation.objects.get(id=int(tran)).delete()


	return redirect('Bable:tob_users_dic_word_tranlsation', user=user, dictionary=dic, word=word, translation=0)


def delete_own_exam(request, user, dic, word, exam):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.filter(the_dictionary_itself=dic).first() # or the_dictionary_itself=

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		if loggedinanon.username.username == user_anon.username.username:
			users_word = users_dic.words.filter(the_word_itself=word).first()
			if users_word: # first?
				users_exam = users_word.examples.get(id=int(exam))
				if users_exam:
					users_word.examples.remove(users_exam)
					Example.objects.get(id=int(exam)).delete()


	return redirect('Bable:tob_users_dic_word_example', user=user, dictionary=dic, word=word, example=0)

def save_own_exa(request, user, exa):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		if request.user.username == user_anon.username.username:
			users_exam = Example.objects.get(id=int(exa))
			if users_exam.author.username == user:
				if users_exam:
					if users_exam in loggedinanon.examples.all():
						loggedinanon.examples.remove(users_exam)
					else:
						loggedinanon.examples.add(users_exam)

	return redirect('Bable:tob_users_examples', user=user, count=0)


def delete_own_stor(request, user, dic, word, stor):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.filter(the_dictionary_itself=dic).first() # or the_dictionary_itself=

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		if loggedinanon.username.username == user_anon.username.username:
			users_word = users_dic.words.filter(the_word_itself=word).first()
			if users_word: # first?
				users_stor = users_word.stories.get(id=int(stor))
				if users_stor:
					users_word.stories.remove(users_stor)
					Story.objects.get(id=int(stor)).delete()


	return redirect('Bable:tob_users_dic_word_story', user=user, dictionary=dic, word=word, story=0)

def delete_own_rela(request, user, dic, word, rela):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.filter(the_dictionary_itself=dic).first() # or the_dictionary_itself=

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		if loggedinanon.username.username == user_anon.username.username:
			users_word = users_dic.words.filter(the_word_itself=word).first()
			if users_word: # first?
				users_rela = users_word.relations.get(id=int(rela))
				if users_rela:
					users_word.relations.remove(users_rela)
					Relation.objects.get(id=int(rela)).delete()


	return redirect('Bable:tob_users_dic_word_relations', user=user, dictionary=dic, word=word, relation=0)

def delete_own_spon(request, user, dic, word, spon):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.filter(the_dictionary_itself=dic).first() # or the_dictionary_itself=

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		if loggedinanon.username.username == user_anon.username.username:
			users_word = users_dic.words.filter(the_word_itself=word).first()
			if users_word: # first?
				users_spon = users_word.sponsors.get(id=int(spon))
				if users_spon:
					users_word.sponsors.remove(users_spon)
					Sponsor.objects.get(id=int(spon)).delete()


	return redirect('Bable:tob_users_dic_word_sponsor', user=user, dictionary=dic, word=word, sponsor=0)

def delete_own_spons(request, spon):
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		if Sponsor.objects.get(id=int(spon)):
			if Sponsor.objects.get(id=int(spon)).author.username == request.user.username:
				Sponsor.objects.get(id=int(spon)).delete()


	return base_redirect(request, 0)


def delete_own_spac(request, user, dic, word, spac):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.filter(the_dictionary_itself=dic).first() # or the_dictionary_itself=

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		if loggedinanon.username.username == user_anon.username.username:
			users_word = users_dic.words.filter(the_word_itself=word).first()
			if users_word: # first?
				users_spac = users_word.spaces.get(id=int(spac))
				if users_spac:
					users_word.spaces.remove(users_spac)
					Space.objects.get(id=int(spac)).delete()


	return redirect('Bable:tob_users_dic_word_space', user=user, dictionary=dic, word=word, space=0)

def delete_own_post(request, user, post):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_post = Post.objects.get(id=post) # or the_dictionary_itself=

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		if loggedinanon.username.username == user_anon.username.username:
			if users_post:
				users_post.delete()
				if loggedinanon.sum_posts:
					loggedinanon.sum_posts -= 1


	return redirect('Bable:tob_user_view_count', user=user, count=0)

def delete_own_space(request, user, space):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_space = Space.objects.get(id=post) # or the_dictionary_itself=


	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		if loggedinanon.username.username == user_anon.username.username:
			if users_space:
				users_space.to_source().delete()
				users_space.delete()


	return redirect('Bable:tob_user_view_count', user=user, count=0)

def delete_own_votestyle(request, voteid):
	users_votestyle = Votes.objects.get(id=int(voteid)) # or the_dictionary_itself=


	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		if loggedinanon.username.username == users_votestyle.author.username:
			users_votestyle.delete()
		else:
			return HttpResponse('not your votestyle')


	return base_redirect(request, 0)

def base_redirect(request, error):
	if request.COOKIES['current'] == ('tob_view_users' or 'tower_of_bable' or 'tob_dics' or 'word_attributess' or 'mutawords' or 'complementary_scholar') :
		response = redirect("Bable:"+request.COOKIES['current'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tower_of_bable_count' or 'tob_view_spaces' or 'tob_view_users'):
		response = redirect("Bable:"+request.COOKIES['current'], count=request.COOKIES['count'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == 'tob_space_view_count':
		response = redirect("Bable:"+request.COOKIES['current'], space=request.COOKIES['space'], count=request.COOKIES['count'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == 'tob_spaces_post':
		response = redirect("Bable:"+request.COOKIES['current'], space=request.COOKIES['space'], post=request.COOKIES['post'], count=request.COOKIES['count'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == 'tob_spaces_post':
		response = redirect("Bable:"+request.COOKIES['current'], space=request.COOKIES['space'], post=request.COOKIES['post'], comment=request.COOKIES['comment'], count=request.COOKIES['count'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_user_view_count' or 'tob_users_spaces' or 'tob_users_posts' or 'tob_users_examples' or 'tob_users_dics'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], count=request.COOKIES['count'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_space'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], space_id=request.COOKIES['space_id'], count=request.COOKIES['count'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_sponsor'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], sponsor=request.COOKIES['sponsor'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_sponsors'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], count=request.COOKIES['count'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_spaces_sponsor'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], space_id=request.COOKIES['space_id'], sponsor=request.COOKIES['sponsor'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_spaces_post'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], space=request.COOKIES['space'], post=request.COOKIES['post'], count=request.COOKIES['count'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_spaces_post_comment'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], space=request.COOKIES['space'], post=request.COOKIES['post'], comment=request.COOKIES['comment'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_votes'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], votes=request.COOKIES['votes'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_post'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], post=request.COOKIES['post'], count=request.COOKIES['count'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_posts_comment'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], post=request.COOKIES['post'], comment=request.COOKIES['comment'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_dic'):
		count = 0
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], dictionary=request.COOKIES['dictionary'], count=count)
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_dics'):
		count = 0
		response = redirect("Bable:"+request.COOKIES['current'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_dic_word_count'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], dictionary=request.COOKIES['dictionary'], word=request.COOKIES['word'], count=request.COOKIES['count'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_dic_word_pronunciation'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], dictionary=request.COOKIES['dictionary'], word=request.COOKIES['word'], pronunciation=request.COOKIES['pronunciation'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_dic_word_attribute'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], dictionary=request.COOKIES['dictionary'], word=request.COOKIES['word'], attribute=request.COOKIES['attribute'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_dic_word_similarity'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], dictionary=request.COOKIES['dictionary'], word=request.COOKIES['word'], similarity=request.COOKIES['similarity'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_dic_word_translation'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], dictionary=request.COOKIES['dictionary'], word=request.COOKIES['word'], translation=request.COOKIES['translation'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_dic_word_example'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], dictionary=request.COOKIES['dictionary'], word=request.COOKIES['word'], example=request.COOKIES['example'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_dic_word_story'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], dictionary=request.COOKIES['dictionary'], word=request.COOKIES['word'], story=request.COOKIES['story'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_dic_word_relation'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], dictionary=request.COOKIES['dictionary'], word=request.COOKIES['word'], relation=request.COOKIES['relation'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_dic_word_sponsor'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], dictionary=request.COOKIES['dictionary'], word=request.COOKIES['word'], sponsor=request.COOKIES['sponsor'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == ('tob_users_dic_word_space'):
		response = redirect("Bable:"+request.COOKIES['current'], user=request.COOKIES['viewing_user'], dictionary=request.COOKIES['dictionary'], word=request.COOKIES['word'], space=request.COOKIES['space'])
		response.set_cookie('error', error)
		return response
	elif request.COOKIES['current'] == 'tob_dic':
		response = redirect("Bable:"+'tob_users_dic', user=request.COOKIES['user'], dictionary=request.COOKIES['dictionary'], count=request.COOKIES['count'])
		response.set_cookie('error', error)
		return response
	return redirect('Bable:tower_of_bable')

def sign_wallet(request):
	data = requests.get("http://"+request.META['HTTP_HOST']+"/metamask/"+request.user.username)
	print(data)
	return redirect('Bable:tower_of_bable')


# Redirects to index
def logout_user(request):
	user = request.user
	logout(request)
	return redirect('Bable:tower_of_bable')

def login_view(request):
	loginform = AuthenticationForm(data=request.POST)
	if loginform.is_valid():
		user = loginform.get_user()
		login(request, user)
		#requests.post("http://"+request.META['HTTP_HOST']+"/metamask/", data={'user': {'username': user.username}, 'public_address': user.username})
	

	### Input redirect to previous page.

	return redirect('Bable:tower_of_bable')

from django.contrib.auth import authenticate

# Needs to be AJAX with Rails-style Flash Messages
def register_view(request):
	loginform = AuthenticationForm()
	login_error = "Try getting it right."
	register_error = "Don't fuck it up."
	registerform = UserCreationForm(request.POST)
	
		
	

	if registerform.is_valid():
		new_user = registerform.save()
		register_error = "Register Successful."
		#must log in after
		user = authenticate(request, username=new_user.username, password=registerform.cleaned_data['password1'])
		if user is not None:
			login(request, user)
			Anon.objects.create(username=User.objects.get(username=new_user.username))
			Author.objects.create(username=new_user.username)
			# Send email.
			# Record IP, record username, record email, record time.
		else:
			login_error = "Not a known Combo, try using a PS4 controller."
	else:
		register_error = "Couldn't register that."
	
	posts_by_viewcount = Post.objects.order_by('viewcount')[:100]
	count = 0
	count100 = 100
	mcount = 0
	page_views, created = Pageviews.objects.get_or_create(page="tower_of_bable")
	page_views.views += 1
	page_views.save()
	total = 0

	base_product, created = Price.objects.get_or_create(id=1)
	if created:
		base_product.name = "Donate - Predictionary.us"
		base_product.stripe_price_id = "price_1Nf8jMIDEcA7LIBjpnt385yZ"
		base_product.anon_user_id = 1
		base_product.stripe_product_id = "prod_OS2pk9gZWam5Ye"
		base_product.price = 500
		base_product.save()
		
	for page in Pageviews.objects.all():
		total += page.views
	the_response = render(request, 'tower_of_bable.html', {"basic_price": base_product, "viewsponsor": viewsponsor, "register_error":register_error, "login_error":login_error, "total": total, "count": count, "mcount": mcount, "count100": count100, "posts": posts_by_viewcount, 'loginform': loginform, 'registerform': registerform, })
	
	the_response.set_cookie('current', 'tower_of_bable')
	return base_redirect(request, 0)

def owner(request):
	#recently_modified_post = Post.objects.order_by('-latest_change_date')[:100]
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	
	dic_form = DictionaryForm()
	post_form = PostForm(request)
	space_form = SpaceForm(request)
	task_form = TaskForm()
	word_form = WordForm(request)

	if request.user.is_authenticated:
		loggedinanon = Anon.objects.get(username=User.ojects.get(username=request.user.username))

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		return render(request, 'jackdonmclovin.html', {"loggedinanon": loggedinanon, 'loginform': loginform, 'registerform': registerform,  'registerterms': registerterms, 'word_form': word_form, 'dic_form':dic_form, 'space_form': space_form, "post_form": post_form, 'task_form': task_form})

	return render(request, 'jackdonmclovin.html', {'loginform': loginform, 'registerform': registerform,  'registerterms': registerterms, 'word_form': word_form, 'dic_form':dic_form, 'space_form': space_form, "post_form": post_form, 'task_form': task_form})





def feedback(request):
	# https://stackoverflow.com/questions/31324005/django-1-8-sending-mail-using-gmail-smtp
	# email = EmailMessage('title', 'body', from_email=[], to=[jackdonmclovin@gmail.com])
	# email.send()
	#recently_modified_post = Post.objects.order_by('-latest_change_date')[:100]
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	
	
	contact_form = ContactForm()

	if request.user.is_authenticated:
		loggedinanon = Anon.objects.get(username=User.objects.get(username=request.user.username))
		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		return render(request, 'feedback.html', {"loggedinanon": loggedinanon, 'contact_form':contact_form, 'loginform': loginform, 'registerform': registerform, 'word_form': word_form, 'dic_form':dic_form, 'space_form': space_form, "post_form": post_form, 'task_form': task_form})

	return render(request, 'feedback.html', {'contact_form':contact_form, 'loginform': loginform, 'registerform': registerform})


def create_feedback(request):
	contactform = ContactForm(request.POST)
	if contactform.is_valid():
		from_email = contactform.cleaned_data['from_email']
		title = contactform.cleaned_data['title']
		message = contactform.cleaned_data['message']
		
		# uncomment if interested in the actual smtp conversation
		# s.set_debuglevel(1)
		# do the smtp auth; sends ehlo if it hasn't been sent already
		
		email = EmailMessage(title+' from: '+from_email, message + "BablyonPolice.com", to=['jackdonmclovin@gmail.com'])
		email.send()
		return redirect('Bable:thanks')
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()

	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		
		return render(request, 'feedback.html', {'loginform': loginform, 'registerform': registerform, 'word_form': word_form, 'dic_form':dic_form, 'space_form': space_form, "post_form": post_form, 'task_form': task_form})
	return render(request, 'feedback.html', {'loginform': loginform, 'registerform': registerform})


def thanks(request):
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	
	
	if request.user.is_authenticated:
		loggedinanon = Anon.objects.get(username=User.objects.get(username=request.user.username))


		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		return render(request, 'thanks.html', {"loggedinanon": loggedinanon, 'loginform': loginform, 'registerform': registerform,  'registerterms': registerterms, 'word_form': word_form, 'dic_form':dic_form, 'space_form': space_form, "post_form": post_form, 'task_form': task_form})

	return render(request, 'thanks.html', {'loginform': loginform, 'registerform': registerform,  'registerterms': registerterms, 'word_form': word_form, 'dic_form':dic_form, 'space_form': space_form, "post_form": post_form, 'task_form': task_form})


def about(request):
	#recently_modified_post = Post.objects.order_by('-latest_change_date')[:100]
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	
	

	if request.user.is_authenticated:
		loggedinanon = Anon.objects.get(username=User.objects.get(username=request.user.username))

		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		return render(request, 'about.html', {"loggedinanon": loggedinanon, 'loginform': loginform, 'registerform': registerform, 'word_form': word_form, 'dic_form':dic_form, 'space_form': space_form, "post_form": post_form, 'task_form': task_form})


	return render(request, 'about.html', {'loginform': loginform, 'registerform': registerform})


def management(request):
	#recently_modified_post = Post.objects.order_by('-latest_change_date')[:100]
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	
	

	if request.user.is_authenticated:
		loggedinanon = Anon.objects.get(username=User.objects.get(username=request.user.username))

		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		return render(request, 'management.html', {"loggedinanon": loggedinanon, 'loginform': loginform, 'registerform': registerform, 'word_form': word_form, 'dic_form':dic_form, 'space_form': space_form, "post_form": post_form, 'task_form': task_form})


	return render(request, 'management.html', {'loginform': loginform, 'registerform': registerform})




@login_required
def create_post(request):
	loggedinanon = Anon.objects.get(username=request.user)
	loggedinauthor = Author.objects.get(username=request.user.username)
	post_form = PostForm(request, data=request.POST)
	if post_form.is_valid():
		if Post.objects.filter(spaces__the_space_itself__the_word_itself=[(e,e) for e in post_form.cleaned_data['spaces']], author=loggedinauthor, title=post_form.cleaned_data['title'], dictionaries__the_dictionary_itself=[(e, e) for e in post_form.cleaned_data['dictionaries']]).count():
			return base_redirect(request, 'duplicate post')
		else:
			if post_form.cleaned_data['url2']:
				if post_form.cleaned_data['img']:
					new_post = Post.objects.create(author=loggedinauthor, title=post_form.cleaned_data['title'], url2=post_form.cleaned_data['url2'], body=post_form.cleaned_data['body'], img=post_form.cleaned_data['img'])
				else:
					new_post = Post.objects.create(author=loggedinauthor, title=post_form.cleaned_data['title'], url2=post_form.cleaned_data['url2'], body=post_form.cleaned_data['body'])
			else:
				new_post = Post.objects.create(author=loggedinauthor, title=post_form.cleaned_data['title'], body=post_form.cleaned_data['body'])
			for word in post_form.cleaned_data['spaces']:
				wordle = Word.objects.get(the_word_itself=word, dictionary__purchased_dictionaries=loggedinanon, spaces__the_space_itself__the_word_itself=word)
				space = SpaceSource.objects.filter(the_space_itself=wordle.to_source(), allowed_to_view_authors=loggedinauthor).first()
				if space:
					new_post.spaces.add(space)
			new_post.sum_spaces = new_post.spaces.count()
			pre_body = post_form.cleaned_data['body']
			exclude = ''
			for dic in post_form.cleaned_data['dictionaries']:
				diction = Dictionary.objects.get(purchased_dictionaries=loggedinanon, the_dictionary_itself=dic)
				new_post.dictionaries.add(diction)
				for word in diction.words.all():
					if word.sponsors.count():
						for sponsor in word.sponsors.all():
							new_post.sponsors.add(sponsor)
					if word.the_word_itself in pre_body:
						if word.the_word_itself not in exclude:
							new_post.words.add(word)
							exclude += word.the_word_itself
			new_post.sum_dictionaries = new_post.dictionaries.count()
			new_post.sum_words = new_post.words.count()
			new_post.cc = post_form.cleaned_data['cc']
			new_post.save()
			loggedinanon.posts.add(new_post)
			loggedinanon.save()
			for space in post_form.cleaned_data['spaces']:
				spa = Space.objects.get(the_space_itself__the_word_itself=space, approved_voters=loggedinauthor)
				spa.posts.add(new_post)
				spa.postcount += 1
				spa.save()
				for spon in spa.sponsors.all():
					new_post.sponsors.add(spon)
				if not new_post.public:
					new_post.public = spa.public
				spa.save()
			new_post.save()
			loggedinanon.sum_posts += 1
			loggedinanon.save()
			return redirect('Bable:tob_users_post', user=request.user.username, post=new_post.id, count=0)
	else:
		return HttpResponse(post_form.errors)
	return redirect('Bable:tob_users_posts', user=request.user.username, count=0)


@login_required
def edit_post(request, post_id):
	loggedinanon = Anon.objects.get(username=request.user)
	loggedinauthor = Author.objects.get(username=request.user.username)
	post_form = PostForm(request, data=request.POST)
	new_post = Post.objects.get(id=post_id)
	if new_post.author.username == loggedinauthor.username:
		if post_form.is_valid():
			for word in post_form.cleaned_data['spaces']:
				wordle = Word.objects.get(the_word_itself=word, dictionary__purchased_dictionaries=loggedinanon, spaces__the_space_itself__the_word_itself=word)
				space = SpaceSource.objects.filter(the_space_itself=wordle.to_source(), allowed_to_view_authors=loggedinauthor).first()
				new_post.spaces.add(space)
			pre_body = post_form.cleaned_data['body']
			new_post.title = post_form.cleaned_data['title']
			new_post.body = pre_body
			exclude = ''
			for dic in post_form.cleaned_data['dictionaries']:
				diction = Dictionary.objects.get(purchased_dictionaries=loggedinanon, the_dictionary_itself=dic)
				new_post.dictionaries.add(diction)
				for word in diction.words.all():
					if word.sponsors.count():
						for sponsor in word.sponsors.all():
							new_post.sponsors.add(sponsor)
					if word.the_word_itself in pre_body:
						if word.the_word_itself not in exclude:
							new_post.words.add(word)
							exclude += word.the_word_itself
			new_post.cc = post_form.cleaned_data['cc']
			for space in post_form.cleaned_data['spaces']:
				spa = Space.objects.get(the_space_itself__the_word_itself=space, approved_voters=loggedinauthor)
				spa.posts.add(new_post)
				for spon in spa.sponsors.all():
					new_post.sponsors.add(spon)
				if not new_post.public:
					new_post.public = spa.public
				spa.save()
			new_post.save()
			loggedinanon.save()
			return redirect('Bable:tob_users_post', user=request.user.username, post=new_post.id, count=0)
	return redirect('Bable:tob_users_posts', user=request.user.username, count=0)


@login_required
def edit_spaces_post(request, space_id, post_id):
	loggedinanon = Anon.objects.get(username=request.user)
	loggedinauthor = Author.objects.get(username=request.user.username)
	post_form = PostForm(request, data=request.POST)
	new_post = Post.objects.get(id=int(post_id))
	space = Space.objects.get(id=int(space_id))
	if request.user.username == loggedinauthor.username or request.user.username in space.approved_voters.values_list('username', flat=True):
		if post_form.is_valid():
			for word in post_form.cleaned_data['spaces']:
				wordle = Word.objects.get(the_word_itself=word, dictionary__purchased_dictionaries=loggedinanon, spaces__the_space_itself__the_word_itself=word)
				space = SpaceSource.objects.get(the_space_itself=wordle.to_source(), allowed_to_view_authors=loggedinauthor)
				new_post.spaces.add(space)
			pre_body = post_form.cleaned_data['body']
			new_post.title = post_form.cleaned_data['title']
			new_post.edits.add(Edit.objects.create(body=pre_body, author=Author.objects.get(username=request.user.username)))
			exclude = ''
			for dic in post_form.cleaned_data['dictionaries']:
				diction = Dictionary.objects.get(purchased_dictionaries=loggedinanon, the_dictionary_itself=dic)
				new_post.dictionaries.add(diction)
				for word in diction.words.all():
					if word.sponsors.count():
						for sponsor in word.sponsors.all():
							new_post.sponsors.add(sponsor)
					if word.the_word_itself in pre_body:
						if word.the_word_itself not in exclude:
							new_post.words.add(word)
							exclude += word.the_word_itself
			new_post.cc = post_form.cleaned_data['cc']
			new_post.save()
			loggedinanon.save()
			return redirect('Bable:tob_users_post', user=request.user.username, post=new_post.id, count=0)
	return redirect('Bable:tob_users_posts', user=request.user.username, count=0)




@login_required
def create_wordgroup():
	return base_redirect(request, 0)


@login_required
def create_translation():
	return base_redirect(request, 0)


@login_required
def create_sentence():
	return base_redirect(request, 0)


@login_required
def create_rendition():
	return base_redirect(request, 0)


@login_required
def create_analysis():
	return base_redirect(request, 0)

@login_required
def create_story():
	return base_redirect(request, 0)

@login_required
def create_pronunciations():
	return base_redirect(request, 0)


@login_required
def create_comment(request, source_type, source, com):
	loggedinanon = Anon.objects.get(username=request.user)
	loggedinauthor = Author.objects.get(username=request.user.username)
	commentform = Comment_SourceForm(request, data=request.POST)
	source = int(source)
	com = int(com)
	new_com = 0
	if source_type == 'post':
		commentform = CommentForm(request, data=request.POST)
		if commentform.is_valid():
			if com == 0:
				if commentform.cleaned_data['dictionaries'] == 0:
					new_com = Comment.objects.create(body=commentform.cleaned_data['body'], author=loggedinauthor)
				else:
					new_com = Comment.objects.create(body=commentform.cleaned_data['body'], author=loggedinauthor)
					for dic in commentform.cleaned_data['dictionaries']:
						new_com.dictionaries.add(loggedinanon.purchased_dictionaries.get(the_dictionary_itself=dic))
					new_com.sum_dictionaries = new_com.dictionaries.count()
					new_com.save()
			else:
				if commentform.cleaned_data['dictionaries'] == 0:
					parent_comment = Comment.objects.get(id=com)
					parent_comment.children_count += 1
					parent_comment.save()
					new_com = Comment.objects.create(body=commentform.cleaned_data['body'], author=loggedinauthor, parent=Comment.objects.get(id=com))
				else:
					parent_comment = Comment.objects.get(id=com)
					parent_comment.children_count += 1
					parent_comment.save()
					new_com = Comment.objects.create(body=commentform.cleaned_data['body'], author=loggedinauthor, parent=Comment.objects.get(id=com))
					for dic in commentform.cleaned_data['dictionaries']:
						new_com.dictionaries.add(loggedinanon.purchased_dictionaries.get(the_dictionary_itself=dic))
					new_com.sum_dictionaries = new_com.dictionaries.count()
					new_com.save()
			the_post = Post.objects.get(id=source)
			the_post.comments.add(new_com)
			the_post.sum_comments = the_post.comments.count()
			the_post.under_talked = float(the_post.votes_uniques) / float(the_post.sum_comments)
			the_post.save()

					

	if commentform.is_valid():
		if com == 0:
			if commentform.cleaned_data['dictionaries'] == 0:
				if new_com:
					new_com = Comment_Source.objects.create(body=commentform.cleaned_data['body'], author=loggedinauthor, original=new_com.id)
				else:
					new_com = Comment_Source.objects.create(body=commentform.cleaned_data['body'], author=loggedinauthor, original=new_com.id)

			else:
				if com:
					parent_comment = Comment.objects.get(id=com)
					parent_comment.children_count += 1
					parent_comment.save()
					new_com = Comment_Source.objects.create(body=commentform.cleaned_data['body'], author=loggedinauthor, original=com)
				else:
					new_com = Comment_Source.objects.create(body=commentform.cleaned_data['body'], author=loggedinauthor)
		else:
			if commentform.cleaned_data['dictionaries'] == 0:
				if com:
					parent_comment = Comment.objects.get(id=com)
					parent_comment.children_count += 1
					parent_comment.save()
					new_com = Comment_Source.objects.create(body=commentform.cleaned_data['body'], author=loggedinauthor, original=com)
				else:
					new_com = Comment_Source.objects.create(body=commentform.cleaned_data['body'], author=loggedinauthor, parent=Comment_Source.objects.get(id=com))
			else:
				if com:
					parent_comment = Comment.objects.get(id=com)
					parent_comment.children_count += 1
					parent_comment.save()
					new_com = Comment_Source.objects.create(body=commentform.cleaned_data['body'], author=loggedinauthor, original=com)
				else:
					new_com = Comment_Source.objects.create(body=commentform.cleaned_data['body'], author=loggedinauthor, parent=Comment_Source.objects.get(id=com))
			comments_dic = Dictionary_Source.objects.get(the_dictionary_itself=commentform.cleaned_data['dictionaries'], author=loggedinauthor)
			new_com.dictionaries.add(comments_dic)
			print(new_com)
		if source_type == 'att_def':
			if Definition.objects.get(id=source):
				Definition.objects.get(id=source).comment_sources.add(new_com)
			print(Definition.objects.get(id=source).the_definition_itself)
		if source_type == 'syn':
			if Synonym.objects.get(id=source):
				Synonym.objects.get(id=source).comment_sources.add(new_com)
		if source_type == 'ant':
			if Antonym.objects.get(id=source):
				Antonym.objects.get(id=source).comment_sources.add(new_com)
		if source_type == 'hom':
			if Homonym.objects.get(id=source):
				Homonym.objects.get(id=source).comment_sources.add(new_com)
		if source_type == 'examp':
			if Example.objects.get(id=source):
				Example.objects.get(id=source).comment_sources.add(new_com)
		if source_type == 'simi':
			if Simulacrum.objects.get(id=source):
				Simulacrum.objects.get(id=source).comment_sources.add(new_com)
		if source_type == 'simiconn':
			if Connexion.objects.get(id=source):
				Connexion.objects.get(id=source).comment_sources.add(new_com)
		if source_type == 'tran':
			if Translation.objects.get(id=source):
				Translation.objects.get(id=source).comment_sources.add(new_com)
		if source_type == 'stor':
			if Story.objects.get(id=source):
				Story.objects.get(id=source).comment_sources.add(new_com)
		if source_type == 'rela':
			if Relation.objects.get(id=source):
				Relation.objects.get(id=source).comment_sources.add(new_com)
		if source_type == 'msg':
			if Anon.objects.get(id=source):
				Anon.objects.get(id=source).received_messages.add(new_com)
				Anon.objects.get(username__username=request.user.username).sent_messages.add(new_com)
	else:
		print(commentform.errors)
	
	return base_redirect(request, 0)


@login_required
def create_message(request):
	loggedinanon = Anon.objects.get(username=request.user)
	loggedinauthor = Author.objects.get(username=request.user.username)
	message_form = MessageForm(request.POST)
	if message_form.is_valid():
		new_message = Message.objects.create(sender=loggedinauthor, receiver=message_form.cleaned_data['receiver'])

	else:
		print(message_form.errors)
	
	return base_redirect(request, 0)




@login_required
def create_comment_thread(request, source_type, source, com):
	loggedinanon = Anon.objects.get(username=request.user)
	loggedinauthor = Author.objects.get(username=request.user.username)
	commentform = Comment_SourceForm(request, data=request.POST)
	source = int(source)
	com = int(com)
	if commentform.is_valid():
		identifier = commentform.cleaned_data['id']
		if com == 0:
			if identifier == 0:
				return base_redirect(request, 0)
			else:
				old_com = Comment_Source.objects.get(id=identifier)
		else:
			if identifier == 0:
				return base_redirect(request, 0)
			else:
				old_com = Comment_Source.objects.get(id=identifier)
			
		if source_type == 'att_def':
			if Definition.objects.get(id=source):
				Definition.objects.get(id=source).comment_sources.add(old_com)
			print(Definition.objects.get(id=source).the_definition_itself)
		if source_type == 'syn':
			if Synonym.objects.get(id=source):
				Synonym.objects.get(id=source).comment_sources.add(old_com)
		if source_type == 'ant':
			if Antonym.objects.get(id=source):
				Antonym.objects.get(id=source).comment_sources.add(old_com)
		if source_type == 'hom':
			if Homonym.objects.get(id=source):
				Homonym.objects.get(id=source).comment_sources.add(old_com)
		if source_type == 'exa':
			if Example.objects.get(id=source):
				Example.objects.get(id=source).comment_sources.add(old_com)
		if source_type == 'simi':
			if Simulacrum.objects.get(id=source):
				Simulacrum.objects.get(id=source).comment_sources.add(old_com)
		if source_type == 'simiconn':
			if Connexion.objects.get(id=source):
				Connexion.objects.get(id=source).comment_sources.add(old_com)
		if source_type == 'tran':
			if Translation.objects.get(id=source):
				Translation.objects.get(id=source).comment_sources.add(old_com)
		if source_type == 'stor':
			if Story.objects.get(id=source):
				Story.objects.get(id=source).comment_sources.add(old_com)
		if source_type == 'rela':
			if Relation.objects.get(id=source):
				Relation.objects.get(id=source).comment_sources.add(old_com)
	else:
		print(commentform.errors)
	
	return base_redirect(request, 0)

from coinbase_commerce.client import Client

@login_required
def buy_users_dic(request, user, dictionary):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	if user_anon.dictionaries.filter(the_dictionary_itself=dictionary).first():
		users_dic = user_anon.dictionaries.filter(the_dictionary_itself=dictionary).first() # or the_dictionary_itself=
	else:
		return HttpResponse("They aren't the author of that.")
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		# wallet function... could become crypto/blockchain, but it is infeasible.
		# if users_dic.author.to_anon().monero_wallet:

		if loggedinanon.false_wallet > users_dic.entry_fee:
			if users_dic.prerequisite_dics:
				for dic in users_dic.prerequisite_dics:
					if dic in loggedinanon.purchased_dictionaries:
						loggedinanon.false_wallet = loggedinanon.false_wallet - users_dic.entry_fee
						user_anon.false_wallet = user_anon.false_wallet + users_dic.entry_fee
						loggedinanon.purchased_dictionaries.add(users_dic)
						loggedinanon.sum_purchased_dictionaries += 1
						users_dic.purchase_orders.add(Purchase_Order.objects.create(author=loggedinauthor))
						users_dic.traded_date = timezone.now
						users_dic.save()
						
					else:
						return HttpResponse("Obtain prerequisites first.")
			else:
				loggedinanon.purchased_dictionaries.add(users_dic)
				loggedinanon.sum_purchased_dictionaries += 1
				loggedinanon.false_wallet = loggedinanon.false_wallet - users_dic.entry_fee
				user_anon.false_wallet = user_anon.false_wallet + users_dic.entry_fee
				users_dic.purchase_orders.add(Purchase_Order.objects.create(author=loggedinauthor))
				users_dic.traded_date = timezone.now
				users_dic.save()
			
		else:
			return HttpResponse("Insufficient balance.")

		loggedinanon.save()
	else:
		return HttpResponse("Oi, you're not logged in.")

	return redirect('Bable:tob_users_dic', user=user_anon.username.username, dictionary=users_dic.the_dictionary_itself)

@login_required
def unpurchase_users_dic(request, user, dictionary):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	if user_anon.dictionaries.filter(the_dictionary_itself=dictionary).first():
		users_dic = user_anon.dictionaries.filter(the_dictionary_itself=dictionary).first() # or the_dictionary_itself=
	else:
		return HttpResponse("They aren't the author of that.")
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		# wallet function... could become crypto/blockchain, but it is infeasible.
		loggedinanon.purchased_dictionaries.remove(users_dic)
		loggedinanon.sum_purchased_dictionaries -= 1
		loggedinanon.save()
	else:
		return HttpResponse("Oi, you're not logged in.")

	return redirect('Bable:tob_users_dic', user=user_anon.username.username, dictionary=users_dic.the_dictionary_itself)




@login_required
def vote(request, vote):
	user_anon = Anon.objects.get(username=request.user)
	user_author = Author.objects.get(username=request.user.username)
	vote = int(vote)
	if Votes.objects.get(id=vote):
		the_vote = Votes.objects.get(id=vote)
		if user_author in the_vote.voters.all():
			the_vote.voters.remove(user_author)
			the_vote.votes -= 1
			the_vote.save()
		else:
			the_vote.voters.add(user_author)
			the_vote.votes += 1
			the_vote.save()
	return base_redirect(request, 0)

@login_required
def votewvotestyle(request, source_type, source_id):
	user_anon = Anon.objects.get(username=request.user)
	user_author = Author.objects.get(username=request.user.username)
	source_id = int(source_id)
	if source_type == 'anal':
		if Analysis.objects.get(id=source_id):
			source_obj = Analysis.objects.get(id=source_id)
			for vote in user_anon.applied_votestyles.all():
				if vote in source_obj.votes.all():
					voters = vote.voters.all()
					if user_author in voters:
						vote.voters.remove(user_author)
						vote.votes -= 1
						vote.save()
					else:
						vote.voters.add(user_author)
						vote.votes += 1
						vote.save()
						voted = True
				else:
					source_obj.votes.add(vote)
					vote.voters.add(user_author)
					vote.votes += 1
					vote.save()
					voted = True
			if user_author in source_obj.has_voted.all():
				if not voted:
					source_obj.has_voted.remove(user_author)
			source_obj.save()

	if source_type == 'search':
		if SearchURL.objects.get(id=source_id):
			source_obj = SearchURL.objects.get(id=source_id)
			for vote in user_anon.applied_votestyles.all():
				if vote in source_obj.votes.all():
					voters = vote.voters.all()
					if user_author in voters:
						vote.voters.remove(user_author)
						vote.votes -= 1
						vote.save()
					else:
						vote.voters.add(user_author)
						vote.votes += 1
						vote.save()
						voted = True
				else:
					source_obj.votes.add(vote)
					vote.voters.add(user_author)
					vote.votes += 1
					vote.save()
					voted = True
			if user_author in source_obj.has_voted.all():
				if not voted:
					source_obj.has_voted.remove(user_author)
			source_obj.save()

	if source_type == 'def':
		if Definition.objects.get(id=source_id):
			# either to_source first or after all
			source_obj = Definition.objects.get(id=source_id)
			for vote in user_anon.applied_votestyles.all():
				if vote in source_obj.votes.all():
					voters = vote.voters.all()
					if user_author in voters:
						vote.voters.remove(user_author)
						vote.votes -= 1
						vote.save()
					else:
						vote.voters.add(user_author)
						vote.votes += 1
						vote.save()
						voted = True
				else:
					source_obj.votes.add(vote)
					vote.voters.add(user_author)
					vote.votes += 1
					vote.save()
					voted = True
			if user_author in source_obj.has_voted.all():
				if not voted:
					source_obj.has_voted.remove(user_author)
			source_obj.save()

	if source_type == 'com':
		if Comment_Source.objects.get(id=source_id):
			source_obj = Comment_Source.objects.get(id=source_id)
			for vote in user_anon.applied_votestyles.all():
				if vote in source_obj.votes.all():
					voters = vote.voters.all()
					if user_author in voters:
						vote.voters.remove(user_author)
						vote.votes -= 1
						vote.save()
					else:
						vote.voters.add(user_author)
						vote.votes += 1
						vote.save()
						voted = True
				else:
					source_obj.votes.add(vote)
					vote.voters.add(user_author)
					vote.votes += 1
					vote.save()
					voted = True
			if user_author in source_obj.has_voted.all():
				if not voted:
					source_obj.has_voted.remove(user_author)
			source_obj.save()
	if source_type == 'exa':
		if Example.objects.get(id=source_id):
			source_obj = Example.objects.get(id=source_id)
			for vote in user_anon.applied_votestyles.all():
				if vote in source_obj.votes.all():
					voters = vote.voters.all()
					if user_author in voters:
						vote.voters.remove(user_author)
						vote.votes -= 1
						vote.save()
					else:
						vote.voters.add(user_author)
						vote.votes += 1
						vote.save()
						voted = True
				else:
					source_obj.votes.add(vote)
					vote.voters.add(user_author)
					vote.votes += 1
					vote.save()
					voted = True
			if user_author in source_obj.has_voted.all():
				if not voted:
					source_obj.has_voted.remove(user_author)
			source_obj.save()

	if source_type == 'conn':
		if Connexion.objects.get(id=source_id):
			source_obj = Connexion.objects.get(id=source_id)
			for vote in user_anon.applied_votestyles.all():
				if vote in source_obj.votes.all():
					voters = vote.voters.all()
					if user_author in voters:
						vote.voters.remove(user_author)
						vote.votes -= 1
						vote.save()
					else:
						vote.voters.add(user_author)
						vote.votes += 1
						vote.save()
						voted = True
				else:
					source_obj.votes.add(vote)
					vote.voters.add(user_author)
					vote.votes += 1
					vote.save()
					voted = True
			if user_author in source_obj.has_voted.all():
				if not voted:
					source_obj.has_voted.remove(user_author)
			source_obj.save()
		
	if source_type == 'simi':
		if Simulacrum.objects.get(id=source_id):
			source_obj = Simulacrum.objects.get(id=source_id)
			for vote in user_anon.applied_votestyles.all():
				if vote in source_obj.votes.all():
					voters = vote.voters.all()
					if user_author in voters:
						vote.voters.remove(user_author)
						vote.votes -= 1
						vote.save()
					else:
						vote.voters.add(user_author)
						vote.votes += 1
						vote.save()
						voted = True
				else:
					source_obj.votes.add(vote)
					vote.voters.add(user_author)
					vote.votes += 1
					vote.save()
					voted = True
			if user_author in source_obj.has_voted.all():
				if not voted:
					source_obj.has_voted.remove(user_author)
			source_obj.save()
		
	if source_type == 'stor':
		if Story.objects.get(id=source_id):
			source_obj = Story.objects.get(id=source_id)
			for vote in user_anon.applied_votestyles.all():
				if vote in source_obj.votes.all():
					voters = vote.voters.all()
					if user_author in voters:
						vote.voters.remove(user_author)
						vote.votes -= 1
						vote.save()
					else:
						vote.voters.add(user_author)
						vote.votes += 1
						vote.save()
						voted = True
				else:
					source_obj.votes.add(vote)
					vote.voters.add(user_author)
					vote.votes += 1
					vote.save()
					voted = True
			if user_author in source_obj.has_voted.all():
				if not voted:
					source_obj.has_voted.remove(user_author)
			source_obj.save()
		
	if source_type == 'rela':
		if Relation.objects.get(id=source_id):
			source_obj = Relation.objects.get(id=source_id)
			for vote in user_anon.applied_votestyles.all():
				if vote in source_obj.votes.all():
					voters = vote.voters.all()
					if user_author in voters:
						vote.voters.remove(user_author)
						vote.votes -= 1
						vote.save()
					else:
						vote.voters.add(user_author)
						vote.votes += 1
						vote.save()
						voted = True
				else:
					source_obj.votes.add(vote)
					vote.voters.add(user_author)
					vote.votes += 1
					vote.save()
					voted = True
			if user_author in source_obj.has_voted.all():
				if not voted:
					source_obj.has_voted.remove(user_author)
			source_obj.save()
		
	if source_type == 'spac':
		if SpaceSource.objects.get(id=source_id):
			source_obj = SpaceSource.objects.get(id=source_id)
			for vote in user_anon.applied_votestyles.all():
				if vote in source_obj.votes.all():
					voters = vote.voters.all()
					if user_author in voters:
						vote.voters.remove(user_author)
						vote.votes -= 1
						vote.save()
					else:
						vote.voters.add(user_author)
						vote.votes += 1
						vote.save()
						voted = True
				else:
					source_obj.votes.add(vote)
					vote.voters.add(user_author)
					vote.votes += 1
					vote.save()
					voted = True
			if user_author in source_obj.has_voted.all():
				if not voted:
					source_obj.has_voted.remove(user_author)
			source_obj.save()
		
	if source_type == 'tran':
		if Translation.objects.get(id=source_id):
			source_obj = Translation.objects.get(id=source_id)
			for vote in user_anon.applied_votestyles.all():
				if vote in source_obj.votes.all():
					voters = vote.voters.all()
					if user_author in voters:
						vote.voters.remove(user_author)
						vote.votes -= 1
						vote.save()
					else:
						vote.voters.add(user_author)
						vote.votes += 1
						vote.save()
						voted = True
				else:
					source_obj.votes.add(vote)
					vote.voters.add(user_author)
					vote.votes += 1
					vote.save()
					voted = True
			if user_author in source_obj.has_voted.all():
				if not voted:
					source_obj.has_voted.remove(user_author)
			source_obj.save()
		
	if source_type == 'spon':
		if Sponsor.objects.get(id=source_id):
			source_obj = Sponsor.objects.get(id=source_id)
			for vote in user_anon.applied_votestyles.all():
				if vote in source_obj.votes.all():
					voters = vote.voters.all()
					if user_author in voters:
						vote.voters.remove(user_author)
						vote.votes -= 1
						vote.save()
					else:
						vote.voters.add(user_author)
						vote.votes += 1
						vote.save()
						voted = True
				else:
					source_obj.votes.add(vote)
					vote.voters.add(user_author)
					vote.votes += 1
					vote.save()
					voted = True
			if user_author in source_obj.has_voted.all():
				if not voted:
					source_obj.has_voted.remove(user_author)
			source_obj.save()
		
	if source_type == 'pron':
		if IPA_pronunciation.objects.get(id=source_id):
			source_obj = IPA_pronunciation.objects.get(id=source_id)
			for vote in user_anon.applied_votestyles.all():
				if vote in source_obj.votes.all():
					voters = vote.voters.all()
					if user_author in voters:
						vote.voters.remove(user_author)
						vote.votes -= 1
						vote.save()
					else:
						vote.voters.add(user_author)
						vote.votes += 1
						vote.save()
						voted = True
				else:
					source_obj.votes.add(vote)
					vote.voters.add(user_author)
					vote.votes += 1
					vote.save()
					voted = True
			if user_author in source_obj.has_voted.all():
				if not voted:
					source_obj.has_voted.remove(user_author)
			source_obj.save()
	
	# below is non-votes-source	
	if source_type == 'comm':
		if Comment.objects.get(id=source_id):
			source_obj = Comment.objects.get(id=source_id)
			for vote in user_anon.applied_votestyles.all():
				if vote in source_obj.votes.all():
					voters = vote.voters.all()
					if user_author in voters:
						vote.voters.remove(user_author)
						vote.votes -= 1
						vote.save()
					else:
						vote.voters.add(user_author)
						vote.votes += 1
						vote.save()
						voted = True
				else:
					source_obj.votes.add(vote)
					vote.voters.add(user_author)
					vote.votes += 1
					vote.save()
					voted = True
			if user_author in source_obj.has_voted.all():
				if not voted:
					source_obj.has_voted.remove(user_author)
			source_obj.save()
		
	if source_type == 'post':
		if Post.objects.get(id=source_id):
			source_obj = Post.objects.get(id=source_id)
			voted = False
			for vote in user_anon.applied_votestyles.all():
				if vote in source_obj.votes.all():
					voters = vote.voters.all()
					if user_author in voters:
						vote.voters.remove(user_author)
						vote.votes -= 1
						vote.save()
					else:
						vote.voters.add(user_author)
						vote.votes += 1
						vote.save()
						voted = True
				else:
					source_obj.votes.add(vote)
					vote.voters.add(user_author)
					vote.votes += 1
					vote.save()
					voted = True
			if user_author in source_obj.has_voted.all():
				if not voted:
					source_obj.has_voted.remove(user_author)
					source_obj.votes_uniques -= 1
					if source_obj.sum_comments:
						source_obj.under_talked = float(source_obj.votes_uniques) / float(source_obj.sum_comments)
			else:
				if voted:
					source_obj.has_voted.add(user_author)
					source_obj.votes_uniques += 1
					if source_obj.sum_comments:
						source_obj.under_talked = float(source_obj.votes_uniques) / float(source_obj.sum_comments)
			source_obj.save()

	return base_redirect(request, 0)

@login_required
def kick_vote_for_member(request, space_id, author_username):
	loggedinanon = Anon.objects.get(username=request.user)
	loggedinauthor = Author.objects.get(username=request.user.username)

	if request.method == "POST":
		author = Author.objects.get(username=author_username)
		space = Space.objects.get(id=int(space_id))
		if loggedinauthor in space.legislative_members:
			# legislative moderates administrative
			if author in space.administrative_members.all():
				space.administrative_members.remove(author)
			# if successive is checked
			if space.successive:
				if author in space.executive_members.all():
					space.executive_members.remove(author)
				if author in space.judiciary_members.all():
					space.judiciary_members.remove(author)
			if author in space.approved_voters.all():
				space.approved_voters.remove(author)



@login_required
def vote_on_edits_to_conditions(request, space_id, term_id, username):
	return base_redirect(request, 0)

@login_required
def vote_on_edits_to_conditioners(request, space_id, term_id, username):
	return base_redirect(request, 0)

@login_required
def vote_on_edits_to_conditionees(request, space_id, term_id, username):
	return base_redirect(request, 0)

@login_required
def vote_on_edits_to_primate(request, space_id, term_id, username):
	return base_redirect(request, 0)


@login_required		
def vote_for_legislative(request, space_id, username):
	loggedinanon = Anon.objects.get(username=request.user)
	loggedinauthor = Author.objects.get(username=request.user.username)

	if request.method == "POST":
		author = Author.objects.get(username=username)
		space = Space.objects.get(id=int(space_id))
		if loggedinauthor in space.approved_voters.all():
			if space.elected_legislative:
				if space.progressive:
					if loggedinauthor in space.administrative_members.all():
						if author in space.administrative_members.all():
							space.legislative_votes.add(MemberVote.objects.create(voter=loggedinauthor, space=space.to_source(), vote_type='legislative', vote_member=author))
							usernames = []
							count = []
							for member in space.legislative_votes.all():
								if usernames.index(member.vote_member) != -1:
									count[usernames.index(member.vote_member)] += 1
								else:
									count.append(1)
									usernames.append(member.vote_member)
							
							for user in usernames:
								if count[usernames.index(user)] > max_count:
									max_count = count[usernames.index(user)]
									max_user = user
							if space.legislative_votes.all().count() > space.legislative_level:
								for i in range(space.space.legislative_members.all().count(), space.legislative_level):	
									for user in usernames:
										if count[usernames.index(user)] > max_count:
											max_count = count[usernames.index(user)]
											max_user = user
									if space.legislative_members.all().count() < space.legislative_level:
										space.administrative_members.remove(max_user)
										space.legislative_members.add(max_user)
				else:
					if loggedinauthor in space.approved_voters.all():
						if author in space.approved_voters.all():
							space.legislative_votes.add(MemberVote.objects.create(voter=loggedinauthor, space=space.to_source(), vote_type='legislative', vote_member=author))
							usernames = []
							count = []
							for member in space.legislative_votes.all():
								if usernames.index(member.vote_member) != -1:
									count[usernames.index(member.vote_member)] += 1
								else:
									count.append(1)
									usernames.append(member.vote_member)
							
							for user in usernames:
								if count[usernames.index(user)] > max_count:
									max_count = count[usernames.index(user)]
									max_user = user
							if space.legislative_votes.all().count() > space.legislative_level:
								for i in range(space.space.legislative_members.all().count(), space.legislative_level):	
									for user in usernames:
										if count[usernames.index(user)] > max_count:
											max_count = count[usernames.index(user)]
											max_user = user
									if space.legislative_members.all().count() < space.legislative_level:
										space.legislative_members.add(max_user)
			else:
				if space.author == loggedinauthor:
					space.legislative_members.add(author)
	return base_redirect(request, 0)	
			

def vote_for_administrative(request, space_id, username):
	loggedinanon = Anon.objects.get(username=request.user)
	loggedinauthor = Author.objects.get(username=request.user.username)

	if request.method == "POST":
		author = Author.objects.get(username=username)
		space = Space.objects.get(id=int(space_id))
		if loggedinauthor in space.approved_voters.all():
			if space.elected_administrative:
				if space.progressive:
					if loggedinauthor in space.executive_members.all():
						if author in space.executive_members.all():
							space.administrative_votes.add(MemberVote.objects.create(voter=loggedinauthor, space=space.to_source(), vote_type='legislative', vote_member=author))
							usernames = []
							count = []
							for member in space.administrative_votes.all():
								if usernames.index(member.vote_member) != -1:
									count[usernames.index(member.vote_member)] += 1
								else:
									count.append(1)
									usernames.append(member.vote_member)
							
							for user in usernames:
								if count[usernames.index(user)] > max_count:
									max_count = count[usernames.index(user)]
									max_user = user
							if space.administrative_votes.all().count() > space.administrative_level:
								for i in range(space.space.administrative_members.all().count(), space.administrative_level):	
									for user in usernames:
										if count[usernames.index(user)] > max_count:
											max_count = count[usernames.index(user)]
											max_user = user
									if space.administrative_members.all().count() < space.administrative_level:
										space.executive_members.remove(max_user)
										space.administrative_members.add(max_user)
				else:
					if loggedinauthor in space.approved_voters.all():
						if author in space.approved_voters.all():
							space.administrative_votes.add(MemberVote.objects.create(voter=loggedinauthor, space=space.to_source(), vote_type='legislative', vote_member=author))
							usernames = []
							count = []
							for member in space.administrative_votes.all():
								if usernames.index(member.vote_member) != -1:
									count[usernames.index(member.vote_member)] += 1
								else:
									count.append(1)
									usernames.append(member.vote_member)
							
							for user in usernames:
								if count[usernames.index(user)] > max_count:
									max_count = count[usernames.index(user)]
									max_user = user
							if space.administrative_votes.all().count() > space.administrative_level:
								for i in range(space.space.administrative_members.all().count(), space.administrative_level):	
									for user in usernames:
										if count[usernames.index(user)] > max_count:
											max_count = count[usernames.index(user)]
											max_user = user
									if space.administrative_members.all().count() < space.administrative_level:
										space.administrative_members.add(max_user)
			else:
				if space.author == loggedinauthor:
					space.administrative_members.add(author)

	return base_redirect(request, 0)


					
def vote_for_executive(request, space_id, username):
	loggedinanon = Anon.objects.get(username=request.user)
	loggedinauthor = Author.objects.get(username=request.user.username)

	if request.method == "POST":
		author = Author.objects.get(username=username)
		space = Space.objects.get(id=int(space_id))
		if loggedinauthor in space.approved_voters.all():
			if space.elected_executive:
				if space.progressive:
					######## UP TO HERE vote_for ---> renaming _votes _members, need to include conditionees, ers, and primation reference #######
					if loggedinauthor in space.judiciary_members.all():
						if author in space.judiciary_members.all():
							space.executive_votes.add(MemberVote.objects.create(voter=loggedinauthor, space=space.to_source(), vote_type='legislative', vote_member=author))
							usernames = []
							count = []
							for member in space.executive_votes.all():
								if usernames.index(member.vote_member) != -1:
									count[usernames.index(member.vote_member)] += 1
								else:
									count.append(1)
									usernames.append(member.vote_member)
							
							for user in usernames:
								if count[usernames.index(user)] > max_count:
									max_count = count[usernames.index(user)]
									max_user = user
							if space.executive_votes.all().count() > space.executive_level:
								for i in range(space.space.executive_members.all().count(), space.executive_level):	
									for user in usernames:
										if count[usernames.index(user)] > max_count:
											max_count = count[usernames.index(user)]
											max_user = user
									if space.executive_members.all().count() < space.executive_level:
										space.judiciary_members.remove(max_user)
										space.executive_members.add(max_user)
				else:
					if loggedinauthor in space.approved_voters.all():
						if author in space.approved_voters.all():
							space.executive_votes.add(MemberVote.objects.create(voter=loggedinauthor, space=space.to_source(), vote_type='legislative', vote_member=author))
							usernames = []
							count = []
							for member in space.executive_votes.all():
								if usernames.index(member.vote_member) != -1:
									count[usernames.index(member.vote_member)] += 1
								else:
									count.append(1)
									usernames.append(member.vote_member)
							
							for user in usernames:
								if count[usernames.index(user)] > max_count:
									max_count = count[usernames.index(user)]
									max_user = user
							
							if space.executive_votes.all().count() > space.executive_level:
								for i in range(space.space.executive_members.all().count(), space.executive_level):	
									for user in usernames:
										if count[usernames.index(user)] > max_count:
											max_count = count[usernames.index(user)]
											max_user = user
									if space.executive_members.all().count() < space.executive_level:
										space.executive_votes.add(max_user)
			else:
				if space.author == loggedinauthor:
					space.administrative_members.add(author)

	return base_redirect(request, 0)



def vote_for_judiciary(request, space_id, username):
	loggedinanon = Anon.objects.get(username=request.user)
	loggedinauthor = Author.objects.get(username=request.user.username)

	if request.method == "POST":
		author = Author.objects.get(username=username)
		space = Space.objects.get(id=int(space_id))
		if loggedinauthor in space.approved_voters.all():
			if space.elected_administrative:
				if space.progressive:
					if loggedinauthor in space.approved_voters.all():
						if author in space.approved_voters.all():
							space.judiciary_votes.add(MemberVote.objects.create(voter=loggedinauthor, space=space.to_source(), vote_type='legislative', vote_member=author))
							usernames = []
							count = []
							for member in space.judiciary_votes.all():
								if usernames.index(member.vote_member) != -1:
									count[usernames.index(member.vote_member)] += 1
								else:
									count.append(1)
									usernames.append(member.vote_member)
							
							for user in usernames:
								if count[usernames.index(user)] > max_count:
									max_count = count[usernames.index(user)]
									max_user = user
							for i in range(space.judiciary_members.all().count(), space.judiciary_level):	
								for user in usernames:
									if count[usernames.index(user)] > max_count:
										max_count = count[usernames.index(user)]
										max_user = user
								if space.judiciary_members.all().count() < space.judiciary_level:
									space.judiciary_members.add(max_user)
				else:
					if loggedinauthor in space.approved_voters.all():
						if author in space.approved_voters.all():
							space.judiciary_votes.add(MemberVote.objects.create(voter=loggedinauthor, space=space.to_source(), vote_type='legislative', vote_member=author))
							usernames = []
							count = []
							for member in space.judiciary_votes.all():
								if usernames.index(member.vote_member) != -1:
									count[usernames.index(member.vote_member)] += 1
								else:
									count.append(1)
									usernames.append(member.vote_member)
							
							for user in usernames:
								if count[usernames.index(user)] > max_count:
									max_count = count[usernames.index(user)]
									max_user = user
							for i in range(space.space.judiciary_members.all().count(), space.judiciary_level):	
								for user in usernames:
									if count[usernames.index(user)] > max_count:
										max_count = count[usernames.index(user)]
										max_user = user
								if space.judiciary_members.all().count() < space.judiciary_level:
									space.judiciary_members.add(max_user)

			else:
				if space.author == loggedinauthor:
					space.judiciary_members.add(author)

	return base_redirect(request, 0)


				




@login_required
def users_space_edit(request, space):
	loggedinanon = Anon.objects.get(username=request.user)
	loggedinauthor = Author.objects.get(username=request.user.username)

	if request.method == 'POST':
		actual_space = Space.objects.get(id=space)
		actual_source_space = actual_space.to_source()

		actual_space.sidebar = request.POST.get('sidebar')
		actual_space.values = request.POST.get('values')
		actual_space.vision = request.POST.get('vision')
		actual_space.mission = request.POST.get('mission')
		if request.POST.get('public') == 'on':
			actual_space.public = True
		if request.POST.get('for_sale') == 'on':
			actual_space.for_sale = True
		actual_space.entry_fee = request.POST.get('entry_fee')
		actual_space.continuation_fee = request.POST.get('continuation_fee')
		
		if request.POST.get('invite_only') == 'on':
			actual_space.invite_only = True
		if request.POST.get('invite_active') == 'on':
			actual_space.invite_active = True
		actual_space.invite_code = request.POST.get('invite_code')
		actual_space.save()
		actual_source_space.save()
		return redirect('Bable:tob_users_space', user=request.user.username, space_id=actual_space.id, count=0)
	return base_redirect(request, 0)


def roadmap(request):
	return render(request, 'roadmap.html')

def annotate_url_post_comment(request, search_url_id):
	registerform = UserCreationForm()
	loginform = AuthenticationForm()
	
	search = SearchURL.objects.get(id=int(search_url_id))
	

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		if loggedinauthor == search.author:
			searchform = SearchURLForm(instance=search)
		else:
			searchform = ''

		commentform = CommentForm(request, request.POST)
		if commentform.is_valid():
			if commentform.cleaned_data['dictionaries'] == 0:
				new_com = Comment.objects.create(body=commentform.cleaned_data['body'], author=loggedinauthor)
			else:
				new_com = Comment.objects.create(body=commentform.cleaned_data['body'], author=loggedinauthor)
				for dic in commentform.cleaned_data['dictionaries']:
					new_com.dictionaries.add(loggedinanon.purchased_dictionaries.get(the_dictionary_itself=dic))
				new_com.sum_dictionaries = new_com.dictionaries.count()
				new_com.save()
			comment_location, x = CommentLocations.objects.get_or_create(from_top=request.POST.get('from_top'), from_left=request.POST.get('from_left'))
			comment_location.comments.add(new_com)
			comment_location.save()
			search.comment_locations.add(comment_location)
			search.save()
		

		commentform = CommentForm(request)
		
		the_response = render(request, 'annotate_here.html', {"commentform": commentform, "searchform": searchform, "search": search, "loggedinanon": loggedinanon, 'loginform': loginform, 'registerform': registerform,  'word_form': word_form, 'dic_form':dic_form, 'space_form': space_form, "post_form": post_form, 'task_form': task_form, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, 'annotate_here.html', {"query_string": query_string, "search": search, 'loginform': loginform, 'registerform': registerform, })
	
	the_response.set_cookie('current', 'annotate_url')
	return the_response


def annotate_url_post_comment_location(request, search_url_id, location_id):
	registerform = UserCreationForm()
	loginform = AuthenticationForm()
	
	search = SearchURL.objects.get(id=int(search_url_id))
	

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		if loggedinauthor == search.author:
			searchform = SearchURLForm(instance=search)
		else:
			searchform = ''

		commentform = CommentForm(request, request.POST)
		if commentform.is_valid():
			if commentform.cleaned_data['dictionaries'] == 0:
				new_com = Comment.objects.create(body=commentform.cleaned_data['body'], author=loggedinauthor)
			else:
				new_com = Comment.objects.create(body=commentform.cleaned_data['body'], author=loggedinauthor)
				for dic in commentform.cleaned_data['dictionaries']:
					new_com.dictionaries.add(loggedinanon.purchased_dictionaries.get(the_dictionary_itself=dic))
				new_com.sum_dictionaries = new_com.dictionaries.count()
				new_com.save()
			comment_location, x = CommentLocations.objects.get(id=int(location_id))
			comment_location.comments.add(new_com)
			comment_location.save()
			search.comment_locations.add(comment_location)
			search.save()
		

		commentform = CommentForm(request)
		
		the_response = render(request, 'annotate_here.html', {"commentform": commentform, "searchform": searchform, "search": search, "loggedinanon": loggedinanon, 'loginform': loginform, 'registerform': registerform,  'word_form': word_form, 'dic_form':dic_form, 'space_form': space_form, "post_form": post_form, 'task_form': task_form, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, 'annotate_here.html', {"query_string": query_string, "search": search, 'loginform': loginform, 'registerform': registerform, })
	
	the_response.set_cookie('current', 'annotate_url')
	return the_response




def annotate_url_comment_delete(request, search_url_id, comment_id):
	registerform = UserCreationForm()
	loginform = AuthenticationForm()
	
	search = SearchURL.objects.get(id=int(search_url_id))
	comment = Comment.objects.get(id=int(comment_id))
	

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		if loggedinauthor == search.author:
			searchform = SearchURLForm(instance=search)
		else:
			searchform = ''

		if loggedinauthor == search.author or loggedinauthor == comment.author:
			comment.delete()

		commentform = CommentForm(request)
		
		the_response = render(request, 'annotate_here.html', {"commentform": commentform, "searchform": searchform, "search": search, "loggedinanon": loggedinanon, 'loginform': loginform, 'registerform': registerform,  'word_form': word_form, 'dic_form':dic_form, 'space_form': space_form, "post_form": post_form, 'task_form': task_form, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, 'annotate_here.html', {"query_string": query_string, "search": search, 'loginform': loginform, 'registerform': registerform, })
	
	the_response.set_cookie('current', 'annotate_url')
	return the_response


def annotate_url_post_edits(request, search_url_id):
	registerform = UserCreationForm()
	loginform = AuthenticationForm()
	
	search = SearchURL.objects.get(id=int(search_url_id))

	

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		if loggedinauthor == search.author:
			searchform = SearchURLForm(request.POST)
			if searchform.is_valid():
				searchform.save()
				search.latest_change_date = timezone.now()
				search.save()
			searchform = SearchURLForm(instance=search)
		else:
			searchform = ''

		commentform = CommentForm(request)
		
		the_response = render(request, 'annotate_here.html', {"commentform": commentform, "searchform": searchform, "search": search, "loggedinanon": loggedinanon, 'loginform': loginform, 'registerform': registerform,  'word_form': word_form, 'dic_form':dic_form, 'space_form': space_form, "post_form": post_form, 'task_form': task_form, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, 'annotate_here.html', {"query_string": query_string, "search": search, 'loginform': loginform, 'registerform': registerform, })
	
	the_response.set_cookie('current', 'annotate_url')
	return the_response


def annotate_url(request, search_url_id):
	registerform = UserCreationForm()
	loginform = AuthenticationForm()
	
	search = SearchURL.objects.get(id=int(search_url_id))
	

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		if loggedinauthor == search.author:
			searchform = SearchURLForm(instance=search)
		else:
			searchform = ''

		commentform = CommentForm(request)
		
		the_response = render(request, 'annotate_here.html', {"commentform": commentform, "searchform": searchform, "search": search, "loggedinanon": loggedinanon, 'loginform': loginform, 'registerform': registerform,  'word_form': word_form, 'dic_form':dic_form, 'space_form': space_form, "post_form": post_form, 'task_form': task_form, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, 'annotate_here.html', {"query_string": query_string, "search": search, 'loginform': loginform, 'registerform': registerform, })
	
	the_response.set_cookie('current', 'annotate_url')
	return the_response




def delete_annotation_url(request, search_url_id):
	registerform = UserCreationForm()
	loginform = AuthenticationForm()
	
	search = SearchURL.objects.get(id=int(search_url_id))
	

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		if loggedinauthor == search.author:
			search.delete()
			searchform = SearchURLForm()
		else:
			searchform = ''

		commentform = CommentForm(request)
		
		the_response = render(request, 'annotate_here.html', {"commentform": commentform, "searchform": searchform, "search": search, "loggedinanon": loggedinanon, 'loginform': loginform, 'registerform': registerform,  'word_form': word_form, 'dic_form':dic_form, 'space_form': space_form, "post_form": post_form, 'task_form': task_form, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, 'annotate_here.html', {"query_string": query_string, "search": search, 'loginform': loginform, 'registerform': registerform, })
	
	the_response.set_cookie('current', 'annotate_url')
	return the_response


import validators
from django.utils import dateformat, timezone
def search(request, count):
	#recently_modified_post = Post.objects.order_by('-latest_change_date')[:100]
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	count = int(count)
	count100 = count+25
	mcount = 0
	if count > 25:
		mcount = count - 25
	if ('q' in request.GET) and request.GET['q'].strip():
		query_string = request.GET['q']
		if validators.url(query_string):
			if request.user.is_authenticated:
				loggedinuser = User.objects.get(username=request.user.username)
				loggedinanon = Anon.objects.get(username=loggedinuser)
				searcher = SearchURL.objects.create(name='/u/'+request.user.username+'/'+dateformat.format(timezone.now(), 'Y-m-d H:i:s'), url=query_string, author=Author.objects.get(username=request.user.username))
				loggedinanon.search_urls.add(searcher)
				return redirect('Bable:annotate_url', search_url_id=searcher.id)

	page_views, created = Pageviews.objects.get_or_create(page="tower_of_bable")
	page_views.views += 1
	page_views.save()

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		previous_view = UserViews.objects.filter(anon=loggedinanon).order_by('view_date').first()
		pages_view = UserViews.objects.create(page_view="search__"+query_string+"__"+str(count), anon=loggedinanon)
		page_views.user_views.add(pages_view)
		if previous_view:
			pages_view.previous_view_id = previous_view.id
			pages_view.previous_page = previous_view.page_view
			pages_view.previous_view_date = previous_view.view_date
			pages_view.previous_view_time_between_pages = datetime.datetime.now(timezone.utc) - previous_view.view_date
		

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		search_post = Post.objects.filter(title__icontains=query_string).filter(Q(public=True)|Q(allowed_to_view_authors=loggedinauthor)).order_by('-latest_change_date')[count:count100]
		search_space = Space.objects.filter(the_space_itself__the_word_itself__icontains=query_string).filter(Q(public=True)|Q(approved_voters=loggedinauthor)).order_by('-latest_change_date')[count:count100]
		search_words = Word.objects.filter(the_word_itself__icontains=query_string).order_by('-latest_change_date')[count:count100]
		search_dics = Dictionary.objects.filter(the_dictionary_itself__icontains=query_string).filter(Q(public=True)|Q(allowed_to_view_authors=loggedinauthor)).order_by('-latest_change_date')[count:count100]
		posts_by_viewcount = search_post
		
		the_response = render(request, 'tob_search.html', {"query_string": query_string, "loggedinanon": loggedinanon, "mcount": mcount, "count100": count100, "posts": posts_by_viewcount, "spaces": search_space, "words": search_words, "dics": search_dics, 'loginform': loginform, 'registerform': registerform,  'word_form': word_form, 'dic_form':dic_form, 'space_form': space_form, "post_form": post_form, 'task_form': task_form, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		search_post = Post.objects.filter(title__icontains=query_string).filter(public=True)[count:count100]
		posts_by_viewcount = search_post
		the_response = render(request, 'tob_search.html', {"query_string": query_string, "mcount": mcount, "count100": count100, "posts": posts_by_viewcount, 'loginform': loginform, 'registerform': registerform, })
	
	the_response.set_cookie('current', 'search')
	return the_response


@login_required
def create_product_w_price(request, post_id):
	loggedinuser = User.objects.get(username=request.user.username)
	loggedinanon = Anon.objects.get(username=loggedinuser)
	loggedinauthor = Author.objects.get(username=request.user.username)
	if request.method == "POST":
		product_form = ProductForm(request.POST)
		product_form.anon_user_id = loggedinanon.id
		if product_form.is_valid():
			product = product_form.save()
			product.anon_user_id = loggedinanon.id
			product.save()
			loggedinanon.products.add(product)
			loggedinanon.save()
			post = Post.objects.get(id=int(post_id))
			if post in loggedinanon.posts.all():
				post.products.add(product)
				post.save()
	return base_redirect(request, 0)



class KeyupCheckoutSessionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        price = Price.objects.get(id=self.kwargs["pk"])
        post = Post.objects.get(id=self.kwargs["post_id"])
        anon = Anon.objects.get(username=request.user)
        if price in anon.products.all():
        	if post in anon.posts.all():
        		post.products.add(price)
        		post.save()
        return base_redirect(request, 0)



class CreateCheckoutSessionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        price = Price.objects.get(id=self.kwargs["pk"])
        loggedinanon = Anon.objects.get(username=request.user)
        stripe.api_key = loggedinanon.stripe_private_key
        domain = "https://www.predictionary.us"
        if price.monthly:
        	mode = 'subscription'
        else:
        	mode = 'payment'
        if settings.DEBUG:
            #domain = "http://127.0.0.1:8000"
        	checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price.stripe_price_id,
                    'quantity': 1,
                },
            ],
            mode=mode,
            success_url=domain + '/success/',
            cancel_url=domain + '/cancel/',
            customer_email=self.request.user.email,
        )
        return redirect(checkout_session.url)

from django.views.generic import TemplateView


class SuccessView(TemplateView):
    template_name = "success.html"

class CancelView(TemplateView):
    template_name = "cancel.html"

@method_decorator(login_required, name="dispatch")
class ProductLandingPageView(TemplateView):
    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        prices = Price.objects.all().filter(name__contains="Full")
        context = super(ProductLandingPageView,
                        self).get_context_data(**kwargs)
        context.update({
            "prices": prices
        })
        return context


import discord
import requests

@csrf_exempt
@login_required
async def stripe_webhook(request):
	payload = request.body
	sig_header = request.META['HTTP_STRIPE_SIGNATURE']
	event = None
	loggedinanon = Anon.objects.get(username=request.user)
	stripe.api_key = loggedinanon.stripe_private_key
	try:
		event = stripe.Webhook.construct_event(
			payload, sig_header, loggedinanon.stripe_private_key
		)
	except ValueError as e:
		# Invalid payload
		return HttpResponse(status=400)
	except stripe.error.SignatureVerificationError as e:
		# Invalid signature
		return HttpResponse(status=400)

	# Handle the checkout.session.completed event
	if event['type'] == 'checkout.session.completed':
		session = event['data']['object']
		customer_email = session["customer_details"]["email"]

		payment_intent = session["payment_intent"]

		line_items = stripe.checkout.Session.list_line_items(session["id"])

		stripe_price_id = line_items["data"][0]["price"]["id"]
		price = Price.objects.get(stripe_price_id=stripe_price_id)
		product = price

		user_that_just_paid, x = User.objects.get_or_create(email=customer_email, username=str(price.id)+stripe_price_id, password=stripe_price_id)
		loggedinanon2, x = Anon.objects.get_or_create(username=user_that_just_paid, stripe_webhook_secret=loggedinanon.stripe_webhook_secret, stripe_private_key=loggedinanon.stripe_private_key)

		loggedinanon.purchases.add(product)
		loggedinanon.save()


		send_mail(
			subject=product.name,
			message="Thanks for your subscription: " + product.url2 + " your username is: "+str(price.id)+stripe_price_id+" and your password is: "+stripe_price_id+"   Here is your purchased message:" + product.description2purchase,
			recipient_list=[customer_email],
			from_email="jackdonmclovin@gmail.com"
		)

		send_mail(
			subject=product.name,
			message="Thanks for your subscription: " + customer_email + " " + product.url2+ "   Here is your purchased message:" + product.description2purchase,
			recipient_list="jackdonmclovin@gmail.com",
			from_email="jackdonmclovin@gmail.com"
		)
		# TODO include a URL to the appropriate discord server for thier level.

		

		

	return redirect(price.url2)






def tower_of_bable(request):
	#recently_modified_post = Post.objects.order_by('-latest_change_date')[:100]
	registerform = UserCreationForm()
	loginform = AuthenticationForm()

	buyadvertisingform = BuyAdvertisingForm()
	
	lower = 0
	count100 = 25
	mcount = 0

	
	basic_price, x = Price.objects.get_or_create(id=1)
	if not basic_price.stripe_price_id:
		basic_price.name="Donate - Predictionary.us"
		basic_price.anon_user_id=1
		basic_price.stripe_price_id = "price_1Nf8jMIDEcA7LIBjpnt385yZ"

		basic_price.stripe_product_id = "prod_OS2pk9gZWam5Ye"
		basic_price.price = 500
		basic_price.save()


	page_views, created = Pageviews.objects.get_or_create(page="tower_of_bable")
	page_views.views += 1
	page_views.save()

	translation = page_views.translation

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		x_forwarded_for = x_forwarded_for.split(',')[0]
	ip = request.META.get('REMOTE_ADDR')

	total = 0
	for page in Pageviews.objects.all():
		total += page.views

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
		previous_view = UserViews.objects.filter(anon=loggedinanon).order_by('view_date').first()
		pages_view = UserViews.objects.create(page_view="tower_of_bable", anon=loggedinanon)
		page_views.user_views.add(pages_view)
		if previous_view:
			pages_view.previous_view_id = previous_view.id
			pages_view.previous_page = previous_view.page_view
			pages_view.previous_view_date = previous_view.view_date
			pages_view.previous_view_time_between_pages = datetime.datetime.now(timezone.utc) - previous_view.view_date
		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		posts_by_viewcount = Post.objects.order_by(loggedinanon.post_sort_char)[:25]
		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		file_form = FileForm()
		post_sort_form = PostSortForm(request)
		
		posts_values = list(posts_by_viewcount.values('img', 'url2', 'author__username', 'id', 'title', 'body', 'viewcount', 'votes_count', 'votes_uniques', 'latest_change_date'))
		postscount = 25
		posts_by_viewcount = posts_values
		
		the_response = render(request, 'tower_of_bable.html', {"basic_price": basic_price, "post_sort_form": post_sort_form, "postscount": postscount, "ip": ip, "x_forwarded_for": x_forwarded_for, "buyadvertisingform": buyadvertisingform, "file_form": file_form, "total": total, "count": lower, "mcount": mcount, "count100": count100, "loggedinanon": loggedinanon, "posts": posts_by_viewcount, 'loginform': loginform, 'registerform': registerform,  'word_form': word_form, 'dic_form':dic_form, 'space_form': space_form, "post_form": post_form, 'task_form': task_form, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		posts_by_viewcount = Post.objects.order_by('viewcount')[:25]
		postscount = 25
		posts_values = list(posts_by_viewcount.values('img', 'url2', 'author__username', 'id', 'title', 'body', 'viewcount', 'votes_count', 'votes_uniques', 'latest_change_date'))
		posts_by_viewcount = posts_values
		the_response = render(request, 'tower_of_bable.html', {"basic_price": basic_price, "postscount": postscount, "ip": ip, "x_forwarded_for": x_forwarded_for, "buyadvertisingform": buyadvertisingform, "total": total, "count": lower, "mcount": mcount, "count100": count100, "posts": posts_by_viewcount, 'loginform': loginform, 'registerform': registerform, })
	
	the_response.set_cookie('current', 'tower_of_bable')
	return the_response


def landingpage(request):
	#recently_modified_post = Post.objects.order_by('-latest_change_date')[:100]
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()

	
	count = 0
	count100 = 100
	mcount = 0

	buyadvertisingform = BuyAdvertisingForm()


	page_views, created = Pageviews.objects.get_or_create(page="landingpage")
	page_views.views += 1
	page_views.save()

	translation = page_views.translation

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		x_forwarded_for = x_forwarded_for.split(',')[0]
	ip = request.META.get('REMOTE_ADDR')

	total = 0
	for page in Pageviews.objects.all():
		total += page.views

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
		previous_view = UserViews.objects.filter(anon=loggedinanon).order_by('view_date').first()
		pages_view = UserViews.objects.create(page_view="landingpage", anon=loggedinanon)
		page_views.user_views.add(pages_view)
		if previous_view:
			pages_view.previous_view_id = previous_view.id
			pages_view.previous_page = previous_view.page_view
			pages_view.previous_view_date = previous_view.view_date
			pages_view.previous_view_time_between_pages = datetime.datetime.now(timezone.utc) - previous_view.view_date
		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		
		the_response = render(request, 'landingpage.html', { "ip": ip, "x_forwarded_for": x_forwarded_for, "buyadvertisingform": buyadvertisingform, "loggedinanon": loggedinanon, 'loginform': loginform, 'registerform': registerform,  'word_form': word_form, 'dic_form':dic_form, 'space_form': space_form, "post_form": post_form, 'task_form': task_form, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})

	the_response = render(request, 'landingpage.html', {"buyadvertisingform": buyadvertisingform, "ip": ip, "x_forwarded_for": x_forwarded_for, 'loginform': loginform, 'registerform': registerform, })
	
	the_response.set_cookie('current', 'landingpage')
	return the_response



def change_password(request):
	#recently_modified_post = Post.objects.order_by('-latest_change_date')[:100]
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	
	posts_by_viewcount = Post.objects.order_by('viewcount')[:100]
	count = 0
	count100 = 100
	mcount = 0

	for post in posts_by_viewcount:
		if ' ' in post.author.username:

			post.delete()

		if post.author.username == "":
			post.delete()
	
		if post.author.username == "...":
			post.delete()

	

	page_views, created = Pageviews.objects.get_or_create(page="tower_of_bable")
	page_views.views += 1
	page_views.save()

	translation = page_views.translation



	total = 0
	for page in Pageviews.objects.all():
		total += page.views

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
		previous_view = UserViews.objects.filter(anon=loggedinanon).order_by('view_date').first()
		pages_view = UserViews.objects.create(page_view="change_password", anon=loggedinanon)
		page_views.user_views.add(pages_view)
		if previous_view:
			pages_view.previous_view_id = previous_view.id
			pages_view.previous_page = previous_view.page_view
			pages_view.previous_view_date = previous_view.view_date
			pages_view.previous_view_time_between_pages = datetime.datetime.now(timezone.utc) - previous_view.view_date
		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		posts_by_viewcount = Post.objects.order_by(loggedinanon.post_sort_char)[0:100]


		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		
		the_response = render(request, 'tower_of_bable.html', {"total": total, "count": count, "mcount": mcount, "count100": count100, "loggedinanon": loggedinanon, "posts": posts_by_viewcount, 'loginform': loginform, 'registerform': registerform,  'word_form': word_form, 'dic_form':dic_form, 'space_form': space_form, "post_form": post_form, 'task_form': task_form, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		count = 0
		the_response = render(request, 'tower_of_bable.html', {"total": total, "count": count, "mcount": mcount, "count100": count100, "posts": posts_by_viewcount, 'loginform': loginform, 'registerform': registerform, })
	
	the_response.set_cookie('current', 'tower_of_bable')
	return the_response



def tower_of_bable_count(request, count):
	#recently_modified_post = Post.objects.order_by('-latest_change_date')[:100]
	registerform = UserCreationForm()

	
	basic_price, x = Price.objects.get_or_create(name="Donate - Predictionary.us", anon_user_id=1)
	if not basic_price.stripe_price_id:
		basic_price.stripe_price_id = "price_1Nf8jMIDEcA7LIBjpnt385yZ"

		basic_price.stripe_product_id = "prod_OS2pk9gZWam5Ye"
		basic_price.price = 500
		basic_price.save()


	count = int(count)
	if not count:
		return redirect('Bable:tower_of_bable')

	page_views, created = Pageviews.objects.get_or_create(page="tower_of_bable_count")
	page_views.views += 1
	page_views.save()

	total = 0
	for page in Pageviews.objects.all():
		total += page.views

	buyadvertisingform = BuyAdvertisingForm()
	
	
	count100 = count + 25
	mcount = 0
	if count > 25:
		mcount = count - 25
	posts_by_viewcount = Post.objects.order_by('viewcount')[count:count100]
	postscount = posts_by_viewcount.count()
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
		previous_view = UserViews.objects.filter(anon=loggedinanon).order_by('view_date').first()
		pages_view = UserViews.objects.create(page_view="tower_of_bable_count__"+str(count), anon=loggedinanon)
		page_views.user_views.add(pages_view)
		if previous_view:
			pages_view.previous_view_id = previous_view.id
			pages_view.previous_page = previous_view.page_view
			pages_view.previous_view_date = previous_view.view_date
			pages_view.previous_view_time_between_pages = datetime.datetime.now(timezone.utc) - previous_view.view_date
		posts_by_viewcount = Post.objects.order_by(loggedinanon.post_sort_char)[count:count100]
	
	
	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		
		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		post_sort_form = PostSortForm(request)
		

		the_response = render(request, 'tower_of_bable.html', {"basic_price": basic_price, "post_sort_form": post_sort_form, "postscount": postscount, "buyadvertisingform": buyadvertisingform, "total": total, "count": count, "mcount": mcount, "count100": count100, "posts": posts_by_viewcount, "loggedinanon": loggedinanon, 'loginform': loginform, 'registerform': registerform,  'postform': post_form, 'spaceform': space_form, "post_form": post_form, 'taskform': task_form, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, 'tower_of_bable.html', {"basic_price": basic_price, "postscount": postscount, "buyadvertisingform": buyadvertisingform, "total": total, "count": count, "mcount": mcount, "count100": count100, "posts": posts_by_viewcount, 'loginform': loginform, 'registerform': registerform, })
	the_response.set_cookie('current', 'tower_of_bable_count')
	the_response.set_cookie('count', count)
	return the_response

def tob_view_spaces(request):
	count = 0
	count100 = count+100
	mcount = 0
	registerform = UserCreationForm()

	page_views, created = Pageviews.objects.get_or_create(page="tower_of_bable_count")
	page_views.views += 1
	page_views.save()
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
		previous_view = UserViews.objects.filter(anon=loggedinanon).order_by('view_date').first()
		pages_view = UserViews.objects.create(page_view="tob_view_spaces", anon=loggedinanon)
		page_views.user_views.add(pages_view)
		if previous_view:
			pages_view.previous_view_id = previous_view.id
			pages_view.previous_page = previous_view.page_view
			pages_view.previous_view_date = previous_view.view_date
			pages_view.previous_view_time_between_pages = datetime.datetime.now(timezone.utc) - previous_view.view_date

		
		spaces = Space.objects.order_by(loggedinanon.space_sort_char)[0:100]
		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		space_sort_form = SpaceSortForm(request)
		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		the_response = render(request, 'tob_view_spaces.html', {"space_sort_form": space_sort_form, "spaces": spaces, "count": count, "mcount": mcount, "count100": count100, "loggedinanon": loggedinanon,'postform': post_form, 'spaceform': space_form, "post_form": post_form, 'taskform': task_form, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		spaces = Space.objects.order_by('-latest_change_date', 'votes_count', 'viewcount')[0:100]
		the_response = render(request, 'tob_view_spaces.html', {"spaces": spaces, "count": count, "mcount": mcount, "count100": count100, 'loginform': loginform, 'registerform': registerform, })
	the_response.set_cookie('current', 'tob_view_spaces')
	the_response.set_cookie('count', count)
	return the_response

def tob_view_spaces_count(request, count):
	count = int(count)
	if not count:
		return redirect('Bable:tob_view_spaces')
	count100 = count+100
	if count > 100:
		mcount = count - 100
	else:
		mcount = 0
	
	registerform = UserCreationForm()
	
		
	page_views, created = Pageviews.objects.get_or_create(page="tower_of_bable_count")
	page_views.views += 1
	page_views.save()
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
		previous_view = UserViews.objects.filter(anon=loggedinanon).order_by('view_date').first()
		pages_view = UserViews.objects.create(page_view="tob_view_spaces_count__"+str(count), anon=loggedinanon)
		page_views.user_views.add(pages_view)
		if previous_view:
			pages_view.previous_view_id = previous_view.id
			pages_view.previous_page = previous_view.page_view
			pages_view.previous_view_date = previous_view.view_date
			pages_view.previous_view_time_between_pages = datetime.datetime.now(timezone.utc) - previous_view.view_date
		
	
	
	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		
		spaces = Space.objects.order_by(loggedinanon.space_sort_char)[0:100]
		
		the_response = render(request, 'tob_view_spaces.html', {"spaces": spaces, "count": count, "mcount": mcount, "count100": count100, "loggedinanon": loggedinanon, 'loginform': loginform, 'registerform': registerform,  'registerterms': registerterms, 'postform': post_form, 'spaceform': space_form, "post_form": post_form, 'taskform': task_form, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		spaces = Space.objects.order_by('latest_change_date', 'votes_count', 'viewcount')[count:count100]
		the_response = render(request, 'tob_view_spaces.html', {"latest_spaces": latest_spaces, "count": count, "mcount": mcount, "count100": count100, 'loginform': loginform, 'registerform': registerform, })
	the_response.set_cookie('current', 'tob_view_spaces_count')
	the_response.set_cookie('count', count)
	return the_response

def tob_space_view(request, space):
	
	count = 0
	registerform = UserCreationForm()
	
		
	page_views, created = Pageviews.objects.get_or_create(page="tower_of_bable_count")
	page_views.views += 1
	page_views.save()
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
		previous_view = UserViews.objects.filter(anon=loggedinanon).order_by('view_date').first()
		pages_view = UserViews.objects.create(page_view="tob_space_view__"+space, anon=loggedinanon)
		page_views.user_views.add(pages_view)
		if previous_view:
			pages_view.previous_view_id = previous_view.id
			pages_view.previous_page = previous_view.page_view
			pages_view.previous_view_date = previous_view.view_date
			pages_view.previous_view_time_between_pages = datetime.datetime.now(timezone.utc) - previous_view.view_date
		
	
	particular_space = Space.objects.get(id=space)
	users_space = Space.objects.get(id=space)
	user = User.objects.get(id=int(users_space.author.to_full().username.id))
	user_anon = Anon.objects.get(username=user)
		
	spaces_posts = particular_space.posts.all()
	users_sponsors = users_space.sponsors.all()
	try:
		if spaces_posts is not None:
			if request.user.is_authenticated:
				if not users_space.public:
					if request.user.username in users_space.approved_voters.all().values_list('username'):
						spaces_posts = spaces_posts.order_by(loggedinanon.post_sort_char)[count:count+100]
						space_viewable = True
					else:
						space_viewable = False
				else:
					spaces_posts = spaces_posts.order_by(loggedinanon.post_sort_char)[count:count+100]
					space_viewable = True
			else:
				if users_space.public:
					spaces_posts.order_by('viewcount')[:100]
					space_viewable = True
				else:
					space_viewable = False
	
	except ObjectDoesNotExist:
		users_space = Space.objects.get(id=space)
		if request.user.is_authenticated:
			if not users_space.public:
				if len(users_space.filter(approved_votters__username=request.user.username))>0:
					spaces_posts = spaces_posts.order_by(loggedinanon.post_sort_char)[count:count+100]
					space_viewable = True
				else:
					space_viewable = False
			else:
				spaces_posts = spaces_posts.order_by(loggedinanon.post_sort_char)[count:count+100]
				space_viewable = True
		else:
			if users_space.public:
				spaces_posts = spaces_posts.order_by(loggedinanon.post_sort_char)[count:count+100]
				space_viewable = True
			else:
				space_viewable = False
	
	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		sponsor_form = SponsorForm()

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		
		the_response = render(request, 'tob_space_view.html', {"sponsorform": sponsor_form, "users_sponsors": users_sponsors, "user_anon": user_anon, "users_space": users_space, "space_viewable": space_viewable, "spaces_posts": spaces_posts, "loggedinanon": loggedinanon, 'loginform': loginform, 'registerform': registerform, 'postform': post_form, 'spaceform': space_form, "post_form": post_form, 'taskform': task_form, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form, 'users_space': users_space, 'spaces_posts': spaces_posts })
	else:
		the_response = render(request, 'tob_space_view.html', {"users_sponsors": users_sponsors, "user_anon": user_anon, "users_space": users_space, "space_viewable": space_viewable, "spaces_posts": spaces_posts, 'loginform': loginform, 'registerform': registerform })
	
	the_response.set_cookie('current', 'tob_space_view')
	the_response.set_cookie('space', space)
	the_response.set_cookie('count', count)
	return the_response

def tob_space_view_count(request, space, count):
	space = int(space)
	count = int(count)
	registerform = UserCreationForm()
	
		
	page_views, created = Pageviews.objects.get_or_create(page="tower_of_bable_count")
	page_views.views += 1
	page_views.save()
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
		previous_view = UserViews.objects.filter(anon=loggedinanon).order_by('view_date').first()
		pages_view = UserViews.objects.create(page_view="tob_space_view_count__"+str(space)+"__"+str(count), anon=loggedinanon)
		page_views.user_views.add(pages_view)
		if previous_view:
			pages_view.previous_view_id = previous_view.id
			pages_view.previous_page = previous_view.page_view
			pages_view.previous_view_date = previous_view.view_date
			pages_view.previous_view_time_between_pages = datetime.datetime.now(timezone.utc) - previous_view.view_date
		
		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		sponsor_form = SponsorForm()

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()


	
	particular_space = Space.objects.get(id=space)
	users_space = Space.objects.get(id=space)
	user_anon = users_space.author.to_anon()
	spaces_posts = particular_space.posts.all()
	users_sponsors = users_space.sponsors.all()
	try:
		if spaces_posts is not None:
			if request.user.is_authenticated:
				if not users_space.public:
					if request.user.username in users_space.approved_voters.all().values_list('username'):
						spaces_posts = spaces_posts.order_by(loggedinanon.post_sort_char)[count:count+100]
						space_viewable = True
					else:
						space_viewable = False
				else:
					spaces_posts = spaces_posts.order_by(loggedinanon.post_sort_char)[count:count+100]
					space_viewable = True
			else:
				if users_space.public:
					spaces_posts.order_by('viewcount')[:100]
					space_viewable = True
				else:
					space_viewable = False
	
	except ObjectDoesNotExist:
		users_space = Space.objects.get(author=user_author, the_space_itself__the_word_itself=space)
		if request.user.is_authenticated:
			if not users_space.public:
				if len(users_space.filter(approved_votters__username=request.user.username))>0:
					spaces_posts = spaces_posts.order_by(loggedinanon.post_sort_char)[count:count+100]
					space_viewable = True
				else:
					space_viewable = False
			else:
				spaces_posts = spaces_posts.order_by(loggedinanon.post_sort_char)[count:count+100]
				space_viewable = True
		else:
			if users_space.public:
				spaces_posts = spaces_posts.order_by(loggedinanon.post_sort_char)[count:count+100]
				space_viewable = True
			else:
				space_viewable = False


	if request.user.is_authenticated:
		vote_for_legislative_form = VoteForLegislativeForm(users_space)
		vote_for_administrative_form = VoteForAdministrativeForm(users_space)
		vote_for_executive_form = VoteForExecutiveForm(users_space)
		vote_for_judiciary_form = VoteForJudiciaryForm(users_space)
		the_response = render(request, 'tob_space_view.html', {"loggedinauthor": loggedinauthor, "vote_for_legislative_form": vote_for_legislative_form, "vote_for_administrative_form": vote_for_administrative_form, "vote_for_executive_form": vote_for_executive_form, "vote_for_judiciary_form": vote_for_judiciary_form, "user_anon": user_anon, "users_sponsors": users_sponsors, "users_space": users_space, "space_viewable": space_viewable, "spaces_posts": spaces_posts, "loggedinanon": loggedinanon, 'loginform': loginform, 'registerform': registerform, 'postform': post_form, 'spaceform': space_form, "post_form": post_form, 'taskform': task_form, 
			"sponsorform": sponsor_form, "apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, 'tob_space_view.html', { "user_anon": user_anon, "users_sponsors": users_sponsors, "users_space": users_space, "space_viewable": space_viewable, "spaces_posts": spaces_posts, 'loginform': loginform, 'registerform': registerform})

	the_response.set_cookie('current', 'tob_space_view_count')
	the_response.set_cookie('space', space)
	the_response.set_cookie('count', count)
	return the_response


@login_required
def vote_for_legislative(request, space):
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		users_space = Space.objects.get(id=int(space))
		
		if request.method == "POST":
			vote_for_legislative_form = VoteForLegislativeForm(users_space, data=request.POST)
			if vote_for_legislative_form.is_valid():
				vote_member = Author.objects.get(username=vote_for_legislative_form.cleaned_data['legislative_members'])
				if loggedinauthor in users_space.approved_voters.all():
					if users_space.legislative_votes.filter(voter=loggedinauthor).count():
						membervotes = users_space.legislative_votes.filter(voter=loggedinauthor)[0]
						member_votes.vote_member = vote_member
						member_votes.save()
					else:
						membervotes = MemberVotes.objects.create(voter=loggedinauthor, space=users_space.to_source(), vote_type="legislative", vote_member=member_votes)
						users_space.legislative_votes.add(membervotes)
						users_space.save()
				elif loggedinauthor == users_space.author:
					for membervotes in users_space.legislative_votes.all():
						membervotes.delete()
					users_space.legislative_votes.add(vote_member)
				for member in users_space.legislative_members.all():
					users_space.legislative_members.remove(member)
				for author in users_space.legislative_votes.all():
					author_count = []
					count = []
					if author in author_count:
						count[author_count.index(author.voter)] += 1
					else:
						author_count.append(author.voter)
						count.append(1)

					idx = np.array(count).argsort()[::-1][:5]
					for x in idx:
						users_space.legislative_members.add(author_count[x])
					users_space.save()
			else:
				return HttpResponse(vote_for_legislative_form.errors)
	
	return base_redirect(request, 0)


@login_required
def vote_for_administrative(request, space):
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		users_space = Space.objects.get(id=int(space))
		
		if request.method == "POST":
			vote_for_administrative_form = VoteForAdministrativeForm(users_space, data=request.POST)
			if vote_for_administrative_form.is_valid():
				vote_member = Author.objects.get(username=vote_for_administrative_form.cleaned_data['administrative_members'])
				if loggedinauthor in users_space.approved_voters.all():
					if users_space.administrative_votes.filter(voter=loggedinauthor).count():
						membervotes = users_space.administrative_votes.filter(voter=loggedinauthor)[0]
						member_votes.vote_member = vote_member
						member_votes.save()
					else:
						membervotes = MemberVotes.objects.create(voter=loggedinauthor, space=users_space.to_source(), vote_type="administrative", vote_member=member_votes)
						users_space.administrative_votes.add(membervotes)
						users_space.save()
				elif loggedinauthor == users_space.author:
					for membervotes in users_space.administrative_votes.all():
						membervotes.delete()
					users_space.administrative_votes.add(vote_member)
				for member in users_space.administrative_members.all():
					users_space.administrative_members.remove(member)
				for author in users_space.administrative_votes.all():
					author_count = []
					count = []
					if author in author_count:
						count[author_count.index(author.voter)] += 1
					else:
						author_count.append(author.voter)
						count.append(1)

					idx = np.array(count).argsort()[::-1][:5]
					for x in idx:
						users_space.administrative_members.add(author_count[x])
					users_space.save()
			else:
				return HttpResponse(vote_for_administrative_form.errors)
	
	return base_redirect(request, 0)


@login_required
def vote_for_executive(request, space):
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		users_space = Space.objects.get(id=int(space))
		
		if request.method == "POST":
			vote_for_executive_form = VoteForExecutiveForm(users_space, data=request.POST)
			if vote_for_executive_form.is_valid():
				vote_member = Author.objects.get(username=vote_for_executive_form.cleaned_data['executive_members'])
				if loggedinauthor in users_space.approved_voters.all():
					if users_spaceexecuative_votes.filter(voter=loggedinauthor).count():
						membervotes = users_space.executive_votes.filter(voter=loggedinauthor)[0]
						member_votes.vote_member = vote_member
						member_votes.save()
					else:
						membervotes = MemberVotes.objects.create(voter=loggedinauthor, space=users_space.to_source(), vote_type="executive", vote_member=member_votes)
						users_space.executive_votes.add(membervotes)
						users_space.save()
				elif loggedinauthor == users_space.author:
					for membervotes in users_space.executive_votes.all():
						membervotes.delete()
					users_space.executive_votes.add(vote_member)
				for member in users_space.executive_members.all():
					users_space.executive_members.remove(member)
				for author in users_space.executive_votes.all():
					author_count = []
					count = []
					if author in author_count:
						count[author_count.index(author.voter)] += 1
					else:
						author_count.append(author.voter)
						count.append(1)

					idx = np.array(count).argsort()[::-1][:5]
					for x in idx:
						users_space.executive_members.add(author_count[x])
					users_space.save()
			else:
				return HttpResponse(vote_for_executive_form.errors)
	
	return base_redirect(request, 0)


@login_required
def vote_for_judiciary(request, space):
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		users_space = Space.objects.get(id=int(space))
		
		if request.method == "POST":
			vote_for_judiciary_form = VoteForJudiciaryForm(users_space, data=request.POST)
			if vote_for_judiciary_form.is_valid():
				vote_member = Author.objects.get(username=vote_for_judiciary_form.cleaned_data['judiciary_members'])
				if loggedinauthor in users_space.approved_voters.all():
					if users_space.judiciary_votes.filter(voter=loggedinauthor).count():
						member_votes = users_space.judiciary_votes.filter(voter=loggedinauthor)[0]
						member_votes.vote_member = vote_member
						member_votes.save()
					else:
						membervotes = MemberVotes.objects.create(voter=loggedinauthor, space=users_space.to_source(), vote_type="judiciary", vote_member=vote_member)
						users_space.judiciary_votes.add(membervotes)
						users_space.save()
				elif loggedinauthor == users_space.author:
					for membervotes in users_space.judiciary_votes.all():
						membervotes.delete()
					users_space.judiciary_votes.add(vote_member)
				for member in users_space.judiciary_members.all():
					users_space.judiciary_members.remove(member)
				for author in users_space.judiciary_votes.all():
					author_count = []
					count = []
					if author in author_count:
						count[author_count.index(author.voter)] += 1
					else:
						author_count.append(author.voter)
						count.append(1)

					idx = np.array(count).argsort()[::-1][:5]
					for x in idx:
						users_space.judiciary_members.add(author_count[x])
					users_space.save()

			else:
				return HttpResponse(vote_for_judiciary_form.errors)
	
	return base_redirect(request, 0)





def tob_post(request, post):
	users_post = Post.objects.get(id=int(post))
	
	posts_comments = users_post.comments.order_by('-viewcount')[:25]
	users_post.viewcount += 1
	if users_post.spaces.count():
		for space in users_post.spaces.all():
			full_space = space.to_full()
			full_space.posts_viewcount += 1
			full_space.save()
	users_post.save()

	page_views, created = Pageviews.objects.get_or_create(page="tob_post")
	page_views.views += 1
	page_views.save()

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		x_forwarded_for = x_forwarded_for.split(',')[0]
	ip = request.META.get('REMOTE_ADDR')


	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		previous_view = UserViews.objects.filter(anon=loggedinanon).order_by('view_date').first()
		pages_view = UserViews.objects.create(page_view="tob_post__"+post, anon=loggedinanon)
		page_views.user_views.add(pages_view)
		if previous_view:
			pages_view.previous_view_id = previous_view.id
			pages_view.previous_page = previous_view.page_view
			pages_view.previous_view_date = previous_view.view_date
			pages_view.previous_view_time_between_pages = datetime.datetime.now(timezone.utc) - previous_view.view_date
		

		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
	
		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		file_form = FileForm() 
		the_response = render(request, "tob_post.html", {"ip": ip, "x_forwarded_for": x_forwarded_for, "file_form": file_form, "loggedinanon": loggedinanon, "users_post": users_post, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_post.html", {"ip": ip, "x_forwarded_for": x_forwarded_for, "users_post": users_post, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_post')
	the_response.set_cookie('post', post)
	the_response.set_cookie('count', 0)
	return the_response

@login_required
def tob_sponsor_product(request, product_id):
	users_product = Price.objects.get(id=int(product_id))
	if not users_product.anon_user_id:

		user_anon = Anon.objects.filter(products=int(product_id)).first()
	else:
		user_anon = Anon.objects.get(id=users_product.anon_user_id)
	
	
	page_views, created = Pageviews.objects.get_or_create(page="tob_sponsor_product")
	page_views.views += 1
	page_views.save()

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		x_forwarded_for = x_forwarded_for.split(',')[0]
	ip = request.META.get('REMOTE_ADDR')


	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)


		if request.method == "POST":
			sponsor_form = SponsorForm(request.POST)
			insert_sponsor_form = InsertSponsorForm(request, request.POST)
			if sponsor_form.is_valid():
				if sponsor_form.cleaned_data["allowable_expenditure"] <= loggedinanon.false_wallet:
					loggedinanon.false_wallet -= sponsor_form.cleaned_data["allowable_expenditure"]
					new_spon = Sponsor.objects.create(payperview=sponsor_form.cleaned_data['payperview'], allowable_expenditure=sponsor_form.cleaned_data["allowable_expenditure"], the_sponsorship_phrase=sponsor_form.cleaned_data['the_sponsorship_phrase'], img=sponsor_form.cleaned_data['img'], url2=sponsor_form.cleaned_data['url2'], price_limit=sponsor_form.cleaned_data['price_limit'], author=loggedinauthor)
					users_product.sponsors.add(new_spon)
					users_product.save()
					request.COOKIES['current'] = 'tob_users_spaces_sponsor'
					request.COOKIES['viewing_user'] = user
					request.COOKIES['space_id'] = users_space.id
					request.COOKIES['sponsor'] = new_spon.id
				elif insert_sponsor_form.is_valid():
					if insert_sponsor_form.cleaned_data['identifier'] != 0:
						new_spon = Sponsor.objects.get(id=insert_sponsor_form.cleaned_data['identifier'])
						if new_spon.author == request.user.username:
							users_product.sponsors.add(new_spon)
							users_product.save()
				else:
					return HttpResponse("not enough balance")
				#return base_redirect(request, 0)
			print('here')
			if insert_sponsor_form.is_valid():
				if not Sponsor.objects.get(id=insert_sponsor_form.cleaned_data["identifier"]):
					return HttpResponse("not a sponsor id.")
				old_spon = Sponsor.objects.get(id=insert_sponsor_form.cleaned_data["identifier"])
				users_product.sponsors.add(old_spon)
				users_product.save()
				request.COOKIES['current'] = 'tob_product'
				request.COOKIES['viewing_user'] = user
				request.COOKIES['product'] = users_product.id
				request.COOKIES['sponsor'] = old_spon.id
				
				#return base_redirect(request, 0)
		
		previous_view = UserViews.objects.filter(anon=loggedinanon).order_by('view_date').first()
		pages_view = UserViews.objects.create(page_view="tob_sponsor_product__"+product_id, anon=loggedinanon)
		page_views.user_views.add(pages_view)
		if previous_view:
			pages_view.previous_view_id = previous_view.id
			pages_view.previous_page = previous_view.page_view
			pages_view.previous_view_date = previous_view.view_date
			pages_view.previous_view_time_between_pages = datetime.datetime.now(timezone.utc) - previous_view.view_date
		

		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
	
		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		file_form = FileForm() 
		the_response = render(request, "tob_product.html", {"ip": ip, "x_forwarded_for": x_forwarded_for, "file_form": file_form, "loggedinanon": loggedinanon, "user_anon": user_anon, "users_product": users_product, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_product.html", {"ip": ip, "x_forwarded_for": x_forwarded_for, "users_product": users_product, "user_anon": user_anon, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_post')
	the_response.set_cookie('post', product_id)
	the_response.set_cookie('count', 0)
	return the_response



def tob_product(request, product_id):
	users_product = Price.objects.get(id=int(product_id))
	if not users_product.anon_user_id:

		user_anon = Anon.objects.filter(products=int(product_id)).first()
	else:
		user_anon = Anon.objects.get(id=users_product.anon_user_id)
	
	page_views, created = Pageviews.objects.get_or_create(page="tob_product")
	page_views.views += 1
	page_views.save()

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		x_forwarded_for = x_forwarded_for.split(',')[0]
	ip = request.META.get('REMOTE_ADDR')


	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		previous_view = UserViews.objects.filter(anon=loggedinanon).order_by('view_date').first()
		pages_view = UserViews.objects.create(page_view="tob_product__"+product_id, anon=loggedinanon)
		page_views.user_views.add(pages_view)
		if previous_view:
			pages_view.previous_view_id = previous_view.id
			pages_view.previous_page = previous_view.page_view
			pages_view.previous_view_date = previous_view.view_date
			pages_view.previous_view_time_between_pages = datetime.datetime.now(timezone.utc) - previous_view.view_date
		

		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
	
		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		sponsor_form = SponsorForm()
	
		file_form = FileForm() 
		the_response = render(request, "tob_product.html", {"sponsor_form":sponsor_form,"ip": ip, "x_forwarded_for": x_forwarded_for, "file_form": file_form, "loggedinanon": loggedinanon, "user_anon": user_anon, "users_product": users_product, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_product.html", {"ip": ip, "x_forwarded_for": x_forwarded_for, "users_product": users_product, "user_anon": user_anon, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_post')
	the_response.set_cookie('post', product_id)
	the_response.set_cookie('count', 0)
	return the_response







def tob_spaces_post(request, space, post, count):
	tob_space = Space.objects.get(id=space)[:100]
	tob_post = tob_space.posts.get(id=post)[:100]
	count = int(count)
	posts_comments = tob_post.comments.order_by('viewcount')[count:count+100]
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	
	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		previous_view = UserViews.objects.filter(anon=loggedinanon).order_by('view_date').first()
		pages_view = UserViews.objects.create(page_view="tob_spaces_post__"+space+"__"+post, anon=loggedinanon)
		page_views.user_views.add(pages_view)
		if previous_view:
			pages_view.previous_view_id = previous_view.id
			pages_view.previous_page = previous_view.page_view
			pages_view.previous_view_date = previous_view.view_date
			pages_view.previous_view_time_between_pages = datetime.datetime.now(timezone.utc) - previous_view.view_date
		

		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
	
		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

	if request.user.is_authenticated:
		the_response = render(request, "tob_spaces_post.html", {"loggedinanon": loggedinanon, "tob_space": tob_space, "tob_post": tob_post, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_spaces_post.html", {"tob_space": tob_space, "tob_post": tob_post, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_spaces_post')
	the_response.set_cookie('space', space)
	the_response.set_cookie('post', post)
	the_response.set_cookie('count', 0)
	return the_response

def tob_spaces_post_count(request, space, post, count):
	count = int(count)
	tob_space = Spaces.objects.get(id=space)[count:count+100]
	tob_post = tob_space.posts.get(id=post)[count:count+100]
	
	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
	
		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
	
	
	if request.user.is_authenticated:
		the_response = render(request, "tob_spaces_post.html", {"loggedinanon": loggedinanon, "tob_space": tob_space, "tob_post": tob_post, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_spaces_post.html", {"tob_space": tob_space, "tob_post": tob_post, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_spaces_post_count')
	the_response.set_cookie('space', space)
	the_response.set_cookie('post', post)
	the_response.set_cookie('count', count)
	return the_response

def tob_spaces_posts_comment(request, space, post, comment):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)

	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
	
	users_spaces = user_anon.spaces
	if users_spaces is not None:
		users_spaces = user_anon.spaces.order_by('-latest_change_date')[:25]
	users_posts = user_anon.posts
	if users_posts is not None:
		users_posts = user_anon.posts.order_by('-latest_change_date')[:25]
	users_dictionaries = user_anon.dictionaries
	if users_dictionaries is not None:
		users_dictionaries = user_anon.dictionaries.order_by('-latest_change_date')[:25]
	users_examples = user_anon.examples
	if users_examples is not None:
		users_examples = user_anon.examples.order_by('-latest_change_date')[:25]


	
	
	
	if request.user.is_authenticated:
		the_response = render(request, "tob_spaces_posts_comment.html", {"loggedinanon": loggedinanon, "users_dictionaries": users_dictionaries, "users_examples": users_examples, "users_posts": users_posts, "users_space": users_spaces, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_spaces_posts_comment.html", {"users_dictionaries": users_dictionaries, "users_examples": users_examples, "users_posts": users_posts, "users_space": users_spaces, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_spaces_posts_comment')
	the_response.set_cookie('space', space)
	the_response.set_cookie('post', post)
	the_response.set_cookie('comment', comment)
	the_response.set_cookie('count', 0)
	return the_response

def tob_spaces_posts_comment_count(request, space, post, comment, count):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)

	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
	
	users_spaces = user_anon.spaces
	if users_spaces is not None:
		users_spaces = user_anon.spaces.order_by('-latest_change_date')[:25]
	users_posts = user_anon.posts
	if users_posts is not None:
		users_posts = user_anon.posts.order_by('-latest_change_date')[:25]
	users_dictionaries = user_anon.dictionaries
	if users_dictionaries is not None:
		users_dictionaries = user_anon.dictionaries.order_by('-latest_change_date')[:25]
	users_examples = user_anon.examples
	if users_examples is not None:
		users_examples = user_anon.examples.order_by('-latest_change_date')[:25]
	
	
	
	if request.user.is_authenticated:
		the_response = render(request, "tob_spaces_posts_comment.html", {"loggedinanon": loggedinanon, "users_dictionaries": users_dictionaries, "users_examples": users_examples, "users_posts": users_posts, "users_space": users_spaces, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_spaces_posts_comment.html", {"users_dictionaries": users_dictionaries, "users_examples": users_examples, "users_posts": users_posts, "users_space": users_spaces, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_spaces_posts_comment_count')
	the_response.set_cookie('space', space)
	the_response.set_cookie('post', post)
	the_response.set_cookie('comment', comment)
	the_response.set_cookie('count', count)
	return the_response


@login_required
def change_anon_sort_char(request):
	if request.method == "POST":
		anon_sort_form = AnonSortForm(request, data=request.POST)
		if anon_sort_form.is_valid():
			anon_sort_form.save()
	return base_redirect(request, 0)

@login_required
def change_dic_sort_char(request):
	if request.method == "POST":
		dic_sort_form = DicSortForm(request, data=request.POST)
		if dic_sort_form.is_valid():
			dic_sort_form.save()
	return base_redirect(request, 0)

@login_required
def change_word_sort_char(request):
	if request.method == "POST":
		word_sort_form = WordSortForm(request, data=request.POST)
		if word_sort_form.is_valid():
			word_sort_form.save()
	return base_redirect(request, 0)

@login_required
def change_attribute_sort_char(request):
	if request.method == "POST":
		attribute_sort_form = AttributeSortForm(request, data=request.POST)
		if attribute_sort_form.is_valid():
			attribute_sort_form.save()
	return base_redirect(request, 0)



@login_required
def change_space_sort_char(request):
	if request.method == "POST":
		space_sort_form = SpaceSortForm(request, data=request.POST)
		if space_sort_form.is_valid():
			space_sort_form.save()
	return base_redirect(request, 0)


@login_required
def change_post_sort_char(request):
	if request.method == "POST":
		post_sort_form = PostSortForm(request, data=request.POST)
		if post_sort_form.is_valid():
			post_sort_form.save()
	return base_redirect(request, 0)


def tob_view_users(request):

	user_anons = Anon.objects.order_by('-latest_change_date')[:25]
	count = 0 
	mcount = 0
	count100 = 25
	registerform = UserCreationForm()
	
	user_anons_count = Anon.objects.count()
	page_views, created = Pageviews.objects.get_or_create(page="tob_view_users")
	page_views.views += 1
	page_views.save()	
	
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		previous_view = UserViews.objects.filter(anon=loggedinanon).order_by('view_date').first()
		pages_view = UserViews.objects.create(page_view="tob_view_users", anon=loggedinanon)
		page_views.user_views.add(pages_view)
		if previous_view:
			pages_view.previous_view_id = previous_view.id
			pages_view.previous_page = previous_view.page_view
			pages_view.previous_view_date = previous_view.view_date
			pages_view.previous_view_time_between_pages = datetime.datetime.now(timezone.utc) - previous_view.view_date
		

		user_anons = Anon.objects.order_by(loggedinanon.anon_sort_char)[0:25]

		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		anon_sort_form = AnonSortForm(request)
	


	
	
	if request.user.is_authenticated:
		the_response = render(request, "tob_view_users.html", {"user_anons_count": user_anons_count, "anon_sort_form": anon_sort_form, "count": count, "mcount": mcount, "count100": count100, "loggedinanon": loggedinanon, "user_anons": user_anons, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_view_users.html", {"user_anons_count": user_anons_count, "count": count, "mcount": mcount, "count100": count100, "user_anons": user_anons, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_view_users')
	the_response.set_cookie('count', 0)
	return the_response

def tob_view_users_count(request, count):
	count = int(count)
	count100 = count + 25
	user_anons = Anon.objects.order_by('-latest_change_date')[count:count100]
	#if request.user.is_authenticated:
	if count > 25:
		mcount = count - 25
	else:
		mcount = 0
	#	if user_anons is not None:
	registerform = UserCreationForm()
	
	user_anons_count = Anon.objects.count()
	page_views, created = Pageviews.objects.get_or_create(page="tob_view_users_count")
	page_views.views += 1
	page_views.save()	
	
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		user_anons = Anon.objects.order_by(loggedinanon.anon_sort_char)[count:count100]

		previous_view = UserViews.objects.filter(anon=loggedinanon).order_by('view_date').first()
		pages_view = UserViews.objects.create(page_view="tob_view_users_count__"+str(count), anon=loggedinanon)
		page_views.user_views.add(pages_view)
		if previous_view:
			pages_view.previous_view_id = previous_view.id
			pages_view.previous_page = previous_view.page_view
			pages_view.previous_view_date = previous_view.view_date
			pages_view.previous_view_time_between_pages = datetime.datetime.now(timezone.utc) - previous_view.view_date
		


		dic_form = DictionaryForm()
		post_form = PostForm(request)
		space_form = SpaceForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
	
		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		anon_sort_form = AnonSortForm(request)

		the_response = render(request, "tob_view_users.html", {"user_anons_count": user_anons_count, "anon_sort_form": anon_sort_form, "count": count, "mcount": mcount, "count100": count100, "loggedinanon": loggedinanon, "user_anons": user_anons, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_view_users.html", {"user_anons_count": user_anons_count, "count": count, "mcount": mcount, "count100": count100, "user_anons": user_anons, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_view_users_count')
	the_response.set_cookie('count', count)
	return the_response

def tob_user_view(request, user, count=0):
	# Takes in the user object and collects lists to be displayed, totalling 100
	# Each must be checked, if any exist, HTML doc displays an IF with a message for each
	# if so, they are then ordered in the feasible ways saved for each anon
	# CHANGE SORTING TO . < function intrinsic to the object


	count = int(count)
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

	if User.objects.filter(username=user).count():
		user_themself, created = User.objects.get_or_create(username=user[0:149])
		user_author, created = Author.objects.get_or_create(username=user[0:149])
		user_anon = user_author.to_anon()
	else:
		user_themself, created = User.objects.get_or_create(username=user[0:149])
		user_author, created = Author.objects.get_or_create(username=user[0:149])
		user_anon = user_author.to_anon()
	
	
	users_spaces = user_anon.spaces.all()
	if users_spaces is not None:
		users_spaces = user_anon.spaces.filter(Q(for_sale=True)|Q(approved_voters__username=request.user.username))
		if request.user.is_authenticated:
			users_spaces = users_spaces.order_by(loggedinanon.space_sort_char)[count:count+25]
		else:
			users_spaces = user_anon.spaces.order_by('viewcount')[count:count+25]
	if request.user.username == user or request.user.username == 'test':
		users_spaces = user_anon.spaces.order_by(loggedinanon.space_sort_char)[count:count+25]
	


	anons_posts = Post.objects.all().filter(author=Author.objects.get(username=user[0:149]))
	for post in anons_posts:
		user_anon.posts.add(post)
	

	users_posts = user_anon.posts.count()
	if users_posts:
		if request.user.is_authenticated:
			users_posts = user_anon.posts.filter(Q(dictionaries__in=loggedinanon.purchased_dictionaries.all())|Q(dictionaries=None))
			users_posts = user_anon.posts.order_by(loggedinanon.post_sort_char)[count:25]
			
		else:
			users_posts = user_anon.posts.order_by('viewcount')[count:count+25]
	if request.user.username == user or request.user.username == 'test':
		users_posts = user_anon.posts.order_by(loggedinanon.post_sort_char)[count:25]
		
	'''
	# Dictionary contains: author, for_sale, views, 
	users_dictionaries = user_anon.dictionaries.filter(Q(for_sale=True)|Q(public=True))
	if users_dictionaries is not None:
		if request.user.is_authenticated:
			if users_dictionaries.filter(purchase_orders__author=loggedinauthor):
				users_dictionaries = users_dictionaries.filter(purchase_orders__author=loggedinauthor)
			users_dictionaries = user_anon.dictionaries.filter(Q(for_sale=True)|Q(author=loggedinauthor))
			users_dictionaries = sort_dictionaries(users_dictionaries, loggedinanon.dictionary_sort, count, 25)
		else:
			users_dictionaries.order_by('viewcount')[count:count+25]
	if request.user.username == user or request.user.username == 'test':
		users_dictionaries = sort_dictionaries(user_anon.dictionaries.all(), loggedinanon.dictionary_sort, count, 25)
	
	users_examples = 0
	if user_anon.examples.count():
		users_examples = user_anon.examples.filter(dictionaries__the_dictionary_itself__in=loggedinanon.purchased_dictionaries.all().values_list('the_dictionary_itself'))
		if request.user.is_authenticated:
			users_examples = sort_examples(user_anon.examples.all(), loggedinanon.example_sort, count, 25)
		else:
			users_examples.order_by('viewcount')[count:count+25]

	users_posted_comments = user_anon.posted_comments.all()
	if users_posted_comments is not None:
		if request.user.is_authenticated:
			users_posted_comments = sort_comments(users_posted_comments, loggedinanon.comment_sort, count, 25)
		else:
			users_posted_comments = sort_comments(users_posted_comments, 14, count, 25)

	users_sponsors = Sponsor.objects.filter(author=user_author)
	if users_sponsors is not None:
		if request.user.is_authenticated:
			users_sponsors = sort_sponsors(users_sponsors, loggedinanon.sponsor_sort, count, 25)
		else:
			users_sponsors = users_sponsors.order_by('price_limit')[count:count+25]
	'''

	'''
		Django, when calling and .order_by, sorts None into Error, rather than into None.
			THAT MUST BE FIXED - ReTaRdS, wouldn't get anywhere with creating the universe.
			So may aswell force 'migrate' to run 'migrate --run-syncdb' and 'makemigrations' beforehand.
	'''
	
	page_views, created = Pageviews.objects.get_or_create(page="tob_user_view")
	page_views.views += 1
	page_views.save()	
	
	total = 0
	for page in Pageviews.objects.all():
		total += page.views
	# Forms for entry on the view of a user of public model entry-points, 
	# each must have a respective submission point, ie. redirection url and therefore view.
	# they can be general (also redirected to by other views,) or specific (redirected from only this)

	# General
	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		bread_form = BreadForm()

		wallet_form = MoneroWalletForm()

		
		
		#apply_votestyle_form = ApplyVotestyleForm(request)
		apply_votes_form = VoteIntoVoteStyleForm()
		#exclude_votes_form = ExcludeVoteStyleForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		file_form = FileForm()
		email_form = EmailForm()
		post_sort_form = PostSortForm(request)


		#dic_names = []
		#for dic in loggedinanon.dictionaries.all: 
		#	dic_names += [dic.the_dictionary_itself]
		#word_form.fields["home_dictionary"].queryset = Dictionary_Source.objects.filter(author=loggedinauthor).values_list('the_dictionary_itself', flat=True)	# Specific
		comment_form = CommentForm(request) # Make in template {% if loggedin %}
	
	if request.user.is_authenticated:
		the_response = render(request, "tob_user_view.html", {"post_sort_form": post_sort_form, "email_form": email_form, "file_form": file_form, "wallet_form": wallet_form, "total": total, "loggedinanon": loggedinanon, "users_posts": users_posts, "users_spaces": users_spaces, "user_anon": user_anon, 
			"bread_form": bread_form,"dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "apply_votes_form": apply_votes_form, "comment_form": comment_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_user_view.html", {"total": total, "users_posts": users_posts, "users_spaces": users_spaces, "user_anon": user_anon, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_user_view_count')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('count', count)
	return the_response


def u(request, user):
	user_id = User.objects.get(username=user)
	return redirect('Bable:tob_user_view', user_id.username)

def tob_user_view_count(request, user, count=0):
	# Takes in the user object and collects lists to be displayed, totalling 100
	# Each must be checked, if any exist, HTML doc displays an IF with a message for each
	# if so, they are then ordered in the feasible ways saved for each anon
	# CHANGE SORTING TO . < function intrinsic to the object
	count = int(count)
	registerform = UserCreationForm()
	
	page_views, created = Pageviews.objects.get_or_create(page="tob_user_view_count")
	page_views.views += 1
	page_views.save()	
	
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

	if User.objects.filter(username=user).count():
		user_themself, created = User.objects.get_or_create(username=user)
		user_author, created = Author.objects.get_or_create(username=user_themself.username)
		user_anon = user_author.to_anon()
	else:
		user_themself, created = User.objects.get_or_create(username=user)
		user_author, created = Author.objects.get_or_create(username=user_themself.username)
		user_anon = user_author.to_anon()
	
	
	users_spaces = user_anon.spaces.all()
	if users_spaces is not None:
		users_spaces = user_anon.spaces.filter(Q(for_sale=True)|Q(approved_voters__username=request.user.username))
		if request.user.is_authenticated:
			users_spaces = users_spaces.order_by(loggedinanon.space_sort_char)[count:count+25]
		else:
			users_spaces = user_anon.spaces.order_by('viewcount')[count:count+25]
	


	anons_posts = Post.objects.all().filter(author=user_author)
	for post in anons_posts:
		user_anon.posts.add(post)
	


	users_posts = user_anon.posts.count()
	if users_posts:
		if request.user.is_authenticated:
			#users_posts = user_anon.posts.filter(Q(dictionaries__in=loggedinanon.purchased_dictionaries.all())|Q(dictionaries=None))
			users_posts = user_anon.posts.filter(Q(dictionaries__in=loggedinanon.purchased_dictionaries.all())|Q(dictionaries=None)).order_by(loggedinanon.post_sort_char)[count:25]
			
		else:
			users_posts = user_anon.posts.order_by('viewcount')[count:count+25]
	if request.user.username == user or request.user.username == 'test':
		users_posts = user_anon.posts.order_by(loggedinanon.post_sort_char)[count:25]
	# Dictionary contains: author, for_sale, views, 
	'''
	users_dictionaries = user_anon.dictionaries.filter(Q(for_sale=True)|Q(public=True))
	if request.user.username == user or request.user.username == 'test':
		users_dictionaries = user_anon.dictionaries
	if users_dictionaries is not None:
		if request.user.is_authenticated:
			if users_dictionaries.filter(purchase_orders__author=loggedinauthor):
				users_dictionaries = users_dictionaries.filter(purchase_orders__author=loggedinauthor)
			users_dictionaries = user_anon.dictionaries.filter(Q(for_sale=True)|Q(author=loggedinauthor))
			users_dictionaries = sort_dictionaries(users_dictionaries, loggedinanon.dictionary_sort, count, 25)
		else:
			users_dictionaries.order_by('viewcount')[count:count+25]

	users_examples = 0
	if user_anon.examples.count():
		users_examples = user_anon.examples.filter(dictionaries__the_dictionary_itself__in=loggedinanon.purchased_dictionaries.all().values_list('the_dictionary_itself'))
		if request.user.is_authenticated:
			users_examples = sort_examples(user_anon.examples.all(), loggedinanon.example_sort, count, 25)
		else:
			users_examples.order_by('viewcount')[count:count+25]

	users_posted_comments = user_anon.posted_comments.all()
	if users_posted_comments is not None:
		if request.user.is_authenticated:
			users_posted_comments = sort_comments(users_posted_comments, loggedinanon.comment_sort, count, 25)
		else:
			users_posted_comments = sort_comments(users_posted_comments, 14, count, 25)

	users_sponsors = Sponsor.objects.filter(author=user_author)
	users_sponsors_count = users_sponsors.count()
	if users_sponsors is not None:
		if request.user.is_authenticated:
			users_sponsors = sort_sponsors(users_sponsors, loggedinanon.sponsor_sort, count, 25)
		else:
			users_sponsors = users_sponsors.order_by('price_limit')[count:count+25]
	'''

	'''
		Django, when calling and .order_by, sorts None into Error, rather than into None.
			THAT MUST BE FIXED - ReTaRdS, wouldn't get anywhere with creating the universe.
			So may aswell force 'migrate' to run 'migrate --run-syncdb' and 'makemigrations' beforehand.
	'''
	
	
	total = 0
	for page in Pageviews.objects.all():
		total += page.views
	# Forms for entry on the view of a user of public model entry-points, 
	# each must have a respective submission point, ie. redirection url and therefore view.
	# they can be general (also redirected to by other views,) or specific (redirected from only this)

	# General
	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		bread_form = BreadForm()

		
		
		#apply_votestyle_form = ApplyVotestyleForm(request)
		apply_votes_form = VoteIntoVoteStyleForm()
		wallet_form = MoneroWalletForm()
		#exclude_votes_form = ExcludeVoteStyleForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		email_form = EmailForm()
		file_form = FileForm()
		post_sort_form = PostSortForm(request)

		#dic_names = []
		#for dic in loggedinanon.dictionaries.all: 
		#	dic_names += [dic.the_dictionary_itself]
		#word_form.fields["home_dictionary"].queryset = Dictionary_Source.objects.filter(author=loggedinauthor).values_list('the_dictionary_itself', flat=True)	# Specific
		#comment_form = CommentForm(request, value_from_object) # Make in template {% if loggedin %}
	
	if request.user.is_authenticated:
		the_response = render(request, "tob_user_view.html", {"post_sort_form": post_sort_form, "file_form": file_form, "email_form": email_form, "wallet_form": wallet_form, "total": total, "loggedinanon": loggedinanon, "users_posts": users_posts, "users_spaces": users_spaces, "user_anon": user_anon, 
			"bread_form": bread_form,"dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "apply_votes_form": apply_votes_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_user_view.html", {"total": total, "users_posts": users_posts, "users_spaces": users_spaces, "user_anon": user_anon, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_user_view_count')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('count', count)
	return the_response


def tob_users_spaces(request, user, count):
	count = int(count)
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)

	registerform = UserCreationForm()
	
	page_views, created = Pageviews.objects.get_or_create(page="tob_users_spaces")
	page_views.views += 1
	page_views.save()	
	
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
	
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	
	users_spaces = user_anon.spaces
	if users_spaces is not None:
		users_spaces = user_anon.spaces.filter(Q(for_sale=True)|Q(approved_voters__username=request.user.username))
		if request.user.is_authenticated:
			users_spaces = users_spaces.order_by(loggedinanon.space_sort_char)[count:count+25]
		else:
			users_spaces = user_anon.spaces.order_by('viewcount')[count:count+100]
	
	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		the_response = render(request, "tob_users_spaces.html", {"loggedinanon": loggedinanon, "users_spaces": users_spaces, "user_anon": user_anon, "space_form": space_form, "dic_form": dic_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_spaces.html", {"users_spaces": users_spaces, "user_anon": user_anon, "registerform": registerform,  "loginform": loginform})

	the_response.set_cookie('current', 'tob_users_spaces')
	the_response.set_cookie('viewing_user', user)
	return the_response

def tob_users_sponsor(request, user, sponsor):
	sponsor = int(sponsor)
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	user_author = Author.objects.get(username=user)
	
	users_sponsors = Sponsor.objects.filter(author=user_author)
	users_sponsor = False
	if not int(sponsor) == 0:
		users_sponsor = Sponsor.objects.get(id=int(sponsor))



	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		comment_form = CommentForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()


	users_sponsors = Sponsor.objects.filter(author=user_author)
	users_sponsor = False
	if not int(sponsor) == 0:
		users_sponsor = Sponsor.objects.get(id=int(sponsor))
	
	if request.user.is_authenticated:
		the_response = render(request, "tob_users_sponsor.html", {"loggedinanon": loggedinanon, "users_sponsors": users_sponsors, "users_sponsor": users_sponsor, "user_anon": user_anon, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_sponsor.html", {"user_anon": user_anon, "users_sponsors": users_sponsors, "users_sponsor": users_sponsor, "registerform": registerform,  "loginform": loginform})

	the_response.set_cookie('current', 'tob_users_sponsor')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('sponsor', sponsor)
	return the_response

def tob_users_sponsors(request, user, count):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	user_author = Author.objects.get(username=user)
	

	count = int(count)


	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		comment_form = CommentForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()


	users_sponsors = Sponsor.objects.filter(author=user_author)
	users_sponsors_count = users_sponsors.count()
	if users_sponsors is not None:
		if request.user.is_authenticated:
			users_sponsors = sort_sponsors(users_sponsors, loggedinanon.sponsor_sort, count, 25)
		else:
			users_sponsors = users_sponsors.order_by('price_limit')[count:count+25]

	if request.user.is_authenticated:
		the_response = render(request, "tob_users_sponsors.html", {"users_sponsors_count": users_sponsors_count, "loggedinanon": loggedinanon, "users_sponsors": users_sponsors, "user_anon": user_anon, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_sponsors.html", {"users_sponsors_count": users_sponsors_count, "user_anon": user_anon, "users_sponsors": users_sponsors, "users_sponsor": users_sponsor, "registerform": registerform,  "loginform": loginform})

	the_response.set_cookie('current', 'tob_users_sponsors')
	the_response.set_cookie('viewing_user', user)
	return the_response


def tob_users_space(request, user, space_id, count):
	count = int(count)
	space_id = int(space_id)
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	user_author = Author.objects.get(username=user)
	




	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		comment_form = CommentForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		sponsor_form = SponsorForm()
		insert_sponsor_form = InsertSponsorForm(request)

		post_sort_form = PostSortForm(request)

	space_viewable = False
	users_space = Space.objects.get(id=space_id)
	spaces_dic = users_space.the_space_itself.home_dictionary.to_full()
	spaces_dic.views += 1
	spaces_dic.update_purchases
	spaces_dic.save()
	try:
		spaces_posts = users_space.posts.count()
		if request.user.is_authenticated:
			if not users_space.public:
				if request.user.username in users_space.approved_voters.all().values_list('username'):
					spaces_posts = users_space.posts.order_by(loggedinanon.post_sort_char)[count:count+25]
					space_viewable = True
				else:
					space_viewable = False
			else:
				spaces_posts = users_space.posts.order_by(loggedinanon.post_sort_char)[count:count+25]
				space_viewable = True
		else:
			if users_space.public:
				spaces_posts = users_space.posts.order_by('viewcount')[count:count+25]
				space_viewable = True
			else:
				space_viewable = False
	
	except ObjectDoesNotExist:
		users_space = Space.objects.get(id=space_id)
		spaces_posts = users_space.posts.count()
		if request.user.is_authenticated:
			if not users_space.public:
				if request.user.username in users_space.approved_voters.all().values_list('username'):
					spaces_posts = users_space.posts.order_by(loggedinanon.post_sort_char)[count:count+25]
					space_viewable = True
				else:
					space_viewable = False
			else:
				spaces_posts = users_space.posts.order_by(loggedinanon.post_sort_char)[count:count+25]
				space_viewable = True
		else:
			if users_space.public:
				spaces_posts = users_space.posts.order_by('viewcount')[count:count+25]
				space_viewable = True
			else:
				space_viewable = False

	if space_viewable:
		users_space.viewcount += 1
		users_space.save()


	if request.user.is_authenticated:
		space_edit_form = SpaceForm(request, instance=users_space)
		the_response = render(request, "tob_users_space.html", {"post_sort_form": post_sort_form, "space_viewable": space_viewable, "loggedinanon": loggedinanon, "sponsor_form": sponsor_form, "insert_sponsor_form": insert_sponsor_form, "spaces_posts": spaces_posts, "users_space": users_space, "user_anon": user_anon, "space_form": space_form, "space_edit_form": space_edit_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_space.html", {"spaces_posts": spaces_posts, "users_space": users_space, "user_anon": user_anon, "registerform": registerform,  "loginform": loginform})

	the_response.set_cookie('current', 'tob_users_space')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('space_id', space_id)
	the_response.set_cookie('count', count)
	return the_response


def tob_users_spaces_sponsor(request, user, space_id, sponsor):
	sponsor = int(sponsor)
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	user_author = Author.objects.get(username=user)
	




	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		comment_form = CommentForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		sponsor_form = SponsorForm()
		insert_sponsor_form = InsertSponsorForm(request)

	space_viewable = False
	users_space = Space.objects.get(id=int(space_id))
	space = users_space.the_space_itself.the_word_itself
	try:
		spaces_sponsors = users_space.sponsors.all()
		if not sponsor == 0:
			spaces_sponsor = Sponsor.objects.get(id=int(sponsor))
		else:
			spaces_sponsor = 0
		if spaces_sponsor is not None:
			if request.user.is_authenticated:
				if not users_space.public:
					if request.user.username in users_space.approved_voters.all().values_list('username'):
						space_viewable = True
					else:
						space_viewable = False
				else:
					space_viewable = True
			else:
				if users_space.public:
					space_viewable = True
				else:
					space_viewable = False
		
	except ObjectDoesNotExist:
		users_space = Space.objects.get(id=int(space_id))
		spaces_sponsors = users_space.sponsors.all()
		spaces_sponsor = Sponsor.objects.get(id=int(sponsor))
		if request.user.is_authenticated:
			if not users_space.public:
				if len(users_space.filter(approved_votters__username=request.user.username))>0:
					space_viewable = True
				else:
					space_viewable = False
			else:
				space_viewable = True
		else:
			if users_space.public:
				space_viewable = True
			else:
				space_viewable = False
	if request.user.username == user:
		space_viewable = True

	if request.method == "POST":
		sponsor_form = SponsorForm(request.POST)
		insert_sponsor_form = InsertSponsorForm(request, request.POST)
		if sponsor_form.is_valid():
			if sponsor_form.cleaned_data["allowable_expenditure"] <= loggedinanon.false_wallet:
				loggedinanon.false_wallet -= sponsor_form.cleaned_data["allowable_expenditure"]
				new_spon = Sponsor.objects.create(payperview=sponsor_form.cleaned_data['payperview'], allowable_expenditure=sponsor_form.cleaned_data["allowable_expenditure"], the_sponsorship_phrase=sponsor_form.cleaned_data['the_sponsorship_phrase'], img=sponsor_form.cleaned_data['img'], url2=sponsor_form.cleaned_data['url2'], price_limit=sponsor_form.cleaned_data['price_limit'], author=loggedinauthor)
				users_space.sponsors.add(new_spon)
				users_space.save()
				request.COOKIES['current'] = 'tob_users_spaces_sponsor'
				request.COOKIES['viewing_user'] = user
				request.COOKIES['space_id'] = users_space.id
				request.COOKIES['sponsor'] = new_spon.id
			elif insert_sponsor_form.is_valid():
				if insert_sponsor_form.cleaned_data['identifier'] != 0:
					new_spon = Sponsor.objects.get(id=insert_sponsor_form.cleaned_data['identifier'])
					if new_spon.author == request.user.username:
						users_space.sponsors.add(new_spon)
						users_space.save()
			else:
				return HttpResponse("not enough balance")
			return base_redirect(request, 0)
		print('here')
		if insert_sponsor_form.is_valid():
			if not Sponsor.objects.get(id=insert_sponsor_form.cleaned_data["identifier"]):
				return HttpResponse("not a sponsor id.")
			old_spon = Sponsor.objects.get(id=insert_sponsor_form.cleaned_data["identifier"])
			users_space.sponsors.add(old_spon)
			users_space.save()
			request.COOKIES['current'] = 'tob_users_spaces_sponsor'
			request.COOKIES['viewing_user'] = user
			request.COOKIES['space_id'] = users_space.id
			request.COOKIES['sponsor'] = old_spon.id
			
			return base_redirect(request, 0)
	else:
		if sponsor != 0:
			sponsor_form = SponsorForm(instance=Sponsor.objects.get(id=sponsor))

	if request.user.is_authenticated:
		space_edit_form = SpaceForm(request, instance=users_space)
		the_response = render(request, "tob_users_spaces_sponsor.html", {"loggedinanon": loggedinanon, "sponsor_form": sponsor_form, "insert_sponsor_form": insert_sponsor_form, "users_space": users_space, "space_viewable": space_viewable, "spaces_sponsor": spaces_sponsor, "spaces_sponsors": spaces_sponsors, "user_anon": user_anon, "space_form": space_form, "space_edit_form": space_edit_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_spaces_sponsor.html", {"spaces_posts": spaces_posts, "users_space": users_space, "space_viewable": space_viewable, "user_anon": user_anon, "registerform": registerform,  "loginform": loginform})

	the_response.set_cookie('current', 'tob_users_spaces_sponsor')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('space_id', users_space.id)
	the_response.set_cookie('sponsor', 0)
	return the_response


def tob_users_spaces_post(request, user, space_id, post_id):
	space_id = int(space_id)
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
	
	user_author = Author.objects.get(username=user)
	latest_edit = 0
	
	space_viewable = False
	users_space = Space.objects.get(author=user_author, id=space_id)
	spaces_post = Post.objects.get(id=int(post_id))
	if spaces_post.edits.count():
		latest_edit = spaces_post.edits.last()
	
	posts_comments = spaces_post.comments.count()
	
	users_space.posts_viewcount += 1
	users_space.save()

	if not users_space.public:
		if request.user.is_authenticated:
			if len(users_space.filter(approved_voters=loggedinauthor))>0:
				space_viewable = True
				posts_comments = spaces_post.comments.order_by(loggedinanon.comment_sort_char)[0:100]
				
				#
			else:
				space_viewable = False
	else:
		space_viewable = True
		if request.user.is_authenticated:
			posts_comments = spaces_post.comments.order_by(loggedinanon.comment_sort_char)[0:100]
		else:
			posts_comments = spaces_post.comments.all()[0:100]
	

	#General
	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		comment_form = CommentForm(request)
		sponsor_form = SponsorForm()
		#translation_dictionaries_queryset = loggedinanon.applied_dictionaries
		#translation_words_queryset = Word.objects.filter(home_dictionary=loggedinanon.applied_dictionaries[0])

		the_response = render(request, "tob_users_spaces_post.html", {"sponsor_form": sponsor_form, "comment_form": comment_form, "space_viewable": space_viewable, "latest_edit": latest_edit, "user_anon": user_anon, "loggedinanon": loggedinanon, "spaces_post": spaces_post, "users_space": users_space, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_spaces_post.html", {"space_viewable": space_viewable, "latest_edit": latest_edit, "spaces_post": spaces_post, "users_space": users_space, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_spaces_post')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('space', space_id)
	the_response.set_cookie('post', post_id)
	return the_response
	

def tob_users_spaces_post_count(request, user, space, post, count):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	
	registerform = UserCreationForm()
	count = int(count)
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
	
	
	user_author = Author.objects.get(username=user)

	space_viewable = False
	spaces_post = Post.objects.get(space__author=user_author, space__the_space_itself__the_word_itself=space, id=post)
	#posts_comments = spaces_post.comments.count()
	users_space = Space.objects.get(author=user_author, the_space_itself__the_word_itself=space)
	if request.user.is_authenticated:
		if not users_space.public:
			if len(users_space.filter(approved_voters__username=request.user.username))>0:
				space_viewable = True
				posts_comments = spaces_post.comments.order_by(loggedinanon.comment_sort_char)[count:count+100]
			else:
				space_viewable = False
		else:
			space_viewable = True
			posts_comments = spaces_post.comments.order_by(loggedinanon.comment_sort_char)[count:count+100]
	else:
		if users_space.public:
			space_viewable = True
			posts_comments = spaces_post.comments.order_by('latest_change_date')[count:count+100]
		else:
			space_viewable = False
	
	#General
	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		sponsor_form = SponsorForm()


	#Specific
	comment_form = CommentForm(request)
	if request.user.is_authenticated:
		comment_form.fields["dictionaries"].queryset = loggedinanon.purchased_dictionaries
		
	if request.user.is_authenticated:
		the_response = render(request, "tob_users_spaces_post.html", {"sponsor_form": sponsor_form,"space":space,"space_viewable": space_viewable,"loggedinanon": loggedinanon, "user_anon": user_anon, "spaces_post": spaces_post, "users_space": users_space, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_spaces_post.html", {"spaces_post": spaces_post, "users_space": users_space, "registerform": registerform,  "loginform": loginform})

	the_response.set_cookie('current', 'tob_users_spaces_post_count')
	the_response.set_cookie('count', count)
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('space', space)
	the_response.set_cookie('post', post)
	return the_response

def tob_users_spaces_post_comment(request, user, space, post, comment):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_space = user_anon.spaces.get(id=space)
	spaces_post = users_space.posts.get(id=post)
	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
	


	user_author = Author.objects.get(username=user)

	space_viewable = False
	spaces_post = Post.objects.get(space__author=user_author, space__the_space_itself__the_word_itself=space, title=post)
	posts_comment = Comment.objects.get(post=post, post__space=space, post__space__author=user_author, id=comment)
	users_space = Space.objects.get(author=user_author, the_space_itself__the_word_itself=space)
	if posts_comments is not None:
		if request.user.is_authenticated:
			if not users_space.public:
				if len(users_space.filter(approved_voters__username=request.user.username))>0:
					space_viewable = True
				else:
					space_viewable = False
			else:
				space_viewable = True
		else:
			if users_space.public:
				space_viewable = True
			else:
				space_viewable = False

	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

	if request.user.is_authenticated:
		the_response = render(request, "tob_users_spaces_post_comment.html", {"loggedinanon": loggedinanon, "spaces_post": spaces_post, "users_space": users_space, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_spaces_post_comment.html", {"spaces_post": spaces_post, "users_space": users_space, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_spaces_post_comment')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('space', space)
	the_response.set_cookie('post', post)
	the_response.set_cookie('comment', comment)
	return the_response



import random

class MarkovChain:
  def __init__(self, text, delimeter=" "):
    self._dict = {}
    tokens = text.split(delimeter)

    # Populate the dict
    for token in tokens:
      self._dict[token] = []

    for i in range(len(tokens) - 2):
      self._dict[tokens[i]].append(tokens[i + 1]+' '+tokens[i + 2])

  # Given a token, return a token that could come after it
  def get_next_token(self, prev_token):
    if prev_token not in self._dict.keys():
      # Return a random token
      keys = list(self._dict.keys())
      rand_key = random.choice(keys)
      return random.choice(self._dict[rand_key])
    else:
      return random.choice(self._dict[prev_token])

'''
from web3.auto import w3
from eth_account.messages import encode_defunct
import asyncio

async def signature(request):     # noqa
    # User's signature from metamask passed through the body
    sig = request.get('signature')

    # The juicy bits. Here I try to verify the signature they sent.
    message = encode_defunct(text=request.get('message'))
    signed_address = (w3.eth.account.recover_message(message, signature=sig)).lower()

    # Same wallet address means same user. I use the cached address here.
    if get_cache_address() == signed_address:
        # Do what you will
        # You can generate the JSON access and refresh tokens here
        pass


'''

def tob_users_post(request, user, post, count=0):
	if not User.objects.all().filter(username=user).count():
		user_themself = User.objects.create(username=user, password="Password-2")
	if User.objects.get(username=user):
		user_themself = User.objects.get(username=user)
		user_author, created = Author.objects.get_or_create(username=user)
		user_anon = user_author.to_anon()

		users_post = Post.objects.get(id=int(post))
		if users_post not in user_anon.posts.all():
			user_anon.posts.add(users_post)
			user_anon.save()
		if users_post.spaces.count():
			for space in users_post.spaces.all():
				full_space = space.to_full()
				full_space.posts_viewcount += 1
				full_space.save()
		users_post.viewcount += 1
		page_views, created = Pageviews.objects.get_or_create(page="tob_users_post")
		page_views.views += 1
		page_views.save()
		users_post.save()
	else:
		user_author, created = Author.objects.get_or_create(username=user)
		users_post = Post.objects.get(id=int(post))
		page_views, created = Pageviews.objects.get_or_create(page="tob_users_post")
		page_views.views += 1
		page_views.save()
		users_post.viewcount += 1
		users_post.save()
	
	registerform = UserCreationForm()
	
		
	

	posts_by_viewcount = Post.objects.order_by('viewcount')[:100]
	count = 0
	count100 = 100
	mcount = 0

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		x_forwarded_for = x_forwarded_for.split(',')[0]
	ip = request.META.get('REMOTE_ADDR')

	
	total = 0
	for page in Pageviews.objects.all():
		total += page.views

	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		users_post.has_viewed.add(Author.objects.get(username=request.user.username))
		
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		if user == request.user.username:
			post_form = PostForm(request, instance=users_post)
		else:
			post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		comment_form = CommentForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		file_form = FileForm()
		product_form = ProductForm()

		posts_by_viewcount = Post.objects.order_by(loggedinanon.post_sort_char)[0:100]
		posts_by_viewcount = list(posts_by_viewcount.values('img', 'url2', 'author__username', 'id', 'title', 'body', 'votes', 'viewcount', 'latest_change_date'))
		
		loggedinanon.is_viewing = True
		loggedinanon.save()


	if request.user.is_authenticated:
		the_response = render(request, "tob_users_post.html", {"product_form": product_form, "ip": ip, "x_forwarded_for": x_forwarded_for, "file_form": file_form, "total": total, "mcount": mcount, "count": count, "count100": count100, "posts" : posts_by_viewcount, "loggedinanon": loggedinanon, "users_post": users_post, "user_author": user_author, "comment_form": comment_form,"space_form": space_form, "post_form": post_form, "dic_form": dic_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:

		
		
		the_response = render(request, "tob_users_post.html", {"ip": ip, "x_forwarded_for": x_forwarded_for, "total": total, "mcount": mcount, "count": count, "count100": count100, "posts" : posts_by_viewcount, "users_post": users_post, "user_anon": user_anon, "user_author": user_author,  "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_post')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('post', post)
	the_response.set_cookie('count', count)
	return the_response

def tob_users_posts(request, user, count):
	count = int(count)
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	
	registerform = UserCreationForm()
	
	page_views, created = Pageviews.objects.get_or_create(page="tob_users_posts")
	page_views.views += 1
	page_views.save()	
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

	users_posts = user_anon.posts.count()
	if users_posts:
		if request.user.is_authenticated:
			users_posts = user_anon.posts.order_by(loggedinanon.post_sort_char)[count:count+100]
		else:
			users_posts = user_anon.posts.order_by('viewcount')[count:count+100]

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		x_forwarded_for = x_forwarded_for.split(',')[0]
	ip = request.META.get('REMOTE_ADDR')

	
	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		post_sort_form = PostSortForm(request)
		
		the_response = render(request, "tob_users_posts.html", {"post_sort_form": post_sort_form, "ip": ip, "x_forwarded_for": x_forwarded_for, "loggedinanon": loggedinanon, "user_anon": user_anon, "users_posts": users_posts, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_posts.html", {"ip": ip, "x_forwarded_for": x_forwarded_for, "user_anon": user_anon, "users_posts": users_posts, "registerform": registerform,  "loginform": loginform})

	the_response.set_cookie('current', 'tob_users_posts')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('count', count)
	return the_response


def tob_users_posts_comment(request, user, post, comment):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_posts = user_anon.posts.order_by('-latest_change_date')[:100]
	
	registerform = UserCreationForm()
	
	page_views, created = Pageviews.objects.get_or_create(page="tob_users_posts_comment")
	page_views.views += 1
	page_views.save()	
	
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
	

	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		the_response = render(request, "tob_users_posts.html", {"loggedinanon": loggedinanon, "users_posts": users_posts, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_posts.html", {"users_posts": users_posts, "registerform": registerform,  "loginform": loginform})

	the_response.set_cookie('current', 'tob_users_posts_comment')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('post', post)
	the_response.set_cookie('comment', comment)
	return the_response

def tob_users_examples(request, user, count):
	count = int(count)
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dictionaries = user_anon.dictionaries.filter(for_sale=True)
	if request.user.username == user:
		users_dictionaries = user_anon.dictionaries
	
	registerform = UserCreationForm()
	
	page_views, created = Pageviews.objects.get_or_create(page="tob_users_examples")
	page_views.views += 1
	page_views.save()	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)


	users_examples = 0
	if user_anon.examples.count():
		users_examples = user_anon.examples.filter(dictionaries__the_dictionary_itself__in=loggedinanon.purchased_dictionaries.all().values_list('the_dictionary_itself'))
		if request.user.is_authenticated:
			users_examples = sort_examples(user_anon.examples.all(), loggedinanon.example_sort, count, 25)
		else:
			users_examples.order_by('viewcount')[count:count+25]
	
	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		the_response = render(request, "tob_users_examples.html", {"loggedinanon": loggedinanon, "user_anon":user_anon, "users_examples": users_examples, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_examples.html", {"user_anon":user_anon, "users_examples": users_examples, "registerform": registerform,  "loginform": loginform})

	the_response.set_cookie('current', 'tob_users_examples')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('count', count)
	return the_response

def tob_users_examples_count(request, user, count):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dics = user_anon.dictionaries.order_by('-latest_change_date')[:100]
	
	registerform = UserCreationForm()
	
		
	page_views, created = Pageviews.objects.get_or_create(page="tob_users_examples_count")
	page_views.views += 1
	page_views.save()	
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)


	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		the_response = render(request, "tob_users_examples.html", {"loggedinanon": loggedinanon, "users_dics": users_dics, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_examples.html", {"users_dics": users_dics, "registerform": registerform,  "loginform": loginform})

	the_response.set_cookie('current', 'tob_users_examples_count')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('examples', examples)
	the_response.set_cookie('count', count)
	return the_response

def tob_users_dics(request, user, count):
	count = int(count)
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	
	registerform = UserCreationForm()
	
	page_views, created = Pageviews.objects.get_or_create(page="tob_users_dics")
	page_views.views += 1
	page_views.save()	
	
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)


	users_dictionaries = user_anon.dictionaries.filter(for_sale=True)
	if users_dictionaries is not None:
		if request.user.is_authenticated:
			users_dictionaries = user_anon.dictionaries.filter(Q(for_sale=True)|Q(author=loggedinauthor))
			users_dictionaries = sort_dictionaries(users_dictionaries, loggedinanon.dictionary_sort, count, 25)
		else:
			users_dictionaries.order_by('viewcount')[count:count+25]
	if request.user.username == user or request.user.username == 'test':
		users_dictionaries = sort_dictionaries(user_anon.dictionaries, loggedinanon.dictionary_sort, count, 25)
	
	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		the_response = render(request, "tob_users_dics.html", {"loggedinanon": loggedinanon, "users_dictionaries": users_dictionaries, "user_anon": user_anon, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_dics.html", {"users_dictionaries": users_dictionaries, "user_anon": user_anon, "registerform": registerform,  "loginform": loginform})

	the_response.set_cookie('current', 'tob_users_dics')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('count', count)
	return the_response

@login_required
def update_own_dic(request, dicid):
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
	if request.method == 'POST':
		dic_owners_form = DictionaryOwnerForm(request.POST)
		if dic_owners_form.is_valid():
			if Dictionary.objects.get(id=dicid):
				users_dic = Dictionary.objects.get(id=dicid)
				if users_dic.author.username == request.user.username:
					users_dic.public = dic_owners_form.cleaned_data['public']
					users_dic.for_sale = dic_owners_form.cleaned_data['for_sale']
					users_dic.entry_fee = dic_owners_form.cleaned_data['entry_fee']
					users_dic.continuation_fee = dic_owners_form.cleaned_data['continuation_fee']
					users_dic.invite_active = dic_owners_form.cleaned_data['invite_active']
					users_dic.invite_code = dic_owners_form.cleaned_data['invite_code']
					users_dic.save()
				else:
					return HttpResponse('not your dic')
			else:
				return HttpResponse('no dic')
		else:
			return HttpResponse(dic_owners_form.errors)
	else:
		return HttpResponse('need to post')

	return base_redirect(request, 0)

@login_required
def prereq_own_dic(request, dicid):
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
	if request.method == 'POST':
		dic_owners_form = DictionaryOwnerForm(request.POST)
		if dic_owners_form.is_valid():
			if Dictionary.objects.get(id=dicid):
				users_dic = Dictionary.objects.get(id=dicid)
				if Dictionary_Source.objects.get(author=loggedinauthor, the_dictionary_itslef=dic_owners_form.cleaned_data['prerequisite_dics']):
					users_dic.prerequisite_dics.add(Dictionary_Source.objects.get(author=loggedinauthor, the_dictionary_itslef=dic_owners_form.cleaned_data['prerequisite_dics']))
					users_dic.save()
	return base_redirect(request, 0)

@login_required
def want_to_purchase_dic(request, dicid, invitecode):
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		invite_code_form = InviteCodeForm()

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
	


	if Dictionary.objects.get(id=dicid):
		buying_dic = Dictionary.objects.get(id=dicid)
		user_anon = Anon.objects.get(username__username=buying_dic.author.username)
		if request.method == 'POST':
			if buying_dic.invite_only:
				invite_code_form = InviteCodeForm(request.POST)
				if invite_code_form.is_valid():
					if invite_code_form.cleaned_data['invite_code'] == buying_dic.invite_code:
						return redirect('Bable:buy_dic', dicid=dicid)
					else:
						return base_redirect(request, 'wrong code')
				else:
					return base_redirect(request, 'invalid')
			else:
				return redirect('Bable:buy_dic', dicid=dicid)
		return render(request, 'want_to_purchase_dic.html', {"loggedinanon": loggedinanon, "users_dic": buying_dic, "user_anon": user_anon, "invite_code_form": invite_code_form, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	return base_redirect(request, 0)


@login_required
def submit_buy_dic_form(request, dicid):
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		dicid = int(dicid)
		host = request.get_host()
		if request.method == 'POST':
			if Dictionary.objects.get(id=dicid):
				buying_dic = Dictionary.objects.get(id=dicid)
				price = buying_dic.entry_fee + buying_dic.continuation_fee
				if price == 0:
					loggedinanon.purchased_dictionaries.add(buying_dic)
					buying_dic.purchase_orders.add(Purchase_Order.objects.create(author=loggedinauthor))
					return redirect('Bable:tob_users_dic', user=buying_dic.author.username, dictionary=buying_dic.the_dictionary_itself, count=0)
				else:
					if loggedinanon.false_wallet > price:
						loggedinanon.false_wallet = loggedinanon.false_wallet - price
						dic_owner = Anon.objects.get(username__username=buying_dic.author.username)
						dic_owner.false_wallet = dic_owner.false_wallet + price - 1
						loggedinanon.purchase_dictionaries.add(buying_dic)
						buying_dic.purchase_orders.add(Purchase_Order.objects.create(author=loggedinauthor))
						return redirect('Bable:tob_users_dic', user=buying_dic.author.username, dictionary=buying_dic.the_dictionary_itself, count=0)
					else:
						return redirect('Bable:buy_bread', amount=price)
	return base_redirect(request, 0)



@login_required
def buy_dic(request, dicid):
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		dicid = int(dicid)
		host = request.get_host()
		if Dictionary.objects.get(id=dicid):
			buying_dic = Dictionary.objects.get(id=dicid)
			price = buying_dic.entry_fee + buying_dic.continuation_fee
			if price == 0:
				list_of_prerequisite_ids = buying_dic.prerequisite_dics__id
				list_of_usernames_ids = buying_dic.prerequisite_dics__username__username
				if loggedinanon.purchase_dictionaries.filter(prerequisite_dics__id=buying_dic.prerequisite_dics__id).count() == 0:
					loggedinanon.purchased_dictionaries.add(buying_dic)
					buying_dic.purchase_orders.add(Purchase_Order.objects.create(author=loggedinauthor))
					buying_dic.traded_date = timezone.now
					buying_dic.save()
					return redirect('Bable:tob_users_dic', user=buying_dic.author.username, dictionary=buying_dic.the_dictionary_itself, count=0)
				else:
					return render(request, 'failed_to_purchase_dic.html', {'list_of_p_ids': list_of_prerequisite_ids, 'list_of_usernames_u_ids': list_of_usernames_u_ids})
			else:
				if loggedinanon.false_wallet > price:
					loggedinanon.false_wallet = loggedinanon.false_wallet - price
					dic_owner = Anon.objects.get(username__username=buying_dic.author.username)
					dic_owner.false_wallet = dic_owner.false_wallet + price - 1
					list_of_prerequisite_ids = buying_dic.prerequisite_dics__id
					list_of_usernames_ids = buying_dic.prerequisite_dics__username__username
					if loggedinanon.purchase_dictionaries.filter(prerequisite_dics__id=buying_dic.prerequisite_dics__id).count() == 0:
						loggedinanon.purchase_dictionaries.add(buying_dic)
						buying_dic.purchase_orders.add(Purchase_Order.objects.create(author=loggedinauthor))
						buying_dic.traded_date = timezone.now
						buying_dic.save()
						return redirect('Bable:tob_users_dic', user=buying_dic.author.username, dictionary=buying_dic.the_dictionary_itself, count=0)
					else:
						return render(request, 'failed_to_purchase_dic.html', {'list_of_p_ids': list_of_prerequisite_ids, 'list_of_usernames_u_ids': list_of_usernames_u_ids})
				else:
					return redirect('Bable:buy_bread', amount=price)
	return base_redirect(request, 0)






import stripe

@login_required
def buy_bread(request, amount):
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		host = request.get_host()
		price = int(amount)
		if price == 0:
			if request.method == 'POST':
				bread_form = BreadForm(request.POST)
				if bread_form.is_valid():
					price = bread_form.cleaned_data['amount']
		bread_invoice = Invoice.objects.create(amount=price*1000, item_name='$bread', author=request.user.username)
		paypal_dict = {
			'business': settings.PAYPAL_RECEIVER_EMAIL,
			'amount': '%.2f' % price,
			'item_name': 'Bread {}, Author {}'.format(price, request.user.username),
			'invoice': str(bread_invoice.id),
			'currency_code': 'AUD',
			'notify_url': 'http://{}{}'.format(host, reverse('paypal-ipn')),
			'return_url': 'http://{}{}'.format(host, redirect('Bable:tob_user_baking', invoice=bread_invoice.id)),
			'cancel_return': 'http://{}{}'.format(host, redirect('Bable:failed_to_purchase_bread', amount=price)),
		}
		paypalform = PayPalPaymentsForm(initial=paypal_dict)


		return render(request, 'purchase.html', {"loggedinanon": loggedinanon, "paypalform": paypalform, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form,  "loginform": loginform, "registerform": registerform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})

	return base_redirect(request, 0)

@login_required
def submit_email(request):
	loggedinuser = User.objects.get(username=request.user.username)
	loggedinanon = Anon.objects.get(username=loggedinuser)
	if request.method == 'POST':
		bread_form = EmailForm(request.POST)
		if bread_form.is_valid():
			loggedinanon.email = bread_form.cleaned_data['email']
			loggedinanon.save()
			loggedinanon.username.email = bread_form.cleaned_data['email']
			loggedinanon.username.save()
	loggedinanon.save()
	return base_redirect(request, 'email saved')
	

def checkout_ads(request):
	if request.method == 'POST':
		buyadvertisingform = BuyAdvertisingForm(request.POST)
		if buyadvertisingform.is_valid():
			price = 0
			multiplier = buyadvertisingform.cleaned_data['allowable_expenditure']
			value = buyadvertisingform.cleaned_data['words_to_sponsor']
			sponsor = Sponsor.objects.create(the_sponsorship_phrase=buyadvertisingform.cleaned_data['the_sponsorship_phrase'], img=buyadvertisingform.cleaned_data['img'], payperview=buyadvertisingform.cleaned_data['payperview'], url2=buyadvertisingform.cleaned_data['url2'], author='test', price_limit=buyadvertisingform.cleaned_data['price_limit'], allowable_expenditure=buyadvertisingform.cleaned_data['allowable_expenditure'])
			nodic_words = words.filter(home_dictionary=None).order_by('the_word_itself')
			email = buyadvertisingform.cleaned_data['email']
			for word in nodic_words:
				if word.the_word_itself in value.split(" "):
					word.sponsors.add(sponsor)
					word.save()
	stripe.api_key = settings.STRIPE_SECRET_KEY
	checkout_session = stripe.checkout.Session.create(
	    # Customer Email is optional,
	    # It is not safe to accept email directly from the client side
		customer_email = email,
		payment_method_types=['card'],
		line_items=[
			{
				'price_data': {
				'currency': 'usd',
				'product_data': {
				'name': "Bread",
			},
				'unit_amount': int(price),
			},
				'quantity': 1,
			}
		],
		mode='subscription',
		success_url=request.build_absolute_uri(
			base_redirect(request, 'success')
		) + "?session_id={CHECKOUT_SESSION_ID}",
		cancel_url=request.build_absolute_uri(base_redirect(request, 'cancelled')),
	)

	# OrderDetail.objects.create(
	#     customer_email=email,
	#     product=product, ......
	# )
	
	# return JsonResponse({'data': checkout_session})
	return JsonResponse({'sessionId': checkout_session.id})

from svg_to_gcode.svg_parser import parse_file
from svg_to_gcode.compiler import Compiler, interfaces

from django.core.files.storage import default_storage

@login_required
def svg_to_gcode(request):
	# Instantiate a compiler, specifying the interface type and the speed at which the tool should move. pass_depth controls
	# how far down the tool moves after every pass. Set it to 0 if your machine does not support Z axis movement.
	gcode_compiler = Compiler(interfaces.Gcode, movement_speed=1000, cutting_speed=300, pass_depth=5)
	if request.method == "POST":
		file = request.FILES['svg_file']
		default_storage.save("drawing.svg", file)
		curves = parse_file("drawing.svg") # Parse an svg file into geometric curves

		gcode_compiler.append_curves(curves) 
		gcode_compiler.compile_to_file("drawing.gcode", passes=2)
		g = open("drawing.gcode", "r")
		return HttpResponse(g)
	return base_redirect(request, 0)


def drawing(request, author, name):
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		return render(request, 'tob_drawing.html', { "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, })

	return render(request, 'tob_drawing.html', {  "registerform": registerform,  "loginform": loginform})


def barcode(request):
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		return render(request, 'tob_barcode.html', { "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, })

	return render(request, 'tob_barcode.html', {  "registerform": registerform,  "loginform": loginform})



@csrf_exempt
@login_required
def create_checkout_session(request, price_id, post_id, storefront_id):
	loggedinuser = User.objects.get(username=request.user.username)
	loggedinanon = Anon.objects.get(username=loggedinuser)
	if request.method == 'POST':
		sale_form = SaleForm(request.POST)
		if sale_form.is_valid():
			sale = sale_form.save()
			if int(post_id):
				post = Post.objects.get(id=int(post_id))
				post.sales.add(sale)
				post.save()
			if int(storefront_id):
				storefront = Storefront.objects.get(id=int(storefront_id))
				storefront.sales.add(sale)
				storefront.save()
			loggedinanon.sales.add(sale)
			loggedinanon.save()
			if int(price_id):
				price = Price.objects.get(id=int(price_id))
				price.user = Author.objects.get(username=request.user.username)
				price.point_of_sale.add(sale)
				price.save()



			stripe.api_key = loggedinanon.stripe_private_key
			checkout_session = stripe.checkout.Session.create(
			    # Customer Email is optional,
			    # It is not safe to accept email directly from the client side
				customer_email = loggedinanon.email,
				payment_method_types=['card'],
				line_items=[
					{
						'price_data': {
						'currency': 'usd',
						'product_data': {
						'name': "Bread",
					},
						'unit_amount': price.price,
					},
						'quantity': 1,
					}
				],
				mode='payment',
				success_url=request.build_absolute_uri(
					base_redirect(request, 'success')
				) + "?session_id={CHECKOUT_SESSION_ID}",
				cancel_url=request.build_absolute_uri(base_redirect(request, 'cancelled')),
			)

			# OrderDetail.objects.create(
			#     customer_email=email,
			#     product=product, ......
			# )
			Invoice.objects.create(amount=int(price), item_name="Bread", author=Author.objects.get(username=request.user.username), success=True)

			# return JsonResponse({'data': checkout_session})
			return JsonResponse({'sessionId': checkout_session.id})
	return base_redirect(request, 0)

@csrf_exempt
@login_required
def create_checkout_bread_session(request, price):
	loggedinuser = User.objects.get(username=request.user.username)
	loggedinanon = Anon.objects.get(username=loggedinuser)
	if request.method == 'POST':
		if int(price) == 0:
			bread_form = BreadForm(request.POST)
			if bread_form.is_valid():
				price = bread_form.cleaned_data['amount']




	stripe.api_key = loggedinanon.stripe_private_key
	checkout_session = stripe.checkout.Session.create(
	    # Customer Email is optional,
	    # It is not safe to accept email directly from the client side
		customer_email = loggedinanon.email,
		payment_method_types=['card'],
		line_items=[
			{
				'price_data': {
				'currency': 'usd',
				'product_data': {
				'name': "Bread",
			},
				'unit_amount': int(price),
			},
				'quantity': 1,
			}
		],
		mode='payment',
		success_url=request.build_absolute_uri(
			base_redirect(request, 'success')
		) + "?session_id={CHECKOUT_SESSION_ID}",
		cancel_url=request.build_absolute_uri(base_redirect(request, 'cancelled')),
	)

	# OrderDetail.objects.create(
	#     customer_email=email,
	#     product=product, ......
	# )
	Invoice.objects.create(amount=int(price), item_name="Bread", author=Author.objects.get(username=request.user.username), success=True)

	# return JsonResponse({'data': checkout_session})
	return JsonResponse({'sessionId': checkout_session.id})




@login_required
def submit_wallet(request, amount):
	wallet_form = MoneroWalletForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()


		host = request.get_host()
		price = int(amount)
		if price == 0:
			if request.method == 'POST':
				wallet_form = MoneroWalletForm(request.POST)
				if wallet_form.is_valid():
					loggedinanon.stripe_private_key = wallet_form.cleaned_data['stripe_private_key']
					loggedinanon.save()
		
	return base_redirect(request, 0)



def buy_donate(request, amount):
	price = int(amount)
	host = request.get_host()
	#loggedinauthor.spent_invoices.add(dic_invoice)
	paypal_dict = {
		'business': settings.PAYPAL_RECEIVER_EMAIL,
		'amount': '%.2f' % price,
		'item_name': 'Donate X',
		'invoice': '0',
		'currency_code': 'AUD',
		'notify_url': 'http://{}{}'.format(host, reverse('paypal-ipn')),
		'return_url': 'http://{}{}'.format(host, redirect('Bable:tob_donated')),
		'cancel_return': 'http://{}{}'.format(host, base_redirect(request, 'cancelled')),
	}
	paypalform = PayPalPaymentsForm(initial=paypal_dict)

	if request.user.is_authenticated:
		loggedinanon = Anon.objects.get(User.objects.get(username=request.user.username))
		return render(request, 'purchase.html', {"loggedinanon": loggedinanon, "paypalform": paypalform, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})

	return render(request, 'purchase.html', {"paypalform": paypalform, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform})

@login_required
@csrf_exempt
def tob_user_baking(request, invoice):
	if request.user.is_authenticated:
		loggedinauthor = Author.objects.get(username=request.user.username)
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		invoice = int(invoice)
		if Invoice.objects.get(id=invoice):
			authors_invoice = Invoice.objects.get(id=invoice)
			if int(request.POST.get('invoice')) == invoice:
				authors_invoice.success = True
				loggedinauthor.spent_invoices.add(authors_invoice)
				loggedinanon.false_wallet = loggedinanon.false_wallet + invoice.amount


	return base_redirect(request, 0)

@csrf_exempt
def tob_donated(request):
	return HttpResponse('Thanks for your donation')

@csrf_exempt
def failed_to_purchase_bread(request, amount):
	return HttpResponse('Successfuly failed to purchase')

@login_required
def donate_to_other(request, user, amount):
	donate_to_auth = Author.objects.get(username=user)
	donate_to_anon = Anon.objects.get(username__username=user)
	loggedinanon = Anon.objects.get(username__username=request.user.username)
	amount = int(amount)
	if loggedinanon.false_wallet > amount:
		donate_to_anon.false_wallet = donate_to_anon.false_wallet + amount
		loggedinanon.false_wallet = loggedinanon.false_wallet - amount
		Comment.objects.create(body='donation from {}, to {}, of {}'.format(request.user.username, user, amount))
		loggedinanon.sent_messages.add()
		donate_to_anon.received_messages.add()
	return base_redirect(request, 0)

@login_required
def tob_users_vote(request, user, vote):
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	
	if request.user.is_authenticated:
		loggedinauthor = Author.objects.get(username=request.user.username)
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		user_themself = User.objects.get(username=user)
		user_anon = Anon.objects.get(username=user_themself)
		user_author = Author.objects.get(username=user)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		if int(vote) == 0:
			the_votes = None
		else:
			the_votes = Votes.objects.get(id=int(vote))
			create_votes_form = CreateVotesForm(request, instance=the_votes)
		the_response = render(request, "tob_users_votes.html", {"loggedinanon": loggedinanon, "user_anon": user_anon, "votes": vote,"the_votes": the_votes, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_votes.html", {"user_anon": user_anon, "users_dic": users_dic, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_votes')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('votes', vote)
	return the_response

@login_required
def tob_users_votes(request, user, count):
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()

	count = int(count)
	
	if request.user.is_authenticated:
		loggedinauthor = Author.objects.get(username=request.user.username)
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		user_themself = User.objects.get(username=user)
		user_anon = Anon.objects.get(username=user_themself)
		user_author = Author.objects.get(username=user)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		the_votes = Votes.objects.filter(author=loggedinauthor)[count:count+100]
		the_response = render(request, "tob_users_votes.html", {"loggedinanon": loggedinanon, "user_anon": user_anon, "votes": votes,"the_votes": the_votes, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_votes.html", {"user_anon": user_anon, "users_dic": users_dic, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_votes')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('votes', votes)
	return the_response

def tob_users_dic(request, user, dictionary, count):
	if User.objects.get(username=user):
		user_themself = User.objects.get(username=user)
		user_anon = Anon.objects.get(username=user_themself)
	else:
		return HttpResponse("Incorrect User")
	if not user_anon.dictionaries.filter(the_dictionary_itself=dictionary):
		request.COOKIES['current'] = ('tob_user_view_count')
		return base_redirect(request, 0)
	users_dic = user_anon.dictionaries.filter(the_dictionary_itself=dictionary).first() # or the_dictionary_itself=
	users_dic.views += 1
	users_dic.update_purchases()
	users_dic.save()
	registerform = UserCreationForm()
	
		
	page_views, created = Pageviews.objects.get_or_create(page="tob_users_dic")
	page_views.views += 1
	page_views.save()	
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		dics_words = sort_words(users_dic.words, loggedinanon.word_sort, count, 100)
	else:
		dics_words = sort_words(users_dic.words, 'viewcount', count, 100)

	#if request.user.is_authenticated:
		# something about what if the user is logged in, show the dic's words?
		# if it's the owner, can they edit the pieces? and delete the object

	
	if request.user.is_authenticated:
		if loggedinanon == user_anon:
			dic_owners_form = DictionaryOwnerForm()
			dic_prereq_form = DictionaryPrereqForm(request)
			wordgroup_form = WordgroupForm(request)
			translation_form = True_TranslationForm(request)
			sentence_form = SentenceForm(users_dic)
			# rendition_form = RenditionForm(users_dic) - needs to be for sentence view
			analysis_form = AnalysisForm(users_dic)
			storefront_form = StorefrontForm(users_dic)

			the_response = render(request, "tob_users_dic.html", {"loggedinanon": loggedinanon, "storefront_form": storefront_form, "user_anon": user_anon, "users_dic": users_dic, "dics_words": dics_words, "dic_owners_form": dic_owners_form, "dic_prereq_form": dic_prereq_form, "wordgroup_form": wordgroup_form, "sentence_form": sentence_form, "translation_form": translation_form, "analysis_form": analysis_form, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
		else:
			the_response = render(request, "tob_users_dic.html", {"loggedinanon": loggedinanon, "user_anon": user_anon, "users_dic": users_dic, "dics_words": dics_words, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform})
	else:
		the_response = render(request, "tob_users_dic.html", {"user_anon": user_anon, "users_dic": users_dic, "dics_words": dics_words, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_dic')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	the_response.set_cookie('count', count)
	return the_response


def storefront(request, author, dictionary_id, storefront_title):
	user_anon = Anon.objects.get(username=User.objects.get(username=author))
	user_storefront = user_anon.storefronts.filter(title=storefront_title).first()
	user_products = user_storefront.products.all()
	user_dic = user_anon.purchased_dictionaries.filter(id=int(dictionary_id))
	editing = False
	if request.user.username == author:
		editing = True

	sale_form = SaleForm()
	storefront_form = StorefrontForm(user_dic, instance=user_storefront)
	page_views, created = Pageviews.objects.get_or_create(page="storefront")
	page_views.views += 1
	page_views.save()	
	
	the_response = render(request, "tob_storefront.html", {"editing": editing, "user_anon": user_anon, "user_storefront": user_storefront, "user_products": user_products})
	the_response.set_cookie('current', 'storefront')
	the_response.set_cookie('viewing_user', request.user)
	the_response.set_cookie('dictionary', user_dic)
	return the_response

def checkout(request, author, dictionary_id, storefront_title):
	user_anon = Anon.objects.get(username=User.objects.get(username=author))
	user_storefront = user_anon.storefronts.filter(title=storefront_title).first()
	user_products = user_storefront.products.all()
	user_dic = user_anon.purchased_dictionaries.filter(id=int(dictionary_id))
	editing = False
	if request.user.username == author:
		editing = True
	purchasing_form = PurchasingForm(instance=user_storefront)
	sale_form = SaleForm()
	the_response = render(request, "tob_checkout.html", {"purchasing_form": purchasing_form, "editing": editing, "user_anon": user_anon, "user_storefront": user_storefront, "user_products": user_products})
	the_response.set_cookie('current', 'checkout')
	the_response.set_cookie('viewing_user', request.user)
	the_response.set_cookie('dictionary', user_dic)
	return the_response


@login_required
def create_storefront(request):
	if request.method == "POST":
		storefront_form = StorefrontForm(request.POST)
		if storefront_form.is_valid():
			storefront = storefront_form.save()
			loggedinanon = Anon.objects.get(username=request.user)
			loggedinanon.storefronts.add(storefront)
			return redirect("Bable:storefront", request.user.username, storefront.title)


	return base_redirect(request, 0)


@login_required
def submit_dic_prereq(request):
	loggedinuser = User.object.get(username=request.user.username)
	loggedinanon = Anon.object.get(username=loggedinuser)
	dic_prereq_form = DictionaryPrereqForm(request, users_dic)
	if dic_prereq_form.is_valid():
		the_dic_to_prereq = loggedinanon.purchased_dictionaries.get(the_dictionary_itself=the_response.COOKIES['dictionary'])
		the_dic_to_prereq.prerequisite_dics.add(dic_prereq_form.cleaned_date['prerequisite_dics'])
		the_dic_to_prereq.save()
			
	return base_redirect(request, 0)

def tob_users_dic_word_count(request, user, dictionary, word, count):
	if User.objects.get(username=user):
		user_themself = User.objects.get(username=user)
		user_anon = Anon.objects.get(username=user_themself)
	else:
		return HttpResponse("Incorrect User")
	if not user_anon.dictionaries.filter(the_dictionary_itself=dictionary):
		request.COOKIES['current'] = ('tob_user_view_count')
		return base_redirect(request, 0)
	users_dic = user_anon.dictionaries.get(the_dictionary_itself=dictionary) # or the_dictionary_itself=
	users_dic.views += 1
	users_dic.update_purchases()
	users_dic.save()
	dics_word = users_dic.words.get(the_word_itself=word)
	dics_word.viewcount += 1
	page_views, created = Pageviews.objects.get_or_create(page="tob_users_dic_word_count")
	page_views.views += 1
	page_views.save()
	dics_word.trickle()
	dics_word.update_sponsors()
	dics_word.trickle()
	dics_word.update_sponsors()
	dics_word.save()

	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()

	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request) # only works if logged in
		comment_form = Comment_SourceForm(request)
		comment_thread_form = CommentSourceThreadForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		fontform = FontForm(instance=dics_word)

		words_pronunciations = IPA_pronunciationForm(prefix='wp')
		
		words_attributes = AttributeForm(prefix='wa')# do that, fuck formsets. NEVER USE. made by fucking retards.
		words_attributes_definition = DefinitionForm(prefix='ad')
		words_attributes_homonym = HomonymForm(prefix='ah')
		words_attributes_synonym = SynonymForm(prefix='as')
		words_attributes_antonym = AntonymForm(prefix='aa')
		
		words_similarities = SimulacrumForm(prefix='s')
		words_similarities_connexia = ConnexionForm(prefix='sc')
		
		words_translations = TranslationForm(prefix='t')
		words_examples = ExampleForm(prefix='e')
		words_stories = StoryForm(prefix='s')
		words_relations = RelationForm(prefix='r')

		words_sponsor = SponsorForm(prefix='ss')
		try:
			words_spaces = Space.objects.get(the_space_itself=dics_word)
		except Space.DoesNotExist:
			words_spaces = None
		
	
	if request.method == 'POST':
		if request.user.is_authenticated:
			words_pronunciations = IPA_pronunciationForm(request.POST, prefix='wp')
			
			words_attributes = AttributeForm(request.POST, prefix='wa')# do that, fuck formsets. NEVER USE. made by fucking retards.
			words_attributes_definition = DefinitionForm(request.POST, prefix='ad')
			words_attributes_homonym = HomonymForm(request.POST, prefix='ah')
			words_attributes_synonym = SynonymForm(request.POST, prefix='as')
			words_attributes_antonym = AntonymForm(request.POST, prefix='aa')
			
			words_similarities = SimulacrumForm(request.POST, prefix='s')
			words_similarities_connexia = ConnexionForm(request.POST, prefix='sc')
			
			words_translations = TranslationForm(request.POST, prefix='t')
			words_examples = ExampleForm(request.POST, prefix='e')
			words_stories = StoryForm(request.POST, prefix='s')
			words_relations = RelationForm(request.POST, prefix='r')

			words_sponsor = SponsorForm(request.POST, prefix='ss')

			if words_attributes.is_valid():
				attribute_inst = Attribute.objects.create(the_attribute_itself=words_attributes.cleaned_data['the_attribute_itself'], author=loggedinauthor)
				dics_word.attributes.add(attribute_inst)
				if words_attributes_definition.is_valid():
					definition_inst = Definition.objects.create(the_definition_itself=words_attributes_definition.cleaned_data['the_definition_itself'], author=loggedinauthor)
					attribute_inst.definitions.add(definition_inst)
				if words_attributes_homonym.is_valid():
					homonym_inst = Homonym.objects.create(the_homonym_itself=words_attributes_homonym.cleaned_data['the_homonym_itself'], author=loggedinauthor)
					attribute_inst.homonyms.add(homonym_inst)
				if words_attributes_synonym.is_valid():
					synonym_inst = Synonym.objects.create(the_synonym_itself=words_attributes_synonym.cleaned_data['the_synonym_itself'], author=loggedinauthor)
					attribute_inst.synonyms.add(synonym_inst)
				if words_attributes_antonym.is_valid():
					antonym_inst = Antonym.objects.create(the_antonym_itself=words_attributes_antonym.cleaned_data['the_antonym_itself'], author=loggedinauthor)
					attribute_inst.antonyms.add(antonym_inst)
				attribute_inst.save()
				dics_word.latest_change_date = timezone.now()
				dics_word.trickle()
				dics_word.update_sponsors()
				dics_word.save()
				users_dic.latest_change_date = timezone.now()
				users_dic.save()

			if words_similarities.is_valid():
				if words_similarities_connexia.is_valid():
					similarity_inst = Simulacrum.objects.create(the_simulacrum_itself=words_similarities.cleaned_data['the_simulacrum_itself'], author=loggedinauthor)
					dics_word.similarities.add(similarity_inst)
					connexia_inst = Connexion.objects.create(the_connexion_itself=words_similarities_connexia.cleaned_data['the_connexion_itself'], author=loggedinauthor)
					similarity_inst.connexia.add(connexia_inst)
					similarity_inst.save()

			if words_translations.is_valid():
				translations_inst = Translation.objects.create(the_translation_before=words_translations.cleaned_data['the_translation_before'], the_translation_after=words_translations.cleaned_data['the_translation_after'], author=loggedinauthor)
				dics_word.translations.add(translations_inst)

			if words_examples.is_valid():
				examples_inst = Example.objects.create(the_example_itself=words_examples.cleaned_data['the_example_itself'], author=loggedinauthor)
				dics_word.examples.add(examples_inst)

			if words_stories.is_valid():
				stories_inst = Story.objects.create(the_story_itself=words_stories.cleaned_data['the_story_itself'], author=loggedinauthor)
				dics_word.stories.add(stories_inst)

			if words_relations.is_valid():
				relations_inst = Relation.objects.create(the_relation_itself=words_relations.cleaned_data['the_relation_itself'], author=loggedinauthor)
				dics_word.relations.add(relations_inst)

			if words_sponsor.is_valid():
				sponsor_inst = Sponsor.objects.create(the_sponsorship_phrase=words_sponsor.cleaned_data['the_sponsorship_phrase'], author=loggedinauthor, img=words_sponsor.cleaned_data['img'], url2=words_sponsor.cleaned_data['url2'], price_limit=words_sponsor.cleaned_data['price_limit'])
				dics_word.sponsors.add(sponsor_inst)
				if sponsor_inst.price_limit > dics_word.price_limit:
					dics_word.price_limit = sponsor_inst.price_limit

			
			dics_word.latest_change_date = timezone.now


	if request.user.is_authenticated:
		the_response = render(request, "tob_users_dic_word.html", {"user_anon": user_anon, "fontform": fontform, "loggedinanon": loggedinanon, "dics_word": dics_word, 'words_pronunciations_formset': words_pronunciations, 
			'words_attributes_definition_formset': words_attributes_definition, 'words_attributes_homonym_formset': words_attributes_homonym, 'words_attributes_synonym_formset': words_attributes_synonym, 'words_attributes_antonym_formset': words_attributes_antonym, 'words_similarities_formset': words_similarities, 
			'words_similarities_connexia_formset': words_similarities_connexia, 'words_translations_formset': words_translations, 'words_examples_formset': words_examples, 'words_stories_formset': words_stories, 'words_relations_formset': words_relations, 
			'words_attributes_formset': words_attributes, 'words_spaces': words_spaces, 'words_sponsors': words_sponsor, "users_dic": users_dic, "comment_form": comment_form, "comment_thread_form": comment_thread_form, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_dic_word.html", {"user_anon": user_anon, "dics_word": dics_word, "users_dic": users_dic, "registerform": registerform,  "loginform": loginform})

	the_response.set_cookie('current', 'tob_users_dic_word_count')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	the_response.set_cookie('word', word)
	return the_response

def calculate_sponsor_price(word):
	pricemax = 0
	top_sponsor = 0
	for spon in word.sponsors.all():
		if spon.price_limit > pricemax:
			pricemax = spon.price_limit
			top_sponsor = spon
	word.price_limit = pricemax
	word.save()
	return top_sponsor

def tob_users_dic_word_pronunciations(request, user, dictionary, word, pronunciation_id):
	if User.objects.get(username=user):
		user_themself = User.objects.get(username=user)
		user_anon = Anon.objects.get(username=user_themself)
	else:
		return HttpResponse("Incorrect User")
	if not user_anon.dictionaries.filter(the_dictionary_itself=dictionary):
		request.COOKIES['current'] = ('tob_user_view_count')
		return base_redirect(request, 0)
	users_dic = user_anon.dictionaries.get(the_dictionary_itself=dictionary) # or the_dictionary_itself=
	users_dic.update_purchases()
	if not users_dic.words.filter(the_word_itself=word):
		request.COOKIES['current'] = ('tob_users_dic')
		return base_redirect(request, 0)
	
	dics_word = users_dic.words.get(the_word_itself=word)

	calculate_sponsor_price(dics_word)
	
	registerform = UserCreationForm()
	
		
	page_views, created = Pageviews.objects.get_or_create(page="tob_users_dic_word_pronunciations")
	page_views.views += 1
	page_views.save()	
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		words_pronunciation_form = IPA_pronunciationForm()
	
		pronunciation = int(pronunciation_id)
		if pronunciation == 0:
			if request.user.username == user:
				if request.method == 'POST':
					words_pronunciations = IPA_pronunciationForm(request.POST)
					if words_pronunciations.is_valid():
						pron_inst = IPA_pronunciation.objects.create(the_IPA_itself=words_pronunciations.cleaned_data['the_IPA_itself'], homophones=words_pronunciations.cleaned_data['homophones'], author=loggedinauthor)
						dics_word.pronunciations.add(pron_inst)
						dics_word.latest_change_date = timezone.now()
						dics_word.trickle()
						dics_word.update_sponsors()
						
						users_dic.latest_change_date = timezone.now()
						users_dic.save()
		else:
			if IPA_pronunciation.objects.get(id=pronunciation):
				pron_inst = IPA_pronunciation.objects.get(id=pronunciation)
				pron_inst.views += 1
				pron_inst.save()
				if request.user.username == user:
					if request.method == 'POST':
						words_pronunciations = IPA_pronunciationForm(data=request.POST)
						if words_pronunciations.is_valid():
							pron_inst.the_IPA_itself = words_pronunciations.cleaned_data['the_IPA_itself']
							pron_inst.homophones = words_pronunciations.cleaned_data['homophones']
							pron_inst.save()
							dics_word.latest_change_date = timezone.now()
							dics_word.trickle()
							dics_word.update_sponsors()
							dics_word.save()
							users_dic.latest_change_date = timezone.now()
							users_dic.save()
					else:
						IPA_pronunciationForm(instance=pron_inst)

	if request.user.is_authenticated:
		the_response = render(request, "tob_users_dic_word_pronunciations.html", {"loggedinanon": loggedinanon, "users_dic": users_dic, "user_anon": user_anon, "loggedinauthor": loggedinauthor, "dics_word": dics_word, 'words_pronunciation_form': words_pronunciation_form, "pronunciation_inst": pronunciation,
			"users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_dic_word_pronunciations.html", {"user_anon": user_anon, "users_dic": users_dic, "dics_word": dics_word, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_dic_word_count')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	the_response.set_cookie('word', word)
	return the_response


def tob_word_pronunciation(request, word_id, pronunciation_id):
	word = Word.objects.get(id=word_id)

	calculate_sponsor_price(dics_word)
	
	registerform = UserCreationForm()
	
		
	page_views, created = Pageviews.objects.get_or_create(page="tob_word_pronunciation")
	page_views.views += 1
	page_views.save()	
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		words_pronunciation_form = IPA_pronunciationForm()
	
	pronunciation = int(pronunciation_id)
	if pronunciation == 0:
		if request.user.username == user:
			if request.method == 'POST':
				words_pronunciations = IPA_pronunciationForm(request.POST)
				if words_pronunciations.is_valid():
					pron_inst = IPA_pronunciation.objects.create(the_IPA_itself=words_pronunciations.cleaned_data['the_IPA_itself'], homophones=words_pronunciations.cleaned_data['homophones'], author=loggedinauthor)
					word.pronunciations.add(pron_inst)
					word.latest_change_date = timezone.now()
					word.trickle()
					word.update_sponsors()
					
	else:
		if IPA_pronunciation.objects.get(id=pronunciation):
			pron_inst = IPA_pronunciation.objects.get(id=pronunciation)
			pron_inst.views += 1
			pron_inst.save()
			if request.user.username == user:
				if request.method == 'POST':
					words_pronunciations = IPA_pronunciationForm(data=request.POST)
					if words_pronunciations.is_valid():
						pron_inst.the_IPA_itself = words_pronunciations.cleaned_data['the_IPA_itself']
						pron_inst.homophones = words_pronunciations.cleaned_data['homophones']
						pron_inst.save()
						word.latest_change_date = timezone.now()
						word.trickle()
						word.update_sponsors()
						word.save()
				else:
					IPA_pronunciationForm(instance=pron_inst)

	if request.user.is_authenticated:
		the_response = render(request, "tob_word_pronunciation.html", {"loggedinanon": loggedinanon, "user_anon": user_anon, "loggedinauthor": loggedinauthor, "dics_word": dics_word, 'words_pronunciation_form': words_pronunciation_form, "pronunciation_inst": pronunciation,
			"users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_word_pronunciation.html", {"user_anon": user_anon, "dics_word": dics_word, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_dic_word_count')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	the_response.set_cookie('word', word)
	return the_response


def tob_pronunciation(request, pronunciation_id):
	
	calculate_sponsor_price(dics_word)
	
	registerform = UserCreationForm()
	
		
	page_views, created = Pageviews.objects.get_or_create(page="tob_pronunciation")
	page_views.views += 1
	page_views.save()	
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		words_pronunciation_form = IPA_pronunciationForm()
	
	pronunciation = int(pronunciation_id)
	if pronunciation == 0:
		if request.user.username == user:
			if request.method == 'POST':
				words_pronunciations = IPA_pronunciationForm(request.POST)
				if words_pronunciations.is_valid():
					pron_inst = IPA_pronunciation.objects.create(the_IPA_itself=words_pronunciations.cleaned_data['the_IPA_itself'], homophones=words_pronunciations.cleaned_data['homophones'], author=loggedinauthor)
					
	else:
		if IPA_pronunciation.objects.get(id=pronunciation):
			pron_inst = IPA_pronunciation.objects.get(id=pronunciation)
			pron_inst.views += 1
			pron_inst.save()
			if request.user.username == user:
				if request.method == 'POST':
					words_pronunciations = IPA_pronunciationForm(data=request.POST)
					if words_pronunciations.is_valid():
						pron_inst.the_IPA_itself = words_pronunciations.cleaned_data['the_IPA_itself']
						pron_inst.homophones = words_pronunciations.cleaned_data['homophones']
						pron_inst.save()
						
				else:
					IPA_pronunciationForm(instance=pron_inst)
			if request.user.is_authenticated:
				the_response = render(request, "tob_word_pronunciation.html", {"loggedinanon": loggedinanon, "user_anon": user_anon, "loggedinauthor": loggedinauthor, "pron": pron_inst, 'words_pronunciation_form': words_pronunciation_form, "pronunciation_inst": pronunciation,
					"users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
					"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
			else:
				the_response = render(request, "tob_word_pronunciation.html", {"user_anon": user_anon, "dics_word": dics_word, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_dic_word_count')
	the_response.set_cookie('viewing_user', user)
	return the_response




def tob_pronunciation(request, pronunciation_id):
	pronunciation = IPA_pronunciation.objects.get(id=int(pronunciation_id)) 

	return redirect('Bable:tob_users_dic_word_pronunciation', pronunciation.word.home_dictionary.author.username, pronunciation.word.home_dictionary.the_dictionary_itself, pronunciation.word.the_word_itself, pronunciation.id)


def tob_users_dic_word_attribute(request, user, dictionary, word, attribute):
	if User.objects.get(username=user):
		user_themself = User.objects.get(username=user)
		user_anon = Anon.objects.get(username=user_themself)
	else:
		return HttpResponse("Incorrect User")
	if not user_anon.dictionaries.filter(the_dictionary_itself=dictionary):
		request.COOKIES['current'] = ('tob_user_view_count')
		return base_redirect(request, 0)
	users_dic = user_anon.dictionaries.get(the_dictionary_itself=dictionary) # or the_dictionary_itself=
	users_dic.views += 1
	users_dic.update_purchases()
	users_dic.save()
	if not users_dic.words.filter(the_word_itself=word):
		request.COOKIES['current'] = ('tob_users_dic')
		return base_redirect(request, 0)

	dics_word = users_dic.words.get(the_word_itself=word)
	
	registerform = UserCreationForm()

	page_views, created = Pageviews.objects.get_or_create(page="tob_users_dic_word_attribute")
	page_views.views += 1
	page_views.save()	
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
	else:
		return redirect('Bable:tob_users_dic_word_count', user, dictionary, word, 0)

	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		comment_form = Comment_SourceForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		attribute_sort_form = AttributeSortForm(request)
		word_sort_form = WordSortForm(request)

		dics_word_attributes = dics_word.attributes.order_by(loggedinanon.attribute_sort_char)
		

	words_attribute_form = AttributeForm(prefix='w')
	wadf = DefinitionForm(prefix='d')
	wahf = HomonymForm(prefix='h')
	wasf = SynonymForm(prefix='s')
	waaf = AntonymForm(prefix='a')

	if int(attribute) == 0:
		if request.user.username == user:
			if request.method == 'POST':
				words_attribute_form = AttributeForm(data=request.POST, prefix='w')
				if words_attribute_form.is_valid():
					words_attribute_form.save()
					attribute_inst = Attribute.objects.get(id=words_attribute_form.instance.id)
					
					dics_word.attributes.add(attribute_inst)
					wadf = DefinitionForm(prefix='d', data=request.POST)
					wahf = HomonymForm(prefix='h', data=request.POST)
					wasf = SynonymForm(prefix='s', data=request.POST)
					waaf = AntonymForm(prefix='a', data=request.POST)
					if wadf.is_valid():
						definition_inst = Definition.objects.create(the_definition_itself=wadf.cleaned_data['the_definition_itself'], author=loggedinauthor)
						attribute_inst.definitions.add(definition_inst)
					if wahf.is_valid():
						if ',' in wahf.cleaned_data['the_homonym_itself']:
							if len(wahf.cleaned_data['the_homonym_itself'].split(', ')):
								for split in wahf.cleaned_data['the_homonym_itself'].split(', '):
									homonym_inst = Homonym.objects.create(the_homonym_itself=split, author=loggedinauthor)
									attribute_inst.homonyms.add(homonym_inst)
						else:
							homonym_inst = Homonym.objects.create(the_homonym_itself=wahf.cleaned_data['the_homonym_itself'], author=loggedinauthor)
							attribute_inst.homonyms.add(homonym_inst)
					if wasf.is_valid():
						if ',' in wasf.cleaned_data['the_synonym_itself']:
							if len(wahf.cleaned_data['the_synonym_itself'].split(', ')):
								for split in wahf.cleaned_data['the_synonym_itself'].split(', '):
									synonym_inst = Synonym.objects.create(the_synonym_itself=split, author=loggedinauthor)
									attribute_inst.synonyms.add(synonym_inst)
						else:
							synonym_inst = Synonym.objects.create(the_synonym_itself=wasf.cleaned_data['the_synonym_itself'], author=loggedinauthor)
							attribute_inst.synonyms.add(synonym_inst)
					if waaf.is_valid():
						if ',' in waaf.cleaned_data['the_antonym_itself']:
							if len(wahf.cleaned_data['the_antonym_itself'].split(', ')):
								for split in wahf.cleaned_data['the_antonym_itself'].split(', '):
									antonym_inst = Antonym.objects.create(the_antonym_itself=split, author=loggedinauthor)
									attribute_inst.antonyms.add(antonym_inst)
						else:
							antonym_inst = Antonym.objects.create(the_antonym_itself=waaf.cleaned_data['the_antonym_itself'], author=loggedinauthor)
							attribute_inst.antonyms.add(antonym_inst)
					attribute_inst.save()
					dics_word.latest_change_date = timezone.now()
					dics_word.trickle()
					dics_word.update_sponsors()
					dics_word.save()
					users_dic.latest_change_date = timezone.now()
					users_dic.save()
	else:
		if Attribute.objects.get(id=int(attribute)):
			attribute_inst = Attribute.objects.get(id=int(attribute))
			words_attribute_form = AttributeForm(instance=attribute_inst, prefix='w')
			attribute_inst.views += 1
			attribute_inst.save()
			if request.user.username == user:
				if request.method == 'POST':
					wadf = DefinitionForm(prefix='d', data=request.POST)
					wahf = HomonymForm(prefix='h', data=request.POST)
					wasf = SynonymForm(prefix='s', data=request.POST)
					waaf = AntonymForm(prefix='a', data=request.POST)
					if attribute_inst.definitions.first():
						attribute_inst.definitions.first().delete()
					if attribute_inst.homonyms.first():
						attribute_inst.homonyms.first().delete()
					if attribute_inst.synonyms.first():
						attribute_inst.synonyms.first().delete()
					if attribute_inst.antonyms.first():
						attribute_inst.antonyms.first().delete()
					words_attribute_form = AttributeForm(instance=attribute_inst, data=request.POST, prefix='w')
					if words_attribute_form.is_valid():
						words_attribute_form.save()
						if wadf.is_valid():
							definition_inst = Definition.objects.create(the_definition_itself=wadf.cleaned_data['the_definition_itself'], author=loggedinauthor)
							attribute_inst.definitions.add(definition_inst)
						if wahf.is_valid():
							if len(wahf.cleaned_data['the_homonym_itself'].split(', ')):
								for split in wahf.cleaned_data['the_homonym_itself'].split(', '):
									homonym_inst = Homonym.objects.create(the_homonym_itself=split, author=loggedinauthor)
									attribute_inst.homonyms.add(homonym_inst)
							else:
								homonym_inst = Homonym.objects.create(the_homonym_itself=wahf.cleaned_data['the_homonym_itself'], author=loggedinauthor)
								attribute_inst.homonyms.add(homonym_inst)
						if wasf.is_valid():
							if len(wahf.cleaned_data['the_synonym_itself'].split(', ')):
								for split in wahf.cleaned_data['the_synonym_itself'].split(', '):
									synonym_inst = Synonym.objects.create(the_synonym_itself=split, author=loggedinauthor)
									attribute_inst.synonyms.add(synonym_inst)
							else:
								synonym_inst = Synonym.objects.create(the_synonym_itself=wasf.cleaned_data['the_synonym_itself'], author=loggedinauthor)
								attribute_inst.synonyms.add(synonym_inst)
						if waaf.is_valid():
							if len(wahf.cleaned_data['the_antonym_itself'].split(', ')):
								for split in wahf.cleaned_data['the_antonym_itself'].split(', '):
									antonym_inst = Antonym.objects.create(the_antonym_itself=split, author=loggedinauthor)
									attribute_inst.antonyms.add(antonym_inst)
							else:
								antonym_inst = Antonym.objects.create(the_antonym_itself=waaf.cleaned_data['the_antonym_itself'], author=loggedinauthor)
								attribute_inst.antonyms.add(antonym_inst)
					
					attribute_inst.save()
					dics_word.latest_change_date = timezone.now()
					dics_word.trickle()
					dics_word.update_sponsors()
					dics_word.save()
					users_dic.latest_change_date = timezone.now()
					users_dic.save()

				else:
					words_attribute_form = AttributeForm(instance=attribute_inst, prefix='w')
					if attribute_inst.definitions.first():
						wadf = DefinitionForm(prefix='d', instance=attribute_inst.definitions.first())
					else:
						wadf = DefinitionForm(prefix='d')
					if attribute_inst.homonyms.first():
						wahf = HomonymForm(prefix='h', instance=attribute_inst.homonyms.first())
					else:
						wahf = HomonymForm(prefix='h')
					if attribute_inst.synonyms.first():
						wasf = SynonymForm(prefix='s', instance=attribute_inst.synonyms.first())
					else:
						wasf = SynonymForm(prefix='s')
					if attribute_inst.antonyms.first():
						waaf = AntonymForm(prefix='a', instance=attribute_inst.antonyms.first())
					else:
						waaf = AntonymForm(prefix='a')
		
	if request.user.is_authenticated:
		the_response = render(request, "tob_users_dic_word_attributes.html", {"user_anon": user_anon, "dics_word_attributes": dics_word_attributes, "attribute_sort_form": attribute_sort_form, "word_sort_form": word_sort_form, "loggedinanon": loggedinanon, "loggedinauthor": loggedinauthor, "dics_word": dics_word, "attribute_instance_id": int(attribute),
			'words_attribute_form': words_attribute_form, "wadf": wadf, "wahf": wahf, "wasf": wasf, "waaf": waaf, "users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, 'comment_form': comment_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:

		dics_word_attributes = dics_word.attributes.all()
		the_response = render(request, "tob_users_dic_word_attributes.html", {"user_anon": user_anon, "dics_word": dics_word,
			"registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_dic_word_attribute')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	the_response.set_cookie('word', word)
	the_response.set_cookie('attribute', attribute)
	return the_response


def tob_word_attribute(request, word_id, attribute_id):
	word = Word.objects.filter(id=int(word_id)).filter(author=None).first()
	
	registerform = UserCreationForm()
	page_views, created = Pageviews.objects.get_or_create(page="tob_word_attribute")
	page_views.views += 1
	page_views.save()	
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

	if request.user.is_authenticated:
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		comment_form = Comment_SourceForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

	words_attribute_form = AttributeForm(prefix='w')
	wadf = DefinitionForm(prefix='d')
	wahf = HomonymForm(prefix='h')
	wasf = SynonymForm(prefix='s')
	waaf = AntonymForm(prefix='a')

	if int(attribute_id) == 0:
		if request.user.username == user:
			if request.method == 'POST':
				words_attribute_form = AttributeForm(data=request.POST, prefix='w')
				if words_attribute_form.is_valid():
					words_attribute_form.save()
					attribute_inst = Attribute.objects.get(id=words_attribute_form.instance.id)
					
					word.attributes.add(attribute_inst)
					wadf = DefinitionForm(prefix='d', data=request.POST)
					wahf = HomonymForm(prefix='h', data=request.POST)
					wasf = SynonymForm(prefix='s', data=request.POST)
					waaf = AntonymForm(prefix='a', data=request.POST)
					if wadf.is_valid():
						definition_inst = Definition.objects.create(the_definition_itself=wadf.cleaned_data['the_definition_itself'], author=loggedinauthor)
						attribute_inst.definitions.add(definition_inst)
					if wahf.is_valid():
						if ',' in wahf.cleaned_data['the_homonym_itself']:
							if len(wahf.cleaned_data['the_homonym_itself'].split(', ')):
								for split in wahf.cleaned_data['the_homonym_itself'].split(', '):
									homonym_inst = Homonym.objects.create(the_homonym_itself=split, author=loggedinauthor)
									attribute_inst.homonyms.add(homonym_inst)
						else:
							homonym_inst = Homonym.objects.create(the_homonym_itself=wahf.cleaned_data['the_homonym_itself'], author=loggedinauthor)
							attribute_inst.homonyms.add(homonym_inst)
					if wasf.is_valid():
						if ',' in wasf.cleaned_data['the_synonym_itself']:
							if len(wahf.cleaned_data['the_synonym_itself'].split(', ')):
								for split in wahf.cleaned_data['the_synonym_itself'].split(', '):
									synonym_inst = Synonym.objects.create(the_synonym_itself=split, author=loggedinauthor)
									attribute_inst.synonyms.add(synonym_inst)
						else:
							synonym_inst = Synonym.objects.create(the_synonym_itself=wasf.cleaned_data['the_synonym_itself'], author=loggedinauthor)
							attribute_inst.synonyms.add(synonym_inst)
					if waaf.is_valid():
						if ',' in waaf.cleaned_data['the_antonym_itself']:
							if len(wahf.cleaned_data['the_antonym_itself'].split(', ')):
								for split in wahf.cleaned_data['the_antonym_itself'].split(', '):
									antonym_inst = Antonym.objects.create(the_antonym_itself=split, author=loggedinauthor)
									attribute_inst.antonyms.add(antonym_inst)
						else:
							antonym_inst = Antonym.objects.create(the_antonym_itself=waaf.cleaned_data['the_antonym_itself'], author=loggedinauthor)
							attribute_inst.antonyms.add(antonym_inst)
					attribute_inst.save()
					word.latest_change_date = timezone.now()
					word.trickle()
					word.update_sponsors()
					word.save()
					
	else:
		if Attribute.objects.get(id=int(attribute)):
			attribute_inst = Attribute.objects.get(id=int(attribute))
			words_attribute_form = AttributeForm(instance=attribute_inst, prefix='w')
			attribute_inst.views += 1
			attribute_inst.save()
			if request.user.username == user:
				if request.method == 'POST':
					wadf = DefinitionForm(prefix='d', data=request.POST)
					wahf = HomonymForm(prefix='h', data=request.POST)
					wasf = SynonymForm(prefix='s', data=request.POST)
					waaf = AntonymForm(prefix='a', data=request.POST)
					if attribute_inst.definitions.first():
						attribute_inst.definitions.first().delete()
					if attribute_inst.homonyms.first():
						attribute_inst.homonyms.first().delete()
					if attribute_inst.synonyms.first():
						attribute_inst.synonyms.first().delete()
					if attribute_inst.antonyms.first():
						attribute_inst.antonyms.first().delete()
					words_attribute_form = AttributeForm(instance=attribute_inst, data=request.POST, prefix='w')
					if words_attribute_form.is_valid():
						words_attribute_form.save()
						if wadf.is_valid():
							definition_inst = Definition.objects.create(the_definition_itself=wadf.cleaned_data['the_definition_itself'], author=loggedinauthor)
							attribute_inst.definitions.add(definition_inst)
						if wahf.is_valid():
							if len(wahf.cleaned_data['the_homonym_itself'].split(', ')):
								for split in wahf.cleaned_data['the_homonym_itself'].split(', '):
									homonym_inst = Homonym.objects.create(the_homonym_itself=split, author=loggedinauthor)
									attribute_inst.homonyms.add(homonym_inst)
							else:
								homonym_inst = Homonym.objects.create(the_homonym_itself=wahf.cleaned_data['the_homonym_itself'], author=loggedinauthor)
								attribute_inst.homonyms.add(homonym_inst)
						if wasf.is_valid():
							if len(wahf.cleaned_data['the_synonym_itself'].split(', ')):
								for split in wahf.cleaned_data['the_synonym_itself'].split(', '):
									synonym_inst = Synonym.objects.create(the_synonym_itself=split, author=loggedinauthor)
									attribute_inst.synonyms.add(synonym_inst)
							else:
								synonym_inst = Synonym.objects.create(the_synonym_itself=wasf.cleaned_data['the_synonym_itself'], author=loggedinauthor)
								attribute_inst.synonyms.add(synonym_inst)
						if waaf.is_valid():
							if len(wahf.cleaned_data['the_antonym_itself'].split(', ')):
								for split in wahf.cleaned_data['the_antonym_itself'].split(', '):
									antonym_inst = Antonym.objects.create(the_antonym_itself=split, author=loggedinauthor)
									attribute_inst.antonyms.add(antonym_inst)
							else:
								antonym_inst = Antonym.objects.create(the_antonym_itself=waaf.cleaned_data['the_antonym_itself'], author=loggedinauthor)
								attribute_inst.antonyms.add(antonym_inst)
					
					attribute_inst.save()
					word.latest_change_date = timezone.now()
					word.trickle()
					word.update_sponsors()
					word.save()
					

				else:
					words_attribute_form = AttributeForm(instance=attribute_inst, prefix='w')
					if attribute_inst.definitions.first():
						wadf = DefinitionForm(prefix='d', instance=attribute_inst.definitions.first())
					else:
						wadf = DefinitionForm(prefix='d')
					if attribute_inst.homonyms.first():
						wahf = HomonymForm(prefix='h', instance=attribute_inst.homonyms.first())
					else:
						wahf = HomonymForm(prefix='h')
					if attribute_inst.synonyms.first():
						wasf = SynonymForm(prefix='s', instance=attribute_inst.synonyms.first())
					else:
						wasf = SynonymForm(prefix='s')
					if attribute_inst.antonyms.first():
						waaf = AntonymForm(prefix='a', instance=attribute_inst.antonyms.first())
					else:
						waaf = AntonymForm(prefix='a')
		
	if request.user.is_authenticated:
		the_response = render(request, "tob_word_attributes.html", {"loggedinanon": loggedinanon, "loggedinauthor": loggedinauthor, "word": word, "attribute_instance_id": int(attribute_id),
			'words_attribute_form': words_attribute_form, "wadf": wadf, "wahf": wahf, "wasf": wasf, "waaf": waaf, "users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, 'comment_form': comment_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_word_attributes.html", {"user_anon": user_anon, "word": word,
			"registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_word_attribute')
	the_response.set_cookie('word', word_id)
	the_response.set_cookie('attribute', attribute_id)
	return the_response





def tob_users_dic_word_similarity(request, user, dictionary, word, similarity):
	if User.objects.get(username=user):
		user_themself = User.objects.get(username=user)
		user_anon = Anon.objects.get(username=user_themself)
	else:
		return HttpResponse("Incorrect User")
	if not user_anon.dictionaries.filter(the_dictionary_itself=dictionary):
		request.COOKIES['current'] = ('tob_user_view_count')
		return base_redirect(request, 0)
	users_dic = user_anon.dictionaries.get(the_dictionary_itself=dictionary) # or the_dictionary_itself=
	users_dic.views += 1
	users_dic.update_purchases()
	users_dic.save()
	if not users_dic.words.filter(the_word_itself=word):
		request.COOKIES['current'] = ('tob_users_dic')
		return base_redirect(request, 0)

	dics_word = users_dic.words.get(the_word_itself=word)
	
	registerform = UserCreationForm()
	
	page_views, created = Pageviews.objects.get_or_create(page="tob_users_dic_word_similarity")
	page_views.views += 1
	page_views.save()	
	
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		comment_form = Comment_SourceForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

	similarity_form = SimulacrumForm(prefix='sim')
	connexia_form = ConnexionForm(prefix='con')

	similarity = int(similarity)
	if similarity == 0:
		if request.user.username == user:
			if request.method == 'POST':
				similarity_form = SimulacrumForm(data=request.POST, prefix='sim')
				if similarity_form.is_valid():
					similarity_inst = Simulacrum.objects.create(the_simulacrum_itself=similarity_form.cleaned_data['the_simulacrum_itself'], author=loggedinauthor)
					similarity = similarity_inst.id
					dics_word.similarities.add(similarity_inst)
					connexia_form = ConnexionForm(data=request.POST, prefix='con')
					if connexia_form.is_valid():
						connexion_inst = Connexion.objects.create(the_connexion_itself=connexia_form.cleaned_data['the_connexion_itself'], author=loggedinauthor)
						similarity_inst.connexia.add(connexion_inst)
						similarity_inst.views += 1
						similarity_inst.save()
						dics_word.latest_change_date = timezone.now
						dics_word.trickle()
						dics_word.update_sponsors()
						dics_word.save()
						users_dic.latest_change_date = timezone.now
						users_dic.save()
	else:
		if Simulacrum.objects.get(id=similarity):
			similarity_inst = Simulacrum.objects.get(id=similarity)
			if request.user.username == user:
				if request.method == 'POST':
					connexia_form = ConnexionForm(data=request.POST, prefix='con')
					if connexia_form.is_valid():
						connexion_inst = Connexion.objects.create(the_connexion_itself=connexia_form.cleaned_data['the_connexion_itself'], author=loggedinauthor)
						similarity_inst.connexia.add(connexion_inst)
						similarity_inst.views += 1
						similarity_inst.save()
						dics_word.latest_change_date = timezone.now
						dics_word.trickle()
						dics_word.update_sponsors()
						dics_word.save()
						users_dic.latest_change_date = timezone.now
						users_dic.save()
				else:
					similarity_form = SimulacrumForm(prefix='sim', instance=similarity_inst)
	
	if request.user.is_authenticated:
		the_response = render(request, "tob_users_dic_word_similarities.html", {"user_anon": user_anon, "loggedinanon": loggedinanon, "loggedinauthor": loggedinauthor, "dics_word": dics_word, "similarity": similarity,
			'similarity_form': similarity_form, 'connexia_form': connexia_form, "users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, 'comment_form': comment_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_dic_word_similarities.html", {"user_anon": user_anon, "dics_word": dics_word,
			"users_dic": users_dic, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_dic_word_similarities')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	the_response.set_cookie('word', word)
	the_response.set_cookie('similarity', similarity)
	return the_response




def tob_users_dic_word_translation(request, user, dictionary, word, translation):
	if User.objects.get(username=user):
		user_themself = User.objects.get(username=user)
		user_anon = Anon.objects.get(username=user_themself)
	else:
		return HttpResponse("Incorrect User")
	if not user_anon.dictionaries.filter(the_dictionary_itself=dictionary):
		request.COOKIES['current'] = ('tob_user_view_count')
		return base_redirect(request, 0)
	users_dic = user_anon.dictionaries.get(the_dictionary_itself=dictionary) # or the_dictionary_itself=
	users_dic.views += 1
	users_dic.update_purchases()
	users_dic.save()
	if not users_dic.words.filter(the_word_itself=word):
		request.COOKIES['current'] = ('tob_users_dic')
		return base_redirect(request, 0)

	dics_word = users_dic.words.get(the_word_itself=word)
	
	registerform = UserCreationForm()
	
	page_views, created = Pageviews.objects.get_or_create(page="tob_users_dic_word_translation")
	page_views.views += 1
	page_views.save()	
	
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		comment_form = Comment_SourceForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		
		trans_form = TranslationForm()
	
	translation = int(translation)
	if translation == 0:
		if request.user.username == user:
			if request.method == 'POST':
				trans_form = TranslationForm(data=request.POST)
				if trans_form.is_valid():
					trans_inst = Translation.objects.create(the_translation_before=trans_form.cleaned_data['the_translation_before'], the_translation_after=trans_form.cleaned_data['the_translation_after'], author=loggedinauthor)
					dics_word.translations.add(trans_inst)
					dics_word.latest_change_date = timezone.now
					dics_word.trickle()
					dics_word.update_sponsors()
					dics_word.save()
					users_dic.latest_change_date = timezone.now
					users_dic.save()
	else:
		if Translation.objects.get(id=translation):
			trans_inst = Translation.objects.get(id=translation)
			trans_inst.views += 1
			trans_inst.save()
			if request.user.username == user:
				if request.method == 'POST':
					trans_form = TranslationForm(data=request.POST)
					if trans_form.is_valid():
						trans_inst.the_translation_before = trans_form.cleaned_data['the_translation_before']
						trans_inst.the_translation_after = trans_form.cleaned_data['the_translation_after']
						trans_inst.save()
						dics_word.latest_change_date = timezone.now
						dics_word.trickle()
						dics_word.update_sponsors()
						dics_word.save()
						users_dic.latest_change_date = timezone.now
						users_dic.save()
				else:
					trans_form = TranslationForm(instance=trans_inst)

	if request.user.is_authenticated:
		the_response = render(request, "tob_users_dic_word_translations.html", {"user_anon": user_anon, "trans_form": trans_form, "loggedinanon": loggedinanon, "loggedinauthor": loggedinauthor, "dics_word": dics_word, 'trans_form': trans_form, "users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, 'comment_form': comment_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_dic_word_translations.html", {"user_anon": user_anon, "dics_word": dics_word, "users_dic": users_dic, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_dic_word_translations')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	the_response.set_cookie('word', word)
	the_response.set_cookie('translation', translation)
	return the_response


def tob_word_translation(request,  word_id, translation_id):
	registerform = UserCreationForm()
	
		
	
	if Word.objects.get(int(word_id)):
		word = word.objects.get(int(word_id))

	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		comment_form = Comment_SourceForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		
		trans_form = TranslationForm()
	
	translation = int(translation)
	if word_id:
		if translation_id == 0:
			if request.user.username == user:
				if request.method == 'POST':
					trans_form = TranslationForm(data=request.POST)
					if trans_form.is_valid():
						trans_inst = Translation.objects.create(the_translation_before=trans_form.cleaned_data['the_translation_before'], the_translation_after=trans_form.cleaned_data['the_translation_after'], author=loggedinauthor)
						word.translations.add(trans_inst)
						word.latest_change_date = timezone.now
						word.trickle()
						word.update_sponsors()
						word.save()
						
		else:
			if Translation.objects.get(id=int(translation_id)):
				trans_inst = Translation.objects.get(id=int(translation_id))
				trans_inst.views += 1
				trans_inst.save()
				if request.user.username == user:
					if request.method == 'POST':
						trans_form = TranslationForm(data=request.POST)
						if trans_form.is_valid():
							trans_inst.the_translation_before = trans_form.cleaned_data['the_translation_before']
							trans_inst.the_translation_after = trans_form.cleaned_data['the_translation_after']
							trans_inst.save()
							word.latest_change_date = timezone.now
							word.trickle()
							word.update_sponsors()
							word.save()
							
					else:
						trans_form = TranslationForm(instance=trans_inst)

	if request.user.is_authenticated:
		the_response = render(request, "tob_word_translations.html", {"loggedinanon": loggedinanon, "word": word, 'trans_form': trans_form, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, 'comment_form': comment_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_dic_word_translations.html", {"user_anon": user_anon, "loggedinanon": loggedinanon, "word": word, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_dic_word_translations')
	the_response.set_cookie('word', word)
	the_response.set_cookie('translation', translation_id)
	return the_response


def tob_users_dic_word_example(request, user, dictionary, word, example):
	if User.objects.get(username=user):
		user_themself = User.objects.get(username=user)
		user_anon = Anon.objects.get(username=user_themself)
	else:
		return HttpResponse("Incorrect User")
	if not user_anon.dictionaries.filter(the_dictionary_itself=dictionary):
		request.COOKIES['current'] = ('tob_user_view_count')
		return base_redirect(request, 0)
	users_dic = user_anon.dictionaries.get(the_dictionary_itself=dictionary) # or the_dictionary_itself=
	users_dic.views += 1
	users_dic.update_purchases()
	users_dic.save()
	if not users_dic.words.filter(the_word_itself=word):
		request.COOKIES['current'] = ('tob_users_dic')
		return base_redirect(request, 0)

	dics_word = users_dic.words.get(the_word_itself=word)
	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		comment_form = Comment_SourceForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		
		example_form = ExampleForm()
	
	example = int(example)
	if example == 0:
		if request.user.username == user:
			if request.method == 'POST':
				example_form = ExampleForm(data=request.POST)
				if example_form.is_valid():
					exa_inst = Example.objects.create(the_example_itself=example_form.cleaned_data['the_example_itself'], author=loggedinauthor)
					exa_inst.words.add(dics_word.to_source())
					exa_inst.dictionaries.add(users_dic.to_source())
					exa_inst.save()
					dics_word.examples.add(exa_inst)
					dics_word.latest_change_date = timezone.now()
					dics_word.trickle()
					dics_word.update_sponsors()
					dics_word.save()
					users_dic.latest_change_date = timezone.now()
					users_dic.save()
	else:
		if Example.objects.get(id=example):
			exa_inst = Example.objects.get(id=example)
			exa_inst.views += 1
			exa_inst.save()
			if request.user.username == user:
				if request.method == 'POST':
					exa_form = ExampleForm(data=request.POST)
					if exa_form.is_valid():
						exa_inst.the_example_itself = example_form.cleaned_data['the_example_itself']
						exa_inst.save()
				else:
					example_form = ExampleForm(instance=exa_inst)
		
	if request.user.is_authenticated:
		the_response = render(request, "tob_users_dic_word_examples.html", {"user_anon": user_anon, "loggedinanon": loggedinanon, "loggedinauthor": loggedinauthor, "dics_word": dics_word, 
			'exa_form': example_form, 'instance_id': example, "users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, 'comment_form': comment_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_dic_word_examples.html", {"user_anon": user_anon, "dics_word": dics_word, 'instance_id': example, 
			"users_dic": users_dic, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_dic_word_example')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	the_response.set_cookie('word', word)
	the_response.set_cookie('example', example)
	return the_response

def tob_word_example(request, word_id, example_id):
	if User.objects.get(username=user):
		user_themself = User.objects.get(username=user)
		user_anon = Anon.objects.get(username=user_themself)
	else:
		return HttpResponse("Incorrect User")
	if not user_anon.dictionaries.filter(the_dictionary_itself=dictionary):
		request.COOKIES['current'] = ('tob_user_view_count')
		return base_redirect(request, 0)
	users_dic = user_anon.dictionaries.get(the_dictionary_itself=dictionary) # or the_dictionary_itself=
	users_dic.update_purchases()
	if not users_dic.words.filter(the_word_itself=word):
		request.COOKIES['current'] = ('tob_users_dic')
		return base_redirect(request, 0)

	dics_word = users_dic.words.get(the_word_itself=word)
	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		comment_form = Comment_SourceForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		
		example_form = ExampleForm()
	
	example = int(example)
	if example == 0:
		if request.user.username == user:
			if request.method == 'POST':
				example_form = ExampleForm(data=request.POST)
				if example_form.is_valid():
					exa_inst = Example.objects.create(the_example_itself=example_form.cleaned_data['the_example_itself'], author=loggedinauthor)
					exa_inst.words.add(dics_word.to_source())
					exa_inst.dictionaries.add(users_dic.to_source())
					exa_inst.save()
					dics_word.examples.add(exa_inst)
					dics_word.latest_change_date = timezone.now()
					dics_word.trickle()
					dics_word.update_sponsors()
					dics_word.save()
					users_dic.latest_change_date = timezone.now()
					users_dic.save()
	else:
		if Example.objects.get(id=example):
			exa_inst = Example.objects.get(id=example)
			exa_inst.views += 1
			exa_inst.save()
			if request.user.username == user:
				if request.method == 'POST':
					exa_form = ExampleForm(data=request.POST)
					if exa_form.is_valid():
						exa_inst.the_example_itself = example_form.cleaned_data['the_example_itself']
						exa_inst.save()
				else:
					example_form = ExampleForm(instance=exa_inst)
		
	if request.user.is_authenticated:
		the_response = render(request, "tob_users_dic_word_examples.html", {"user_anon": user_anon, "loggedinanon": loggedinanon, "dics_word": dics_word, 
			'exa_form': example_form, 'instance_id': example, "users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, 'comment_form': comment_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_dic_word_examples.html", {"user_anon": user_anon, "loggedinanon": loggedinanon, "dics_word": dics_word, 
			"users_dic": users_dic, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_dic_word_example')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	the_response.set_cookie('word', word)
	the_response.set_cookie('example', example)
	return the_response



def tob_users_dic_word_story(request, user, dictionary, word, story):
	if User.objects.get(username=user):
		user_themself = User.objects.get(username=user)
		user_anon = Anon.objects.get(username=user_themself)
	else:
		return HttpResponse("Incorrect User")
	if not user_anon.dictionaries.filter(the_dictionary_itself=dictionary):
		request.COOKIES['current'] = ('tob_user_view_count')
		return base_redirect(request, 0)
	users_dic = user_anon.dictionaries.get(the_dictionary_itself=dictionary) # or the_dictionary_itself=
	users_dic.views += 1
	users_dic.update_purchases()
	users_dic.save()
	if not users_dic.words.filter(the_word_itself=word):
		request.COOKIES['current'] = ('tob_users_dic')
		return base_redirect(request, 0)

	dics_word = users_dic.words.get(the_word_itself=word)
	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		comment_form = Comment_SourceForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

	
		story_form = StoryForm(prefix='s')
	
	story_inst = 0
	story = int(story)
	if story == 0:
		if request.user.username == user:
			if request.method == 'POST':
				story_form = StoryForm(request.POST)
				print('here')
				if story_form.is_valid():
					print('there')
					story_inst = Story.objects.create(the_story_itself=story_form.cleaned_data['the_story_itself'], author=loggedinauthor)
					dics_word.stories.add(story_inst)
					dics_word.latest_change_date = timezone.now()
					dics_word.trickle()
					dics_word.update_sponsors()
					dics_word.save()
					users_dic.latest_change_date = timezone.now()
					users_dic.save()
	else:
		if Story.objects.get(id=story):
			story_inst = Story.objects.get(id=story)
			story_inst.views += 1
			story_inst.save()
			if request.user.username == user:
				if request.method == 'POST':
					story_form = StoryForm(request.POST)
					if story_form.is_valid():
						story_inst.the_story_itself = story_form.cleaned_data['the_story_itself']
						story_inst.save()
						dics_word.latest_change_date = timezone.now()
						dics_word.trickle()
						dics_word.update_sponsors()
						dics_word.save()
						users_dic.latest_change_date = timezone.now()
						users_dic.save()
				else:
					story_form = StoryForm(instance=story_inst)
	
	if request.user.is_authenticated:
		the_response = render(request, "tob_users_dic_word_stories.html", {"story":story, "user_anon": user_anon, "users_dic": users_dic, "loggedinanon": loggedinanon, "loggedinauthor": loggedinauthor, "dics_word": dics_word, "story": story, "story_inst": story_inst, 'story_form': story_form, "users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, 'comment_form': comment_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_dic_word_stories.html", {"user_anon": user_anon, "users_dic": users_dic, "dics_word": dics_word, "users_dic": users_dic, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_dic_word_story')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	the_response.set_cookie('word', word)
	the_response.set_cookie('story', story)
	return the_response


def tob_word_story(request, word_id, story_id):
	word = Word.objects.filter(id=int(word_id)).filter(author=None).first()
	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		comment_form = Comment_SourceForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

	
		story_form = StoryForm(prefix='s')
	
	story_inst = 0
	story = int(story_id)
	if story == 0:
		if request.method == 'POST':
			story_form = StoryForm(request.POST)
			print('here')
			if story_form.is_valid():
				print('there')
				story_inst = Story.objects.create(the_story_itself=story_form.cleaned_data['the_story_itself'], author=loggedinauthor)
				word.stories.add(story_inst)
				word.latest_change_date = timezone.now()
				word.trickle()
				word.update_sponsors()
				word.save()
					
	else:
		if Story.objects.get(id=story):
			story_inst = Story.objects.get(id=story)
			story_inst.views += 1
			story_inst.save()
			if request.user.username == user:
				if request.method == 'POST':
					story_form = StoryForm(request.POST)
					if story_form.is_valid():
						story_inst.the_story_itself = story_form.cleaned_data['the_story_itself']
						story_inst.save()
						word.latest_change_date = timezone.now()
						word.trickle()
						word.update_sponsors()
						word.save()
						
				else:
					story_form = StoryForm(instance=story_inst)
	
	if request.user.is_authenticated:
		the_response = render(request, "tob_word_stories.html", {"loggedinanon": loggedinanon, "word": word, "story": story, "story_inst": story_inst, 'story_form': story_form, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, 'comment_form': comment_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_word_stories.html", {"loggedinanon": loggedinanon, "word": word, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_word_story')
	the_response.set_cookie('word', word)
	the_response.set_cookie('story', story)
	return the_response



def tob_users_dic_word_relation(request, user, dictionary, word, relation):
	if User.objects.get(username=user):
		user_themself = User.objects.get(username=user)
		user_anon = Anon.objects.get(username=user_themself)
	else:
		return HttpResponse("Incorrect User")
	if not user_anon.dictionaries.filter(the_dictionary_itself=dictionary):
		request.COOKIES['current'] = ('tob_user_view_count')
		return base_redirect(request, 0)
	users_dic = user_anon.dictionaries.get(the_dictionary_itself=dictionary) # or the_dictionary_itself=
	users_dic.views += 1
	users_dic.update_purchases()
	users_dic.save()
	if not users_dic.words.filter(the_word_itself=word):
		request.COOKIES['current'] = ('tob_users_dic')
		return base_redirect(request, 0)

	dics_word = users_dic.words.get(the_word_itself=word)
	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		comment_form = Comment_SourceForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		relation_form = RelationForm()
		
		relation = int(relation)
		if relation == 0:
			if request.user.username == user:
				if request.method == 'POST':
					relation_form = RelationForm(request.POST)
					if relation_form.is_valid():
						relation_inst = Relation.objects.create(the_relation_itself=relation_form.cleaned_data['the_relation_itself'], author=loggedinauthor)
						dics_word.relations.add(relation_inst)
						dics_word.latest_change_date = timezone.now()
						dics_word.trickle()
						dics_word.update_sponsors()
						dics_word.save()
						users_dic.latest_change_date = timezone.now()
						users_dic.save()
		else:
			if Relation.objects.get(id=relation):
				relation_inst = Relation.objects.get(id=relation)
				if request.user.username == user:
					if request.method == 'POST':
						relation_form = RelationForm(request.POST)
						if relation_form.is_valid():
							relation_inst.the_relation_itself = relation_form.cleaned_data['the_relation_itself']
							dics_word.latest_change_date = timezone.now()
							dics_word.trickle()
							dics_word.update_sponsors()
							dics_word.save()
							users_dic.latest_change_date = timezone.now()
							users_dic.save()
					else:
						relation_form = RelationForm(instance=relation_inst)
		the_response = render(request, "tob_users_dic_word_relations.html", {"relation": relation, "user_anon": user_anon, "users_dic": users_dic, "loggedinanon": loggedinanon, "loggedinauthor": loggedinauthor, "dics_word": dics_word, 'relation_form': relation_form, "users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, 'comment_form': comment_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_dic_word_relations.html", {"user_anon": user_anon, "users_dic": users_dic, "dics_word": dics_word, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_dic_word_relation')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	the_response.set_cookie('word', word)
	the_response.set_cookie('relation', relation)
	return the_response


def tob_word_relation(request, word_id, relation_id):
	word = Word.objects.filter(id=int(word_id)).filter(author=None).first()
	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

	dic_form = DictionaryForm()
	space_form = SpaceForm(request)
	post_form = PostForm(request)
	task_form = TaskForm()
	word_form = WordForm(request)
	comment_form = Comment_SourceForm(request)

	apply_votestyle_form = ApplyVotestyleForm(request)
	create_votes_form = CreateVotesForm(request)
	exclude_votes_form = ExcludeVotesForm(request)
	apply_dic_form = ApplyDictionaryForm(request)
	exclude_dic_form = ExcludeDictionaryAuthorForm()

	relation_form = RelationForm()
	
	relation = int(relation_id)
	if relation == 0:
		if request.user.username == user:
			if request.method == 'POST':
				relation_form = RelationForm(request.POST)
				if relation_form.is_valid():
					relation_inst = Relation.objects.create(the_relation_itself=relation_form.cleaned_data['the_relation_itself'], author=loggedinauthor)
					word.relations.add(relation_inst)
					word.latest_change_date = timezone.now()
					word.trickle()
					word.update_sponsors()
					word.save()
					
	else:
		if Relation.objects.get(id=relation):
			relation_inst = Relation.objects.get(id=relation)
			if request.user.username == user:
				if request.method == 'POST':
					relation_form = RelationForm(request.POST)
					if relation_form.is_valid():
						relation_inst.the_relation_itself = relation_form.cleaned_data['the_relation_itself']
						word.latest_change_date = timezone.now()
						word.trickle()
						word.update_sponsors()
						word.save()
				else:
					relation_form = RelationForm(instance=relation_inst)
	if request.user.is_authenticated:
		the_response = render(request, "tob_word_relations.html", {"loggedinanon": loggedinanon, 'relation_form': relation_form, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, 'comment_form': comment_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_word_relations.html", {"loggedinanon": loggedinanon, "word": word, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_word_relation')
	the_response.set_cookie('word', word)
	the_response.set_cookie('relation', relation)
	return the_response

def tob_users_dic_word_sponsor(request, user, dictionary, word, sponsor):
	if User.objects.get(username=user):
		user_themself = User.objects.get(username=user)
		user_anon = Anon.objects.get(username=user_themself)
	else:
		return HttpResponse("Invalid User")
	if not user_anon.dictionaries.filter(the_dictionary_itself=dictionary):
		request.COOKIES['current'] = ('tob_user_view_count')
		return base_redirect(request, 0)
	users_dic = user_anon.dictionaries.get(the_dictionary_itself=dictionary) # or the_dictionary_itself=
	users_dic.views += 1
	users_dic.update_purchases()
	users_dic.save()
	if not users_dic.words.filter(the_word_itself=word):
		request.COOKIES['current'] = ('tob_users_dic')
		return base_redirect(request, 0)

	dics_word = users_dic.words.get(the_word_itself=word)
	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=loggedinuser.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		comment_form = Comment_SourceForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		sponsor_form = SponsorForm()
		### need some kind of magic for the price limit situation...
		sponsor = int(sponsor)
		if sponsor == 0:
			if request.method == 'POST':
				sponsor_form = SponsorForm(request.POST)
				if sponsor_form.is_valid():
					if sponsor_form.cleaned_data["allowable_expenditure"] <= loggedinanon.false_wallet:
						loggedinanon.false_wallet -= sponsor_form.cleaned_data["allowable_expenditure"]
						sponsor_inst = Sponsor.objects.create(the_sponsorship_phrase=sponsor_form.cleaned_data['the_sponsorship_phrase'], img=sponsor_form.cleaned_data['img'], payperview=sponsor_form.cleaned_data['payperview'], url2=sponsor_form.cleaned_data['url2'], author=loggedinauthor, price_limit=sponsor_form.cleaned_data['price_limit'], allowable_expenditure=sponsor_form.cleaned_data['allowable_expenditure'])
						dics_word.sponsors.add(sponsor_inst)
						dics_word.latest_change_date = timezone.now()
						dics_word.trickle()
						dics_word.update_sponsors()
						dics_word.save()
						users_dic.latest_change_date = timezone.now()
						users_dic.save()
						sponsor = sponsor_inst.id
					else:
						return HttpResponse("not enough balance")
				else:
					print(sponsor_form.errors)
		else:
			if Sponsor.objects.get(id=sponsor):
				sponsor_inst = Sponsor.objects.get(id=sponsor)
				if request.user.username == sponsor_inst.author.username:
					if request.method == 'POST':
						sponsor_form = SponsorForm(request.POST)
						if sponsor_form.is_valid():
							sponsor_inst.the_sponsorship_phrase = sponsor_form.cleaned_data['the_sponsorship_phrase']
							sponsor_inst.img = sponsor_form.cleaned_data['img']
							sponsor_inst.url = sponsor_form.cleaned_data['url2']
							sponsor_inst.author = loggedinauthor
							sponsor_inst.price_limit = sponsor_form.cleaned_data['price_limit']
							sponsor_inst.payperview = sponsor_form.cleaned_data['payperview']
							sponsor_inst.save()
							dics_word.latest_change_date = timezone.now()
							dics_word.trickle()
							dics_word.update_sponsors()
							dics_word.save()
							users_dic.latest_change_date = timezone.now()
							users_dic.save()
					else:
						sponsor_form = SponsorForm(instance=sponsor_inst)
	if request.user.is_authenticated:
		the_response = render(request, "tob_users_dic_word_sponsors.html", {"user_anon": user_anon, "loggedinanon": loggedinanon, "loggedinauthor": loggedinauthor, "dics_word": dics_word, 'sponsor_form': sponsor_form, "sponsor_id": sponsor, "users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, 'comment_form': comment_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_dic_word_sponsors.html", {"user_anon": user_anon, "dics_word": dics_word, "users_dic": users_dic, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_dic_word_sponsor')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	the_response.set_cookie('word', word)
	the_response.set_cookie('sponsor', sponsor)
	return the_response



def tob_word_sponsor(request, word_id, sponsor_id):
	if word_id != 0:
		word = Word.objects.get(id=int(word_id))
	if sponsor_id != 0:
		sponsor = Sponsor.objects.get(id=int(sponsor_id))
	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=loggedinuser.username)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		comment_form = Comment_SourceForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		sponsor_form = SponsorForm()
		### need some kind of magic for the price limit situation...
		sponsor = int(sponsor)
		if sponsor == 0:
			if request.method == 'POST':
				sponsor_form = SponsorForm(request.POST)
				if sponsor_form.is_valid():
					if sponsor_form.cleaned_data["allowable_expenditure"] <= loggedinanon.false_wallet:
						loggedinanon.false_wallet -= sponsor_form.cleaned_data["allowable_expenditure"]
						sponsor_inst = Sponsor.objects.create(the_sponsorship_phrase=sponsor_form.cleaned_data['the_sponsorship_phrase'], img=sponsor_form.cleaned_data['img'], url2=sponsor_form.cleaned_data['url2'], author=loggedinauthor, payperview=sponsor_form.cleaned_data['payperview'], price_limit=sponsor_form.cleaned_data['price_limit'], allowable_expenditure=sponsor_form.cleaned_data['allowable_expenditure'])
						dics_word.sponsors.add(sponsor_inst)
						dics_word.latest_change_date = timezone.now()
						dics_word.trickle()
						dics_word.update_sponsors()
						dics_word.save()
						users_dic.latest_change_date = timezone.now()
						users_dic.save()
						sponsor = sponsor_inst.id
					else:
						return HttpResponse("not enough balance")
				else:
					print(sponsor_form.errors)
		else:
			if Sponsor.objects.get(id=sponsor):
				sponsor_inst = Sponsor.objects.get(id=sponsor)
				if request.user.username == sponsor_inst.author.username:
					if request.method == 'POST':
						sponsor_form = SponsorForm(request.POST)
						if sponsor_form.is_valid():
							sponsor_inst.the_sponsorship_phrase = sponsor_form.cleaned_data['the_sponsorship_phrase']
							sponsor_inst.img = sponsor_form.cleaned_data['img']
							sponsor_inst.url = sponsor_form.cleaned_data['url2']
							sponsor_inst.author = loggedinauthor
							sponsor_inst.price_limit = sponsor_form.cleaned_data['price_limit']
							sponsor_inst.save()
							dics_word.latest_change_date = timezone.now()
							dics_word.trickle()
							dics_word.update_sponsors()
							dics_word.save()
							users_dic.latest_change_date = timezone.now()
							users_dic.save()
					else:
						sponsor_form = SponsorForm(instance=sponsor_inst)
	if request.user.is_authenticated:
		the_response = render(request, "tob_users_dic_word_sponsors.html", {"user_anon": user_anon, "loggedinanon": loggedinanon, "word": word, 'sponsor_form': sponsor_form, "sponsor_id": sponsor, "users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, 'comment_form': comment_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_word_sponsors.html", {"user_anon": user_anon, "word": word, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_word_sponsor')
	the_response.set_cookie('word', word)
	the_response.set_cookie('sponsor', sponsor)
	return the_response

def tob_users_dic_word_space(request, user, dictionary, word, space):
	if User.objects.get(username=user):
		user_themself = User.objects.get(username=user)
		user_anon = Anon.objects.get(username=user_themself)
	else:
		return HttpResponse("Incorrect User")
	if not user_anon.dictionaries.filter(the_dictionary_itself=dictionary):
		request.COOKIES['current'] = ('tob_user_view_count')
		return base_redirect(request, 0)
	users_dic = user_anon.dictionaries.get(the_dictionary_itself=dictionary) # or the_dictionary_itself=
	users_dic.views += 1
	users_dic.update_purchases()
	users_dic.save()
	if not users_dic.words.filter(the_word_itself=word):
		request.COOKIES['current'] = ('tob_users_dic')
		return base_redirect(request, 0)
	dics_word = users_dic.words.get(the_word_itself=word)
	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		comment_form = Comment_SourceForm(request)

		space_data_form = SpaceDataForm()
		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

	space = int(space)
	words_spaces = dics_word.spaces.all()
	if space == 0:
		words_space = 0
	else:
		if SpaceSource.objects.all().filter(id=space).first():
			words_space = SpaceSource.objects.all().filter(id=space).first().to_full()

	if request.user.is_authenticated:
		the_response = render(request, "tob_users_dic_word_space.html", {"user_anon": user_anon, "loggedinanon": loggedinanon,"loggedinauthor": loggedinauthor, "dics_word": dics_word, 'space_form': space_form, "users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, 'comment_form': comment_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		the_response = render(request, "tob_users_dic_word_space.html", {"user_anon": user_anon, "dics_word": dics_word, "users_dic": users_dic, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_dic_word_space')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	the_response.set_cookie('word', word)
	the_response.set_cookie('space', space)
	return the_response

def tob_users_dic_words(request, user, dictionary, count):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.get(the_dictionary_itself=dictionary) # or the_dictionary_itself=
	users_dic.update_purchases()
	count = int(count)
	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		word_sort_form = WordSortForm(request)
		attribute_sort_form = AttributeSortForm(request)

		dic_words = users_dic.words.order_by(loggedinanon.word_sort_char)[count:count+100]
	
		the_response = render(request, "tob_users_dic_words.html", {"loggedinanon": loggedinanon, "attribute_sort_form": attribute_sort_form, "word_sort_form": word_sort_form, "dic_words": dic_words, "users_dic": users_dic, "user_anon": user_anon, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, "apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	else:
		dic_words = users_dic.words.all()[count:count+100]
	
		the_response = render(request, "tob_users_dic_words.html", {"dic_words": dic_words, "users_dic": users_dic, "user_anon": user_anon, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_users_dic_words')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	return the_response

def tob_users_dic_wordgroups(request, user, dictionary, count):
	count = int(count)
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.get(dictionary_name=dictionary) # or the_dictionary_itself=
	users_dic.update_purchases()
	dics_word = users_dic.wordgroups.get(the_word_itself=word)[count:count+100]
	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

	the_response = render(request, "tob_users_dic_word.html", {"loggedinanon": loggedinanon, "dics_word": dics_word, "users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	the_response.set_cookie('current', 'tob_users_dic_word_count')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	the_response.set_cookie('word', word)
	return the_response

def tob_users_dic_votes(request, user, dictionary, count):
	count = int(count)
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.get(dictionary_name=dictionary) # or the_dictionary_itself=
	users_dic.update_purchases()
	dics_word = users_dic.votes.get(the_word_itself=word)[count:count+100]
	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

	the_response = render(request, "tob_users_dic_word.html", {"loggedinanon": loggedinanon, "dics_word": dics_word, "users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	the_response.set_cookie('current', 'tob_users_dic_word_count')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	the_response.set_cookie('word', word)
	return the_response

def tob_users_dic_translations(request, user, dictionary, count):
	count = int(count)
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.get(dictionary_name=dictionary) # or the_dictionary_itself=
	users_dic.update_purchases()
	dics_word = users_dic.translations.get(the_word_itself=word)[count:count+100]
	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

	the_response = render(request, "tob_users_dic_word.html", {"loggedinanon": loggedinanon, "dics_word": dics_word, "users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	the_response.set_cookie('current', 'tob_users_dic_word_count')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	the_response.set_cookie('word', word)
	return the_response

def tob_users_dic_sentences(request, user, dictionary, count):
	count = int(count)
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.get(dictionary_name=dictionary) # or the_dictionary_itself=
	users_dic.update_purchases()
	dics_sentences = users_dic.sentences.get(the_word_itself=word)[count:count+100]
	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

	the_response = render(request, "tob_users_dic_word.html", {"loggedinanon": loggedinanon, "dics_word": dics_word, "users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	the_response.set_cookie('current', 'tob_users_dic_word_count')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	the_response.set_cookie('word', word)
	return the_response

def tob_users_dic_renditions(request, user, dictionary, sentence, count):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.get(dictionary_name=dictionary) # or the_dictionary_itself=
	users_dic.update_purchases()
	dics_sentence = users_dic.sentences.get(the_word_itself=word)
	

	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)
		rendition_form = RenditionForm()

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

	the_response = render(request, "tob_users_dic_word.html", {"loggedinanon": loggedinanon, "dics_word": dics_word, "users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	the_response.set_cookie('current', 'tob_users_dic_word_count')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	the_response.set_cookie('word', word)
	return the_response

def tob_users_dic_analyses(request, user, dictionary, count):
	user_themself = User.objects.get(username=user)
	user_anon = Anon.objects.get(username=user_themself)
	users_dic = user_anon.dictionaries.get(dictionary_name=dictionary) # or the_dictionary_itself=
	users_dic.update_purchases()
	dics_word = users_dic.words.get(the_word_itself=word)
	
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

	the_response = render(request, "tob_users_dic_word.html", {"loggedinanon": loggedinanon, "dics_word": dics_word, "users_dic": users_dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	the_response.set_cookie('current', 'tob_users_dic_word_count')
	the_response.set_cookie('viewing_user', user)
	the_response.set_cookie('dictionary', dictionary)
	the_response.set_cookie('word', word)
	return the_response

def tob_dics(request):

	
	registerform = UserCreationForm()
	
		
	count = 0
	mcount = 0
	count100 = count + 25

	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)


		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		dic_sort_form = DicSortForm(request)
		word_sort_form = WordSortForm(request)
		
		dics = Dictionary.objects.all().order_by(loggedinanon.dictionary_sort_char)[:25]
		the_response = render(request, "tob_dics.html", {"word_sort_form": word_sort_form, "dic_sort_form": dic_sort_form, "loggedinanon": loggedinanon, "dics": dics, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
		the_response.set_cookie('current', 'tob_dics')
		return the_response
	dics = Dictionary.objects.all().order_by('-latest_change_date')[:25]
	the_response = render(request, "tob_dics.html", {"dics": dics, "registerform": registerform,  "loginform": loginform})
	the_response.set_cookie('current', 'tob_dics')
	return the_response

def tob_dics_count(request, count):

	
	registerform = UserCreationForm()
	
	count = int(count)
	if count > 25:
		mcount = count - 25
	else:
		mcount = 0
	count100 = count + 25
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		dic_sort_form = DicSortForm(request)
		word_sort_form = WordSortForm(request)
		if loggedinanon.dictionary_sort_char == "0":
			loggedinanon.dictionary_sort_char = "views"
			loggedinanon.save()
		dics = Dictionary.objects.order_by(loggedinanon.dictionary_sort_char)[count:count+25]
		the_response = render(request, "tob_dics.html", {"word_sort_form": word_sort_form, "dic_sort_form": dic_sort_form, "loggedinanon": loggedinanon, "dics": dics, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	dics = Dictionary.objects.order_by('-latest_change_date')[count:count+25]
	the_response = render(request, "tob_dics.html", {"dics": dics, "registerform": registerform,  "loginform": loginform})
	
	the_response.set_cookie('current', 'tob_dics_count')
	the_response.set_cookie('count', count)
	return the_response


def clickthrough(request):
	##3 charge
	form = ClichtroughForm(request.POST)
	sponsor_id = 1
	author = 'test'
	if form.is_valid():
		sponsor_id = form.sponsor_id
		author = form.author
	clicked_sponsor = Sponsor.objects.get(id=int(sponsor_id))
	parked_author = Author.objects.get(username=author)


	parked_anon = parked_author.to_anon()
	if author == request.user.username:
		return redirect(clicked_sponsor.url)

	if request.META.get('REMOTE_ADDR') not in clicked_sponsor.requested_agents.values_list('user_agent', flat=True):
		clicked_sponsor.requested_agents.add(Requested_Agent.objects.create(user_agent=request.META.get('REMOTE_ADDR')))
		if clicked_sponsor.price_limit > 0:
			if clicked_sponsor.allowable_expenditure > 0:
				clicked_sponsor.allowable_expenditure -= clicked_sponsor.price_limit
				clicked_anon = clicked_sponsor.author.to_anon()
				clicked_anon.false_wallet -= clicked_sponsor.price_limit
				if parked_anon in available_request_agents:
					parked_anon.false_wallet += clicked_sponsor.price_limit
					parked_anon.save()
				clicked_anon.save()
				clicked_sponsor.save()
			else:
				clicked_sponsor.delete()
	


	return redirect(clicked_sponsor.url)


def viewsponsor(request, sponsor_id):
	##3 charge
	clicked_sponsor = Sponsor.objects.get(id=int(sponsor_id))
	parked_author = Author.objects.get(username=request.user.username)

	parked_anon = parked_author.to_anon()
	
	if parked_anon.is_viewing:
		if clicked_sponsor.price_limit > 0:
			if clicked_sponsor.allowable_expenditure > 0:
				clicked_sponsor.allowable_expenditure -= clicked_sponsor.price_limit
				clicked_anon = clicked_sponsor.author.to_anon()
				clicked_anon.false_wallet -= clicked_sponsor.price_limit
				parked_anon.false_wallet += clicked_sponsor.price_limit
				parked_anon.save()
				clicked_anon.save()
				clicked_sponsor.save()
			else:
				clicked_sponsor.delete()
		parked_anon.is_viewing = False
		parked_anon.save()
	return HttpResponse("True")

# have a search bar for looking up pronunciations
# list top pronunciation by viewcount, votecount, 
def universal_pronunciations(request):
	
	registerform = UserCreationForm()
	
		
	
	pronunciations = IPA_pronunciation.objects.all()
	loginform = AuthenticationForm()

	if ('q' in request.GET) and request.GET['q'].strip():
		query_string = request.GET['q']
		pronunciations = IPA_pronunciation.objects.all().filter(the_IPA_itself__contains=query_string).filter(public=True)
	
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
	
		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()



		return render(request, "universal_pronunciations.html", {"loggedinanon": loggedinanon, "pronunciations": pronunciations, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	return render(request, "universal_pronunciations.html", {"pronunciations": pronunciations, "registerform": registerform,  "loginform": loginform})


def universal_pronunciation(request, pronunciation):
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	pronunciations = IPA_pronunciation.objects.filter(the_IPA_itself=pronunciation)
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		return render(request, "universal_pronunciation.html", {"loggedinanon": loggedinanon, "pronunciations": pronunciations, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	return render(request, "universal_pronunciation.html", {"pronunciations": pronunciations, "registerform": registerform,  "loginform": loginform})


def word_attributess(request):
	registerform = UserCreationForm()
	
		

	word_attributes = Attribute.objects.all().order_by('-latest_change_date')[0:100]
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		return render(request, "word_attributess.html", {"loggedinanon": loggedinanon, "word_attributes": word_attributes, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	return render(request, "word_attributess.html", {"word_attributes": word_attributes, "registerform": registerform,  "loginform": loginform})

def attribute(request, attribute_id):
	registerform = UserCreationForm()
	
		
	
	word_attribute = Attribute.objects.get(id=attribute_id)
	

	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		return render(request, "word_attributes.html", {"loggedinanon": loggedinanon, "dic": dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	return render(request, "word_attributes.html", {"dic": dic, "registerform": registerform,  "loginform": loginform, 
			})




def attributes(request, word_id):
	registerform = UserCreationForm()
	
		
	
	word_attributes = Word.objects.get(id=word_id).attributes.all()
	

	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		return render(request, "word_attributes.html", {"loggedinanon": loggedinanon, "dic": dic, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	return render(request, "word_attributes.html", {"dic": dic, "registerform": registerform,  "loginform": loginform, 
			})



def word_attributes(request, word):
	registerform = UserCreationForm()
	
		
	
	word_attributes = Attribute.objects.all().filter(the_attribute_itself=word)
	

	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		return render(request, "word_attributes.html", {"loggedinanon": loggedinanon, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	return render(request, "word_attributes.html", {"dic": dic, "registerform": registerform,  "loginform": loginform, 
			})


def valid_word(word, rack):
    available_letters = rack[:]
    blank_count = available_letters.count('_')
    # print available_letters, blank_count

    missed_counter = 0
    for letter in word:
        if letter in available_letters:         
            available_letters.remove(letter)
        else:
            missed_counter += 1

    # print word, missed_counter
    if missed_counter <= blank_count:
        return word
    return

'''
# Test program
rack = ['_', 'u', 'v', 'w', 'x', 'y', 'z']
lexicon = ['apple', 'whisky', 'yutz', 'xray', 'tux', 'xyzzy', 'zebra']

for word in lexicon: 
    valid_word(word, rack)
'''


def mutawords(request):
	registerform = UserCreationForm()
	print(timezone.now())
	with open(settings.MEDIA_ROOT + '/words.txt') as f:
		word_array = f.read().splitlines()
	print(timezone.now())
	loginform = AuthenticationForm()
	mutawords = Word.objects.all()

	query_string_1 = ''
	query_string_2 = ''
	query_string_3 = ''
	query_string_4 = ''
	query_string_5 = ''
	query_string_6 = ''
	query_string_7 = ''
	query_string_8 = ''
	query_string_9 = ''
	query_string_10 = ''
	query_string_11 = ''
	query_string_12 = ''
	query_string_13 = ''
	query_string_14 = ''

	querystring = []

	if ('q_1' in request.GET) and request.GET['q_1'].strip():
		query_string_1 = request.GET['q_1']
		querystring.append(query_string_1)
	if ('q_2' in request.GET) and request.GET['q_2'].strip():
		query_string_2 = request.GET['q_2']
		querystring.append(query_string_2)
	if ('q_3' in request.GET) and request.GET['q_3'].strip():
		query_string_3 = request.GET['q_3']
		querystring.append(query_string_3)
	if ('q_4' in request.GET) and request.GET['q_4'].strip():
		if not request.GET['q_4'] == 'null':
			query_string_4 = request.GET['q_4']
			querystring.append(query_string_4)
	if ('q_5' in request.GET) and request.GET['q_5'].strip():
		if not request.GET['q_5'] == 'null':
			query_string_5 = request.GET['q_5']
			querystring.append(query_string_5)
	if ('q_6' in request.GET) and request.GET['q_6'].strip():
		if not request.GET['q_6'] == 'null':
			query_string_6 = request.GET['q_6']
			querystring.append(query_string_6)
	if ('q_7' in request.GET) and request.GET['q_7'].strip():
		if not request.GET['q_7'] == 'null':
			query_string_7 = request.GET['q_7']
			querystring.append(query_string_7)
	if ('q_8' in request.GET) and request.GET['q_8'].strip():
		if not request.GET['q_8'] == 'null':
			query_string_8 = request.GET['q_8']
			querystring.append(query_string_8)
	if ('q_9' in request.GET) and request.GET['q_9'].strip():
		if not request.GET['q_9'] == 'null':
			query_string_9 = request.GET['q_9']
			querystring.append(query_string_9)
	if ('q_10' in request.GET) and request.GET['q_10'].strip():
		if not request.GET['q_10'] == 'null':
			query_string_10= request.GET['q_10']
			querystring.append(query_string_10)
	if ('q_11' in request.GET) and request.GET['q_11'].strip():
		if not request.GET['q_11'] == 'null':
			query_string_11 = request.GET['q_11']
			querystring.append(query_string_11)
	if ('q_12' in request.GET) and request.GET['q_12'].strip():
		if not request.GET['q_12'] == 'null':
			query_string_12 = request.GET['q_12']
			querystring.append(query_string_12)
	if ('q_13' in request.GET) and request.GET['q_13'].strip():
		if not request.GET['q_13'] == 'null':
			query_string_13 = request.GET['q_13']
			querystring.append(query_string_13)
	if ('q_14' in request.GET) and request.GET['q_14'].strip():
		if not request.GET['q_14'] == 'null':
			query_string_14 = request.GET['q_14']
			querystring.append(query_string_14)
	query_string = ''.join(querystring)
	possible_words = []
	print(len(word_array))

	for word in word_array:
		output = valid_word(word, querystring)
		if output is not None:
			possible_words.append(output)
	print(timezone.now())
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		#mutawords = Word.objects.all().filter(the_word_itself__search=querystring).order_by('-latest_change_date')[:100]

		return render(request, "mutawords.html", {"possible_words": possible_words, "loggedinanon": loggedinanon, "querystring": query_string, "mutawords": mutawords, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform, "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})


	#mutawords = Word.objects.filter(home_dictionary__public=True).filter(the_word_itself__search=querystring).order_by('-latest_change_date')[:100]

	return render(request, "mutawords.html", {"possible_words": possible_words, "querystring": query_string, "mutawords": mutawords, "registerform": registerform, "loginform": loginform, })


def mutaword(request, word):
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

	words = Word.objects.all().filter(the_word_itself=word, home_dictionary__public=True)

	return render(request, "mutaword.html", {"loggedinanon": loggedinanon, "words": words, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})


def tob_example(request, example_id):
	registerform = UserCreationForm()
	
		
	example = Example.objects.get(id=int(example_id))
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		return render(request, "tob_word.html", {"loggedinanon": loggedinanon, "example": example, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	return render(request, "tob_word.html", {"example": example,})

def tob_examples(request):
	registerform = UserCreationForm()
	
		
	examples = Example.objects.all().order_by('the_example_itself')
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		return render(request, "tob_word.html", {"loggedinanon": loggedinanon, "examples": examples, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	return render(request, "tob_word.html", {"examples": examples,})




def tob_pronunciations(request):
	registerform = UserCreationForm()
	
		
	prons = IPA_pronuncation.objects.all().order_by('the_IPA_itself')
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		return render(request, "tob_word.html", {"loggedinanon": loggedinanon, "prons": prons, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	return render(request, "tob_word.html", {"prons": prons,})


def tob_pronunciation(request, pron_id):
	registerform = UserCreationForm()
	
		
	pron = IPA_pronunciation.objects.get(id=int(pron_id))
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		return render(request, "tob_word.html", {"loggedinanon": loggedinanon, "pron": pron, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	return render(request, "tob_word.html", {"pron": pron,})




def tob_word(request, word_id):
	registerform = UserCreationForm()
	
		
	word = Word.objects.get(id=int(word_id))
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()
		

		words_pronunciations = IPA_pronunciationForm(prefix='wp')
		
		words_attributes = AttributeForm(prefix='wa')# do that, fuck formsets. NEVER USE. made by fucking retards.
		words_attributes_definition = DefinitionForm(prefix='ad')
		words_attributes_homonym = HomonymForm(prefix='ah')
		words_attributes_synonym = SynonymForm(prefix='as')
		words_attributes_antonym = AntonymForm(prefix='aa')
		
		words_similarities = SimulacrumForm(prefix='s')
		words_similarities_connexia = ConnexionForm(prefix='sc')
		
		words_translations = TranslationForm(prefix='t')
		words_examples = ExampleForm(prefix='e')
		words_stories = StoryForm(prefix='s')
		words_relations = RelationForm(prefix='r')

		words_sponsor = SponsorForm(prefix='ss')
		try:
			words_spaces = Space.objects.get(the_space_itself=word)
		except Space.DoesNotExist:
			words_spaces = None
		
	
	if request.method == 'POST':
		if request.user.is_authenticated:
			words_pronunciations = IPA_pronunciationForm(request.POST, prefix='wp')
			
			words_attributes = AttributeForm(request.POST, prefix='wa')# do that, fuck formsets. NEVER USE. made by fucking retards.
			words_attributes_definition = DefinitionForm(request.POST, prefix='ad')
			words_attributes_homonym = HomonymForm(request.POST, prefix='ah')
			words_attributes_synonym = SynonymForm(request.POST, prefix='as')
			words_attributes_antonym = AntonymForm(request.POST, prefix='aa')
			
			words_similarities = SimulacrumForm(request.POST, prefix='s')
			words_similarities_connexia = ConnexionForm(request.POST, prefix='sc')
			
			words_translations = TranslationForm(request.POST, prefix='t')
			words_examples = ExampleForm(request.POST, prefix='e')
			words_stories = StoryForm(request.POST, prefix='s')
			words_relations = RelationForm(request.POST, prefix='r')

			words_sponsor = SponsorForm(request.POST, prefix='ss')

			if words_attributes.is_valid():
				attribute_inst = Attribute.objects.create(the_attribute_itself=words_attributes.cleaned_data['the_attribute_itself'], author=loggedinauthor)
				word.attributes.add(attribute_inst)
				if words_attributes_definition.is_valid():
					definition_inst = Definition.objects.create(the_definition_itself=words_attributes_definition.cleaned_data['the_definition_itself'], author=loggedinauthor)
					attribute_inst.definitions.add(definition_inst)
				if words_attributes_homonym.is_valid():
					homonym_inst = Homonym.objects.create(the_homonym_itself=words_attributes_homonym.cleaned_data['the_homonym_itself'], author=loggedinauthor)
					attribute_inst.homonyms.add(homonym_inst)
				if words_attributes_synonym.is_valid():
					synonym_inst = Synonym.objects.create(the_synonym_itself=words_attributes_synonym.cleaned_data['the_synonym_itself'], author=loggedinauthor)
					attribute_inst.synonyms.add(synonym_inst)
				if words_attributes_antonym.is_valid():
					antonym_inst = Antonym.objects.create(the_antonym_itself=words_attributes_antonym.cleaned_data['the_antonym_itself'], author=loggedinauthor)
					attribute_inst.antonyms.add(antonym_inst)
				attribute_inst.save()
				word.latest_change_date = timezone.now()
				word.trickle()
				word.update_sponsors()
				word.save()

			if words_similarities.is_valid():
				if words_similarities_connexia.is_valid():
					similarity_inst = Simulacrum.objects.create(the_simulacrum_itself=words_similarities.cleaned_data['the_simulacrum_itself'], author=loggedinauthor)
					dics_word.similarities.add(similarity_inst)
					connexia_inst = Connexion.objects.create(the_connexion_itself=words_similarities_connexia.cleaned_data['the_connexion_itself'], author=loggedinauthor)
					similarity_inst.connexia.add(connexia_inst)
					similarity_inst.save()

			if words_translations.is_valid():
				translations_inst = Translation.objects.create(the_translation_before=words_translations.cleaned_data['the_translation_before'], the_translation_after=words_translations.cleaned_data['the_translation_after'], author=loggedinauthor)
				word.translations.add(translations_inst)

			if words_examples.is_valid():
				examples_inst = Example.objects.create(the_example_itself=words_examples.cleaned_data['the_example_itself'], author=loggedinauthor)
				word.examples.add(examples_inst)

			if words_stories.is_valid():
				stories_inst = Simulacrum.objects.create(the_story_itself=words_stories.cleaned_data['the_story_itself'], author=loggedinauthor)
				word.stories.add(stories_inst)

			if words_relations.is_valid():
				relations_inst = Relation.objects.create(the_relation_itself=words_relations.cleaned_data['the_relation_itself'], author=loggedinauthor)
				word.relations.add(relations_inst)

			if words_sponsor.is_valid():
				sponsor_inst = Sponsor.objects.create(the_sponsorship_phrase=words_sponsor.cleaned_data['the_sponsorship_phrase'], author=loggedinauthor, img=words_sponsor.cleaned_data['img'], url2=words_sponsor.cleaned_data['url2'], price_limit=words_sponsor.cleaned_data['price_limit'])
				word.sponsors.add(sponsor_inst)
				if sponsor_inst.price_limit > dics_word.price_limit:
					word.price_limit = sponsor_inst.price_limit

			
			word.latest_change_date = timezone.now()
			word.save()

		words_examples = ExampleForm(prefix='e')
		words_stories = StoryForm(prefix='s')
		words_relations = RelationForm(prefix='r')

		words_sponsor = SponsorForm(prefix='ss')

		story_id = 0
		sponsor_id = 0

		return render(request, "tob_word.html", {"story_id": story_id, "sponsor_id": sponsor_id, "loggedinanon": loggedinanon, "word": word, "words_pronunciations": words_pronunciations, "words_attributes": words_attributes, "words_attributes_definition": words_attributes_definition, "words_attributes_antonym": words_attributes_antonym, "words_attributes_synonym": words_attributes_synonym, "words_attributes_homonym": words_attributes_homonym, "words_similarities": words_similarities, "words_similarities_connexia": words_similarities_connexia, 
			"words_translations": words_translations, "words_sponsor": words_sponsor, "words_examples": words_examples, "words_stories": words_stories, "words_relations": words_relations, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform,  "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	return render(request, "tob_word.html", {"word": word, "story_id": 0,})


def tob_pronunciations(request, word_id):
	registerform = UserCreationForm()
	
		
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

	word = Word.objects.get(id=int(word_id))


	return redirect('Bable:tob_users_dic_word_count', word.home_dictionary.author, word.home_dictionary.the_dictionary_itself, word.the_word_itself, 0)



@login_required
def tob_loan(request, loan_id, self_dic_word, dictionary_source):
	dictionary_source = int(dictionary_source)
	loan = 0
	loan_form = 0
	if dictionary_source:
		dictionary_source = Dictionary_Source.objects.get(id=dictionary_source)
	loan_id = int(loan_id)
	if self_dic_word == "word":
		loan = Word_Loan.objects.get(id=loan_id)
		loan_form = WordLoanForm(request, dictionary_source, instance=loan)
	if self_dic_word == "self":
		loan = Loan.objects.get(id=loan_id)
		loan_form = LoanForm(request, instance=loan)
	if self_dic_word == "dic":
		loan = Dictionary_Loan.objects.get(id=loan_id)
		loan_form = DictionaryLoanForm(request, instance=loan)

	registerform = UserCreationForm()
	loginform = AuthenticationForm()

	loggedinuser = User.objects.get(username=request.user.username)
	loggedinanon = Anon.objects.get(username=loggedinuser)

	dic_form = DictionaryForm()
	space_form = SpaceForm(request)
	post_form = PostForm(request)
	task_form = TaskForm()
	word_form = WordForm(request)

	apply_votestyle_form = ApplyVotestyleForm(request)
	create_votes_form = CreateVotesForm(request)
	exclude_votes_form = ExcludeVotesForm(request)
	apply_dic_form = ApplyDictionaryForm(request)
	exclude_dic_form = ExcludeDictionaryAuthorForm()
	
	return render(request, "tob_loan.html", {"loan": loan, "loan_form": loan_form, "registerform": registerform,
		"loginform": loginform, "loggedinanon": loggedinanon, "loggedinuser": loggedinuser, "dic_form": dic_form,
		"space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "apply_votestyle_form": apply_votestyle_form,
		"apply_dic_form": apply_dic_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form,
		"exclude_dic_form": exclude_dic_form})

def tob_create_loan(request, self_dic_word):
	dictionary_source = 0
	if self_dic_word == "self":
		form = LoanForm(request.POST)
		if form.is_valid():
			form.save()
			for space in form.spaces.all():
				space.space_wallet += form.amount_total//form.spaces.count()
	if self_dic_word == "dic":
		form = DictionaryLoanForm(request.POST)
		if form.is_valid():
			form.save()
			for dictionary in form.dictionaries.all():
				dictionary.dictionary_wallet += form.amount_total//form.dictionaries.count()
	if self_dic_word == "word":
		form = WordLoanForm(request.POST)
		dictionary_source = form.dictionary_source.id
		if form.is_valid():
			form.save()
			for word in form.words.all():
				word.word_wallet += form.amount_total//form.words.count()

	return redirect('Bable:tob_loan', form.instance.id, self_dic_word, dictionary_source)

import requests
import ipfshttpclient
from base64 import b64encode

@login_required
def upload_file(request):
	loggedinuser = User.objects.get(username=request.user.username)
	loggedinanon = Anon.objects.get(username=loggedinuser)
	if request.method == 'POST':
		file_form = FileForm(request.POST, request.FILES)
		if file_form.is_valid() and file_form.cleaned_data['file']:
			#client = ipfshttpclient.connect()
			#datahash = client.addfile(request.FILES['file'].read())
			#print(datahash)
			userAndPass = b64encode(b"ff371d15-c2bc-4930-83c4-ce5c9c926dcc:phbzspnkD3gNP3CHkIBolc4MkziwSS8EjWY26PujQlXRDR0y9J").decode("ascii")
			headers = { 'Authorization' : 'Basic %s' %  userAndPass, "Content-Type": "application/octet-stream" }

			resp = requests.post('https://runfission.com/ipfs/', headers=headers, files={ "files": request.FILES['file'].read()})
			print(resp)
			data = resp.read()
			new_file = File.objects.create(url='https://runfission.com/ipfs/'+data['Hash']+'?filename='+data['Name'], public=file_form.cleaned_data['public'])
			if new_file.public:
				loggedinanon.public_files.add(new_file)
			else:
				loggedinanon.all_files.add(new_file)
			loggedinanon.save()
		else: return HttpResponse(file_form.errors)

	return redirect('Bable:tob_users_files', request.user.username)


@login_required
def tob_users_files(request, user):
	viewing_user = User.objects.get(username=user)
	viewing_anon = Anon.objects.get(username=viewing_user)
	loggedinuser = User.objects.get(username=request.user.username)
	loggedinanon = Anon.objects.get(username=loggedinuser)
	dic_form = DictionaryForm()
	space_form = SpaceForm(request)
	post_form = PostForm(request)
	task_form = TaskForm()
	word_form = WordForm(request)

	apply_votestyle_form = ApplyVotestyleForm(request)
	create_votes_form = CreateVotesForm(request)
	exclude_votes_form = ExcludeVotesForm(request)
	apply_dic_form = ApplyDictionaryForm(request)
	exclude_dic_form = ExcludeDictionaryAuthorForm()

	file_form = FileForm()
	all_files = loggedinanon.all_files.all()
	public_files = loggedinanon.public_files.all()
	return render(request, "tob_users_files.html", { "file_form": file_form, "loggedinanon": loggedinanon, "viewing_anon": viewing_anon, "dic_form": dic_form, "space_form": space_form, "apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form, "post_form": post_form, "task_form": task_form, "word_form": word_form})



import math
from matplotlib import pyplot as plt
import matplotlib
from matplotlib_venn import venn2, venn3
import numpy as np
from matplotlib.figure import Figure

import plotly

import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3

import plotly as py
from plotly.offline import iplot
import plotly.graph_objs as go
import plotly.io as pio
pio.renderers.default = 'iframe'

import scipy


def venn_to_plotly(L_sets,L_labels=None,title=None):
    
    #get number of sets
    n_sets = len(L_sets)
    
    #choose and create matplotlib venn diagramm
    if n_sets == 2:
        if L_labels and len(L_labels) == n_sets:
            v = venn2(L_sets,L_labels)
        else:
            v = venn2(L_sets)
    elif n_sets == 3:
        if L_labels and len(L_labels) == n_sets:
            v = venn3(L_sets,L_labels)
        else:
            v = venn3(L_sets)
    #supress output of venn diagramm
    plt.close()
    
    #Create empty lists to hold shapes and annotations
    L_shapes = []
    L_annotation = []
    
    #Define color list for sets
    #check for other colors: https://css-tricks.com/snippets/css/named-colors-and-hex-equivalents/
    L_color = ['FireBrick','DodgerBlue','DimGrey'] 
    
    #Create empty list to make hold of min and max values of set shapes
    L_x_max = []
    L_y_max = []
    L_x_min = []
    L_y_min = []
    
    for i in range(0,n_sets):
        
        #create circle shape for current set
        
        shape = go.layout.Shape(
                type="circle",
                xref="x",
                yref="y",
                x0= v.centers[i][0] - v.radii[i],
                y0=v.centers[i][1] - v.radii[i],
                x1= v.centers[i][0] + v.radii[i],
                y1= v.centers[i][1] + v.radii[i],
                fillcolor=L_color[i],
                line_color=L_color[i],
                opacity = 0.75
            )
        
        L_shapes.append(shape)
        
        #create set label for current set
        for text in v.set_labels:
            text.set_fontsize(15)
        for x in range(len(v.subset_labels)):
            if v.subset_labels[x] is not None:
                v.subset_labels[x].set_fontsize(15)
        anno_set_label = go.layout.Annotation(
                xref="x",
                yref="y",
                x = v.set_labels[i].get_position()[0],
                y = v.set_labels[i].get_position()[1],
                text = v.set_labels[i].get_text(),
                showarrow=False
        )
        
        L_annotation.append(anno_set_label)
        
        #get min and max values of current set shape
        L_x_max.append(v.centers[i][0] + v.radii[i])
        L_x_min.append(v.centers[i][0] - v.radii[i])
        L_y_max.append(v.centers[i][1] + v.radii[i])
        L_y_min.append(v.centers[i][1] - v.radii[i])
    
    #determine number of subsets
    n_subsets = sum([scipy.special.binom(n_sets,i+1) for i in range(0,n_sets)])
    
    for i in range(0,int(n_subsets)):
        
        #create subset label (number of common elements for current subset
        anno_subset_label = go.layout.Annotation(
                xref="x",
                yref="y",
                x = v.subset_labels[i].get_position()[0],
                y = v.subset_labels[i].get_position()[1],
                text = v.subset_labels[i].get_text(),
                showarrow=False
        )
        
        L_annotation.append(anno_subset_label)
        
        
    #define off_set for the figure range    
    off_set = 0.2
    
    #get min and max for x and y dimension to set the figure range
    x_max = max(L_x_max) + off_set
    x_min = min(L_x_min) - off_set
    y_max = max(L_y_max) + off_set
    y_min = min(L_y_min) - off_set
    
    #create plotly figure
    p_fig = go.Figure()
    
    #set xaxes range and hide ticks and ticklabels
    p_fig.update_xaxes(
        range=[x_min, x_max], 
        showticklabels=False, 
        ticklen=0
    )
    
    #set yaxes range and hide ticks and ticklabels
    p_fig.update_yaxes(
        range=[y_min, y_max], 
        scaleanchor="x", 
        scaleratio=1, 
        showticklabels=False, 
        ticklen=0
    )
    
    #set figure properties and add shapes and annotations
    p_fig.update_layout(
        plot_bgcolor='white', 
        margin = dict(b = 0, l = 10, pad = 0, r = 10, t = 40),
        width=800, 
        height=400,
        shapes= L_shapes, 
        annotations = L_annotation,
        title = dict(text = title, x=0.5, xanchor = 'center')
    )

    return p_fig



'''
def complementary_scholar(request):
	registerform = UserCreationForm()
	#
	#	
	#a = set(['a', 'b', 'c']) 
	#b = set(['c', 'd', 'e'])
	#c = set(['e', 'f', 'a'])
	#s = [a, b, c]

	# Plot it
	#matplotlib.pyplot.switch_backend('Agg')
	#h = venn3(s, ('A', 'B', 'C'))

	#h = venn_to_plotly(s)
	
	#graph_div = plotly.offline.plot(h, auto_open = False, output_type="div")
	
	#s = [a, b]
	#h = venn_to_plotly(s)

	search_1 = 0
	search_2 = 0
	#search_3 = 0
	search_1__2 = 0
	search_1_2 = 0
	#search_1_3 = 0
	#search_2__3 = 0
	#search_2_3 = 0
	#search_1__2__3 = 0
	#search_1_2_3 = 0

	#graph_div_2 = plotly.offline.plot(h, auto_open = False, output_type="div")
	
	if ('q_1' in request.GET) and request.GET['q_1'].strip():
		query_string_1 = request.GET['q_1']
		search_1 = Post.objects.filter(title__contains=query_string_1).filter(public=True).order_by('-latest_change_date')[0:10]
		

	if ('q_2' in request.GET) and request.GET['q_2'].strip():
		query_string_2 = request.GET['q_2']
		search_2 = Post.objects.filter(title__contains=query_string_2).filter(public=True).order_by('-latest_change_date')[0:10]
		
	
	if ('q_3' in request.GET) and request.GET['q_3'].strip():
		query_string_3 = request.GET['q_3']
		search_3 = Post.objects.filter(title__contains=query_string_3).filter(public=True).order_by('-latest_change_date')[0:100]
	
	if ('q_1' in request.GET) and request.GET['q_1'].strip() and ('q_2' in request.GET) and request.GET['q_2'].strip():
		query_string_1 = request.GET['q_1']
		query_string_2 = request.GET['q_2']
		search_1__2 = Post.objects.filter(title__contains=query_string_1+' '+query_string_2).filter(public=True).order_by('-latest_change_date')[0:10]
		search_1_2 = Post.objects.filter(title__contains=query_string_1).filter(title__contains=query_string_2).filter(public=True).order_by('-latest_change_date')[0:10]
	
	if ('q_1' in request.GET) and request.GET['q_1'].strip() and ('q_3' in request.GET) and request.GET['q_3'].strip():
		query_string_1 = request.GET['q_1']
		query_string_3 = request.GET['q_3']
		search_1_3 = Post.objects.filter(title__contains=query_string_1).filter(title__contains=query_string_3).filter(public=True).order_by('-latest_change_date')[0:100]
	
	if ('q_2' in request.GET) and request.GET['q_2'].strip() and ('q_3' in request.GET) and request.GET['q_3'].strip():
		query_string_2 = request.GET['q_2']
		query_string_3 = request.GET['q_3']
		search_2__3 = Post.objects.filter(title__contains=query_string_2 + ' ' + query_string_2).filter(public=True).order_by('-latest_change_date')[0:100]
		search_2_3 = Post.objects.filter(title__contains=query_string_2).filter(title__contains=query_string_3).filter(public=True).order_by('-latest_change_date')[0:100]
	
	if ('q_2' in request.GET) and request.GET['q_2'].strip() and ('q_3' in request.GET) and request.GET['q_3'].strip():
		query_string_1 = request.GET['q_1']
		query_string_2 = request.GET['q_2']
		query_string_3 = request.GET['q_3']
		search_1 = Post.objects.filter(title__contains=query_string_1).filter(public=True).order_by('-latest_change_date')[0:100]
		search_2 = Post.objects.filter(title__contains=query_string_2).filter(public=True).order_by('-latest_change_date')[0:100]
		search_3 = Post.objects.filter(title__contains=query_string_3).filter(public=True).order_by('-latest_change_date')[0:100]
		
		if search_1.count() > 3 and search_2.count() > 3 and search_3.count() > 3:
			list1 = search_1.values_list('id', flat=True)
			list2 = search_2.values_list('id', flat=True)
			list3 = search_3.values_list('id', flat=True)
			subset1 = list(set(list1).intersection(list2))
			subset2 = list(set(list1).intersection(list3))
			subset3 = list(set(list2).intersection(list3))

			if len(subset1) and len(subset2) and len(subset3):

				a = set(list1) 
				b = set(list2)
				c = set(list3)
				s = [a, b, c]

				# Plot it
				matplotlib.pyplot.switch_backend('Agg')
				h = venn3(s, ('A', 'B', 'C'))

				h = venn_to_plotly(s)
				
				graph_div = plotly.offline.plot(h, auto_open = False, output_type="div")

				#h = venn2(s, ('A', 'B', 'C'))
		if search_1__2.count() > 3 and search_2__3.count() > 3:
			a = set(search_1__2.values_list('id', flat=True)) 
			b = set(search_2__3.values_list('id', flat=True))
			s = [a, b]

			h = venn_to_plotly(s)
			
			graph_div_2 = plotly.offline.plot(h, auto_open = False, output_type="div")
		search_1__2__3 = Post.objects.filter(title__contains=query_string_1+' '+query_string_2+' '+query_string_3).filter(public=True).order_by('-latest_change_date')[0:100]
		search_1_2_3 = Post.objects.filter(title__contains=query_string_1).filter(title__contains=query_string_2).filter(title__contains=query_string_3).filter(public=True).order_by('-latest_change_date')[0:100]
	


	
	
	loginform = AuthenticationForm()
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		dic_form = DictionaryForm()
		space_form = SpaceForm(request)
		post_form = PostForm(request)
		task_form = TaskForm()
		word_form = WordForm(request)

		apply_votestyle_form = ApplyVotestyleForm(request)
		create_votes_form = CreateVotesForm(request)
		exclude_votes_form = ExcludeVotesForm(request)
		apply_dic_form = ApplyDictionaryForm(request)
		exclude_dic_form = ExcludeDictionaryAuthorForm()

		return render(request, "complementary_scholar.html", {"loggedinanon": loggedinanon, "search_1": search_1, "search_2": search_2, "search_1_2": search_1_2, "search_1__2": search_1__2, "dic_form": dic_form, "space_form": space_form, "post_form": post_form, "task_form": task_form, "word_form": word_form, "registerform": registerform, "loginform": loginform, 
			"apply_votestyle_form": apply_votestyle_form, "create_votes_form": create_votes_form, "exclude_votes_form": exclude_votes_form, "apply_dic_form": apply_dic_form, "exclude_dic_form": exclude_dic_form})
	return render(request, "complementary_scholar.html", {"search_1": search_1, "search_2": search_2, "search_1_2": search_1_2, "search_1__2": search_1__2, "registerform": registerform, "loginform": loginform, 
			})
'''


@login_required
def tob_save_com(request, user, com):
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		author = Author.objects.get(username=user)
		saving_com = Comment.objects.get(id=int(com))

		if saving_com in loggedinanon.saved_comments.all():
			loggedinanon.saved_comments.remove(saving_com)
		else:
			loggedinanon.saved_comments.add(saving_com)
	return base_redirect(request, 0)

@login_required
def tob_save_votestyle(request, user, votestyleid):
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)

		author = Author.objects.get(username=user)
		saving_votestyle = Votes.objects.get(id=int(votestyleid))

		if saving_votestyle in loggedinanon.saved_votestyles.all():
			loggedinanon.saved_votestyles.remove(saving_votestyle)
		else:
			loggedinanon.saved_votestyles.add(saving_votestyle)
	return base_redirect(request, 0)

@login_required
def tob_buy_space(request, user, space):
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		author = Author.objects.get(username=user)
		saving_space = Space.objects.get(author=author, the_space_itself__the_word_itself=space)

		if saving_space in loggedinanon.purchased_spaces.all():
			loggedinanon.purchased_spaces.remove(saving_space)
			saving_space.approved_voters.remove(loggedinauthor)
		else:
			if saving_space.for_sale:
				if saving_space.entry_fee + saving_space.continuation_fee < loggedinanon.false_wallet:
					loggedinanon.false_wallet = loggedinanon.false_wallet - saving_space.entry_fee - saving_space.continuation_fee
					saving_anon = saving_space.author.to_anon()
					saving_anon.false_wallet += saving_space.entry_fee + saving_space.continuation_fee
					saving_space.approved_voters.add(loggedinauthor)
					loggedinanon.purchased_spaces.add(saving_space)
	return base_redirect(request, 0)

@login_required
def submit_buy_space_form(request, space_id):
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		saving_space = Space.objects.get(id=space_id)
		if request.method == "POST":
			if saving_space.for_sale:
				if saving_space.entry_fee + saving_space.continuation_fee < loggedinanon.false_wallet:
					loggedinanon.false_wallet = loggedinanon.false_wallet - saving_space.entry_fee - saving_space.continuation_fee
					saving_anon = saving_space.author.to_anon()
					saving_anon.false_wallet += saving_space.entry_fee + saving_space.continuation_fee
					if not loggedinauthor in saving_space.approved_voters.all():
						saving_space.approved_voters.add(loggedinauthor)
					loggedinuser = User.objects.get(username=request.user.username)
					loggedinanon = Anon.objects.get(username=loggedinuser)
		
					if not saving_space in loggedinanon.purchased_spaces.all():
						loggedinanon.purchased_spaces.add(saving_space)
	return base_redirect(request, 0)

@login_required
def tob_remove_space(request, user, space):
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		author = Author.objects.get(username=user)
		saving_space = Space.objects.get(author=author, the_space_itself__the_word_itself=space)

		if saving_space in loggedinanon.purchased_spaces.all():
			loggedinanon.purchased_spaces.remove(saving_space)
			saving_space.approved_voters.remove(loggedinauthor)
	return base_redirect(request, 0)


@login_required
def tob_save_space(request, user, space):
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		author = Author.objects.get(username=user)
		saving_space = Space.objects.get(author=author, the_space_itself__the_word_itself=space)

		if saving_space in loggedinanon.purchased_spaces.all() or saving_space in loggedinanon.spaces.all():
			loggedinanon.saved_spaces.add(saving_space)
	return base_redirect(request, 0)


@login_required
def tob_unsave_space(request, user, space):
	if request.user.is_authenticated:
		loggedinuser = User.objects.get(username=request.user.username)
		loggedinanon = Anon.objects.get(username=loggedinuser)
		loggedinauthor = Author.objects.get(username=request.user.username)

		author = Author.objects.get(username=user)
		saving_space = Space.objects.get(author=author, the_space_itself__the_word_itself=space)

		if saving_space in loggedinanon.saved_spaces.all():
			loggedinanon.purchased_spaces.remove(saving_space)
			saving_space.approved_voters.remove(loggedinauthor)
		return base_redirect(request, 0)

