# Copyright Aden Handasyde 2019

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User, UserManager, AbstractBaseUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import os
from django.urls import reverse
from django import forms
from mptt.models import MPTTModel, TreeForeignKey
from webpreview import web_preview

from django.conf import settings

import PIL.Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

from datetime import timedelta
from random import choice
# from resizeimage import resizeimage

#from videofield.models import VideoField
# Create your models here.
def get_image_path(instance, filename):
    return settings.MEDIA_ROOT + str(instance.id) + '{}'.format(filename)
#Repeat of Words with OVERTOPVISION

# '/media/' for heroku
# settings.MEDIA_ROOT for local
class File(models.Model):
	file = models.FileField(upload_to='files', null=True)
	url2 = models.URLField(max_length=2000)
	filename = models.CharField(max_length=200, default='')
	public = models.BooleanField(default=False)
	creation_date = models.DateTimeField(default=timezone.now)

# Many to many fields create a A = .m2m(B), into a A_B hidden table. ie. it's backwards compatable with .m2m(B, through='AB')

class Notification(models.Model):
	text = models.CharField(max_length=200)
	link = models.URLField(max_length=2000, default='')
	username = models.CharField(max_length=150, default='', unique=True)
	sent = models.BooleanField(default=False)
	new = models.BooleanField(default=True)
	creation_date = models.DateTimeField(default=timezone.now)
	read_date = models.DateTimeField(default=timezone.now)
	click_date = models.DateTimeField(default=timezone.now)


# trying to save every change within the new saves, but not need a mirage of every other class.
class ChangeDate(models.Model):
	def __init__(self, charfield=None, textfield=None, **kwargs):
		if charfield:
			self.charfield = models.CharField(max_length=200, default='', unique=True)
		if textfield:
			self.textfield = models.TextField(max_length=1000, default='')
	each = models.DateTimeField(default=timezone.now)

class Requested_Agent(models.Model):
	user_agent = models.CharField(max_length=200, default='')


class Invoice(models.Model):
	amount = models.IntegerField(default=0)
	price_id = models.CharField(max_length=200, default='')
	item_name = models.CharField(max_length=200, default='')
	author = models.CharField(max_length=200, default='')
	success = models.BooleanField(default=False)
	submit_date = models.DateTimeField(default=timezone.now)

class Author(models.Model):
	username = models.CharField(max_length=150, default='', unique=True)
	spent_invoices = models.ManyToManyField(Invoice, default=None, related_name='spentinvoices')
	earnt_invoices = models.ManyToManyField(Invoice, default=None, related_name='earntinvoices')

	def to_anon(self):
		if Anon.objects.filter(username__username=self.username[0:149]).count():
			if not User.objects.filter(username=self.username[0:149]).count():
				user = User.objects.create(username=self.username[0:149], password="Password-2")
			else:
				user = User.objects.get(username=self.username[0:149])
			anon = Anon.objects.get(username=user)
			author, created = Author.objects.get_or_create(username=self.username[0:149])
			anons_posts = Post.objects.filter(author=author)
			for post in anons_posts:
				if post not in anon.posts.all():
					anon.posts.add(post)
			return anon
		else:
			if not User.objects.filter(username=self.username[0:149]).count():
				user = User.objects.create(username=self.username[0:149], password="Password-2")
			else:
				user = User.objects.get(username=self.username[0:149])
			
			if Anon.objects.filter(username=user).count():
				anon = Anon.objects.get(username=user)
				anons_posts = Post.objects.filter(author=Author.objects.get(username=self.username[0:149]))
				for post in anons_posts:
					if post not in anon.posts.all():
						anon.posts.add(post)
				return anon
			else:
				anon = Anon.objects.create(username=user)
				anons_posts = Post.objects.all().filter(author=Author.objects.get(username=self.username[0:149]))
				for post in anons_posts:
					if post not in anon.posts.all():
						anon.posts.add(post)
				return anon


class Word_Source(models.Model):
	the_word_itself = models.CharField(max_length=200, default='')
	home_dictionary = models.CharField(max_length=200, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)

	word_id = models.CharField(max_length=256, default='')

	def to_full(self):
		return Word.objects.get(author=self.author, home_dictionary__the_dictionary_itself=self.home_dictionary, the_word_itself=self.the_word_itself)


class Searches(models.Model):
	the_search_itself = models.CharField(max_length=200, default='')
	creation_date = models.DateTimeField(default=timezone.now)


class Dictionary_Source(models.Model):
	the_dictionary_itself = models.CharField(max_length=200, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	words = models.ManyToManyField(Word_Source, default=None)
	purchasers = models.ManyToManyField(Author, default=None, related_name='dspurchasers')
	public = models.BooleanField(default=False)

	dictionary_id = models.CharField(max_length=256, default='')


	def __unicode__(self):
   		return self.the_dictionary_itself
	
	def to_full(self):
		return Dictionary.objects.get(author=self.author, the_dictionary_itself=self.the_dictionary_itself)

	def get_purchasers(self):
		self.to_full.get_allowed
		for purchaser in self.to_full.allowed_to_view_authors.all():
			self.purchasers.add(purchaser)


class Votes_Source(models.Model):
	the_vote_style = models.ManyToManyField(Word_Source, related_name='votestyle', default=None)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.IntegerField(default=0)
	the_vote_name = models.ForeignKey(Word_Source, on_delete=models.CASCADE, related_name='votename', default=None)

	def to_full(self):
		return Votes.objects.get(author=self.author, the_vote_name=self.the_vote_name__the_word_itself)

class Comment_Source(MPTTModel):
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	dictionaries = models.ManyToManyField(Dictionary_Source, default=None)
	sum_dictionaries = models.IntegerField(default=0)
	words = models.ManyToManyField(Word_Source, default=None)
	sum_words = models.IntegerField(default=0)
	body = models.TextField(max_length=144000, default='')
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	original = models.CharField(max_length=200, default='')
	parent = TreeForeignKey('self', on_delete=models.CASCADE, default=None, null=True, blank=True, related_name='children', db_index=True)

	def __str__(self):
		return self.body

	def __unicode__(self):
   		return unicode(self.body) or u''

	def children(self):
		return Comment_Sources.objects.filter(parent=self)

	@property
	def is_parent(self):
		if self.parent is not None:
			return False
		return True

	def to_original(self):
		return Comment.objects.get(id=self.original)

	class MPTTMeta:
		order_insertion_by = ['votes_count']



class SpaceSource(models.Model):
	the_space_itself = models.ForeignKey(Word_Source, on_delete=models.CASCADE, default=None)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, related_name='space_source_author')
	dictionary = models.ForeignKey(Dictionary_Source, on_delete=models.CASCADE, default=None)
	allowed_to_view_authors = models.ManyToManyField(Author, default=None, related_name='space_source_allowed')
	votessource = models.ManyToManyField(Votes_Source, default=None)

	def to_full(self):
		return Space.objects.get(author=self.author, the_space_itself=self.the_space_itself.to_full())




class Sponsor(models.Model):
	the_sponsorship_phrase = models.CharField(max_length=200, default='')
	latest_change_date = models.DateTimeField(default=timezone.now)
	img = models.URLField(max_length=2000)
	url2 = models.URLField(max_length=2000)
	clicks = models.IntegerField(default=0)
	payperview = models.BooleanField(default=False)
	price_limit = models.IntegerField(default=0)
	allowable_expenditure = models.IntegerField(default=0)
	trickles = models.IntegerField(default=0)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="spo_has_voted", default=None)
	views = models.IntegerField(default=0)
	requested_agents = models.ManyToManyField(Requested_Agent, default=None)

	
class Advertising(models.Model):
	email = models.EmailField(max_length=144, default='', null=True)
	allowable_expenditure = models.IntegerField(default=0)
	price_limit = models.IntegerField(default=0)
	words_to_sponsor = models.CharField(max_length=2000, default='')
	the_sponsorship_phrase = models.CharField(max_length=200, default='')
	latest_change_date = models.DateTimeField(default=timezone.now)
	img = models.URLField(max_length=2000)
	url2 = models.URLField(max_length=2000)
	clicks = models.IntegerField(default=0)
	payperview = models.BooleanField(default=False)
	trickles = models.IntegerField(default=0)
	name = models.CharField(max_length=2000, default='')
	views = models.IntegerField(default=0)
	requested_agents = models.ManyToManyField(Requested_Agent, default=None)


class Definition(models.Model):
	the_definition_itself = models.TextField(max_length=1000, default='')
	latest_change_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="def_has_voted", default=None)
	views = models.IntegerField(default=0)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="def_com", default=None)
	sponsors = models.ManyToManyField(Sponsor, default=None)

#Repeat of Words with OVERTOPVISION-onedictionary_to_rule_them_all
class Translation(models.Model):
	the_translation_before = models.TextField(max_length=1000, default='')
	the_translation_after = models.TextField(max_length=1000, default='')
	latest_change_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.ManyToManyField(Votes_Source, default=None)

	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="tra_has_voted", default=None)
	views = models.IntegerField(default=0)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="tra_com", default=None)

#Repeat of Words with OVERTOPVISION
class Connexion(models.Model):
	the_connexion_itself = models.CharField(max_length=200, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, null=True)
	latest_change_date = models.DateTimeField(default=timezone.now)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="con_has_voted", default=None)
	views = models.IntegerField(default=0)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="con_com", default=None)

# ie. Metaphor, Spelling
class Simulacrum(models.Model):
	the_simulacrum_itself = models.CharField(max_length=200, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	connexia = models.ManyToManyField(Connexion, default=None)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="sim_com", default=None)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="sim_has_voted", default=None)
	views = models.IntegerField(default=0)

class Synonym(models.Model):
	the_synonym_itself = models.CharField(max_length=200, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="syn_com", default=None)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="syn_has_voted", default=None)
	views = models.IntegerField(default=0)

class Antonym(models.Model):
	the_antonym_itself = models.CharField(max_length=200, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="ant_com", default=None)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="ant_has_voted", default=None)
	views = models.IntegerField(default=0)

class Homonym(models.Model):
	the_homonym_itself = models.CharField(max_length=200, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="hom_com", default=None)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="hom_has_voted", default=None)
	views = models.IntegerField(default=0)

class Attribute(models.Model):
	the_attribute_itself = models.CharField(max_length=200, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, null=True)
	views = models.IntegerField(default=0)
	latest_change_date = models.DateTimeField(default=timezone.now)
	creation_date = models.DateTimeField(default=timezone.now)
	definitions = models.ManyToManyField(Definition, default=None)
	definition_count = models.IntegerField(default=0)
	synonyms = models.ManyToManyField(Synonym, default=None)
	synonym_count = models.IntegerField(default=0)
	antonyms = models.ManyToManyField(Antonym, default=None)
	antonym_count = models.IntegerField(default=0)
	homonyms = models.ManyToManyField(Homonym, default=None)
	homonym_count = models.IntegerField(default=0)
	
ATTRIBUTE_SORT_CHOICES_CHAR = (
	("the_attribute_itself", "Alphabetical"),
	("-the_attribute_itself", "Anti Alphabetical"),
	("-views", "Most Viewed"),
	("views", "Least Viewed"),
	("-defintion_count", "Most Definitions"),
	("defintion_count", "Least Definitions"),
	("-synonym_count", "Most Synonyms"),
	("synonym_count", "Least Synonyms"),
	("-antonym_count", "Most Antonyms"),
	("antonym_count", "Least Antonyms"),
	("-homonym_count", "Most Homonyms"),
	("homonym_count", "Least Homonyms"),
	("-latest_change_date", "Most Recently Changed"),
	("latest_change_date", "Least Recently Changed"),
	("-creation_date", "Most Recently Created"),
	("creation_date", "Least Recently Created"),
)


# Change it so that the IPA characters is user definable, oh, they already are.
class IPA_pronunciation(models.Model):
	the_IPA_itself = models.CharField(max_length=200, default='')
	homophones = models.TextField(max_length=1000, default='')
	latest_change_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="pro_has_voted", default=None)
	views = models.IntegerField(default=0)

class Example(models.Model):
	the_example_itself = models.TextField(max_length=1000, default='')
	words = models.ManyToManyField(Word_Source, default=None)
	dictionaries = models.ManyToManyField(Dictionary_Source, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="exa_com", default=None)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, null=True)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="exa_has_voted", default=None)
	views = models.IntegerField(default=0)

	

	def max_sponsor(self):
		max_price = 0
		pks = Sponsor.objects.values_list('pk', flat=True)
		random_pk = choice(pks)
		random_obj = Sponsor.objects.get(pk=random_pk)
		max_sponsor = random_obj
		for word in self.words.all():
			for sponsor in word.to_full().sponsors.all().filter(payperview=False):
				if sponsor.allowable_expenditure >= sponsor.price_limit:
					if sponsor.price_limit >= max_price:
						max_price = sponsor.price_limit
						max_sponsor = sponsor
		return max_sponsor

EXAMPLE_SORT_CHOICES = (
	(0, "freshest"),
	(1, "oldest"),
	(2, "precision"),
	(3, "votes"),
	(4, "unseen"),
	(5, "views"),
	

)



class Story(models.Model):
	the_story_itself = models.TextField(max_length=4000, default='')
	latest_change_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="sto_has_voted", default=None)
	views = models.IntegerField(default=0)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="sto_com", default=None)

class Relation(models.Model):
	the_relation_itself = models.CharField(max_length=200, default='')
	latest_change_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.ManyToManyField(Votes_Source, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="rel_has_voted", default=None)
	views = models.IntegerField(default=0)
	comment_sources = models.ManyToManyField(Comment_Source, related_name="rel_com", default=None)


SPONSOR_SORT_CHOICES = (
	(0, "alphabetical"),
	(1, "-alphabetical"),
	(2, "latest"),
	(3, "oldest"),
	(4, "lowtohigh"),
	(5, "hightolow"),
	(6, "low allowable"),
	(7, "high allowable"),
	(8, "votes"),
	(9, "-votes"),
	(10, "views"),
	(11, "-views"),
)


from numpy.random import choice

class Word(models.Model):
	the_word_itself	= models.CharField(max_length=200, default='')
	home_dictionary = models.ForeignKey(Dictionary_Source, on_delete=models.CASCADE, default=None, null=True)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, related_name='word_author', null=True)
	latest_change_date = models.DateTimeField(default=timezone.now)
	creation_date = models.DateTimeField(default=timezone.now)
	pronunciations = models.ManyToManyField(IPA_pronunciation, default=None)
	pronunciation_count = models.IntegerField(default=0)
	attributes = models.ManyToManyField(Attribute, default=None)
	attribute_count = models.IntegerField(default=0)
	similarities = models.ManyToManyField(Simulacrum, default=None)
	similarity = models.IntegerField(default=0)
	translations = models.ManyToManyField(Translation, default=None)
	translation_count = models.IntegerField(default=0)
	examples = models.ManyToManyField(Example, default=None)
	example_count = models.IntegerField(default=0)
	stories = models.ManyToManyField(Story, default=None)
	story_count = models.IntegerField(default=0)
	relations = models.ManyToManyField(Relation, default=None)
	relation_count = models.IntegerField(default=0)
	sponsors = models.ManyToManyField(Sponsor, default=None)
	sponsor_count = models.IntegerField(default=0)
	price_limit = models.IntegerField(default=0) # NEED TO MAKE IT LEGIT
	viewcount = models.IntegerField(default=0)
	spaces = models.ManyToManyField(SpaceSource, default=None)
	space_count = models.IntegerField(default=0)
	votes = models.ManyToManyField(Votes_Source, default=None)
	vote_count = models.IntegerField(default=0)
	ap_voters = models.ManyToManyField(Author, default=None, related_name="ap_voters")
	ap_voter_count = models.IntegerField(default=0)
	fontstyle = models.URLField(max_length=2000, blank=True, default='')
	fontsize = models.CharField(max_length=3, blank=True, default='')
	fontype = models.TextField(max_length=14400, default='')

	word_source = models.CharField(max_length=400, default='')

	word_wallet = models.IntegerField(default=0)
	
	class Meta:
		unique_together = (('home_dictionary', 'the_word_itself'),)


	def to_source(self):
		return Word_Source.objects.filter(author=self.author, the_word_itself=self.the_word_itself, home_dictionary=self.home_dictionary.the_dictionary_itself).first()

	def get_approved(self):
		self.home_dictionary.get_purchasers
		for purchaser in self.home_dictionary.purchasers.all():
			self.ap_voters.add(purchaser)


	def random_sponsor(self):
		if self.sponsors.count():
			return self.sponsors.all().order_by('?').first()
		else:
			return Sponsor.objects.get(id=1)
		



	# for every word in the sponsorship phrase, look for dictionaries owned by the owner of the word, and if those dictionaries contain that word in the sponsorship phrase 
	# then the spaces with that word, every post and comment in that space, and the space itself are also sponsored so you if like someone's "style" of content you can benefit every member of their tribe.'
	def trickle(self):
		for sponsor in self.sponsors.all():
			if sponsor.trickles>0:
				words = sponsor.the_sponsorship_phrase.split(" ")
				trickle = {}
				for word in words:
					for dic in self.Author.to_anon().dictionaries.all():
						for dics_word in dic.words.all():
							if word in dics_word.the_word_itself:
								for space in dics_word.spaces.all():
									trickle.append(space)
									space.sponsors.add(sponsor)
				for space in trickle:
					for post in space.posts.all():
						post.sponsors.add(sponsor)
						for dic in post.dictionaries.all():
							for word in dic.words.all():
								word.sponsors.add(sponsor)
						for com in post.comments.all():
							com.sponsors.add(sponsor)
							for dic in com.dictionaries.all():
								for word in dic.words.all():
									word.sponsors.add(sponsor)
				sponsor.trickle_down -= 1

	def update_sponsors(self):
		for sponsor in self.sponsors.all():
			if (sponsor.allowable_expenditure == 0 and sponsor.price_limit != 0) or (sponsor.author.to_anon().false_wallet < sponsor.price_limit):
				self.sponsors.remove(sponsor)
				sponsor.delete()

	def max_sponsor(self):
		max_price = 0

		pks = Sponsor.objects.values_list('pk', flat=True)
		random_pk = choice(pks)
		random_obj = Sponsor.objects.get(pk=random_pk)
		max_sponsor = random_obj
		for sponsor in self.sponsors.all().filter(payperview=False):
			if sponsor.allowable_expenditure >= sponsor.price_limit:
				if sponsor.price_limit >= max_price:
					max_price = sponsor.price_limit
					max_sponsor = sponsor
		return max_sponsor


WORD_SORT_CHOICES = (
	(0, "alphabetical"),
	(1, "latest"),
	(2, "definitions"),
	(3, "pronunciations"),
	(4, "attributes"),
	(5, "similarities"),
	(6, "translations"),
	(7, "examples"),
	(8, "relations"),
	(9, "sponsor"),
	(10, "viewcount"),
	(11, "-viewcount"),
	(12, "price"),
	(13, "-price"),
	(14, "spaces"),
	(15, "stories"),
	(16, "votes"),
	(17, "-votes"),
)

WORD_SORT_CHOICES_CHAR = (
	("the_word_itself", "Alphabetical"),
	("-the_word_itself", "Anti Alphabetical"),
	("-latest_change_date", "Most Recent Change"),
	("latest_change_date", "Least Recent Change"),
	("-creation_date", "Most Recently Created"),
	("creation_date", "Least Recently Created"),
	("-pronunciation_count", "Most Pronunciations"),
	("pronunciation_count", "Least Pronunciations"),
	("-attribute_count", "Most Attributes"),
	("attribute_count", "Least Attributes"),
	("-similarity_count", "Most Similarities"),
	("similarity_count", "Least Similarities"),
	("-translation_count", "Most Translations"),
	("translation_count", "Least Translations"),
	("-example_count", "Most Examples"),
	("example_count", "Least Examples"),
	("-relation_count", "Most Relations"),
	("relation_count", "Least Relations"),

	("-sponsor_count", "Most Sponsors"),
	("sponsor_count", "Least Sponsors"),
	("-viewcount", "Most Viewed"),
	("viewcount", "Least Viewed"),
	("-price_limit", "Most Expensive"),
	("price_limit", "Least Expensive"),
	("-space_count", "Most Spaces"),
	("space_count", "Least Spaces"),
	("-story_count", "Most Stories"),
	("story_count", "Least Stories"),
	("-vote_count", "Most Votes"),
	("vote_count", "Least Votes"),
)

class Votes(models.Model):
	the_vote_name = models.CharField(max_length=200, default='', unique=True)
	url2 = models.URLField(max_length=2000, blank=True, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	the_vote_style = models.ForeignKey(SpaceSource, on_delete=models.CASCADE, related_name='votename', default=1)
	votes = models.IntegerField(default=0)
	voters = models.ManyToManyField(Author, related_name="votestyle_voters", default=None)
	voters_count = models.IntegerField(default=0)
	
	creation_date = models.DateTimeField(default=timezone.now)

	def to_source(self):
		return Votes_Source.objects.get(author=author, the_vote_name__the_word_itself=the_vote_name)


class Votings(models.Model):
	votes = models.ManyToManyField(Votes, default=None)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	sponsor = models.ManyToManyField(Sponsor, default=None)
	ip = models.CharField(max_length=15, default="")
	creation_date = models.DateTimeField(default=timezone.now)


# of difference
class Analysis(models.Model):
	the_critique_itself = models.ManyToManyField(Word, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.ManyToManyField(Votes, default=None)
	vote_count = models.IntegerField(default=0)
	the_owner = models.CharField(max_length=200, default='')
	viewcount = models.IntegerField(default=0)


class Rendition(models.Model):
	the_rendition_itself = models.ManyToManyField(Word, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.ManyToManyField(Votes, default=None)
	vote_count = models.IntegerField(default=0)
	the_owner = models.CharField(max_length=200, default='')
	views = models.IntegerField(default=0)

class Sentence(models.Model):
	the_sentence_itself = models.ManyToManyField(Word, default=None)
	renditions = models.ManyToManyField(Rendition, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.ManyToManyField(Votes, default=None)
	vote_count = models.IntegerField(default=0)
	the_owner = models.CharField(max_length=200, default='')
	views = models.IntegerField(default=0)

class True_Translation(models.Model):
	the_translation_before = models.ManyToManyField(Word, default=None, related_name="translation_from_words")
	the_translation_after = models.ManyToManyField(Word, default=None, related_name="translation_to_words")
	latest_change_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	votes = models.ManyToManyField(Votes, default=None)
	vote_count = models.IntegerField(default=0)
	views = models.IntegerField(default=0)
ATTRIBUTE_SORT_CHOICES = (
	(0, "latest"),
	(1, "definitions"),
	(2, "votes"),
	(3, "-votes"),
	(4, "views"),
	(5, "-views"),
)



class Wordgroup_Source(models.Model):
	grouping = models.CharField(max_length=200)
	words = models.ManyToManyField(Word, default=None)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)

class Wordgroup(models.Model):
	grouping = models.CharField(max_length=200)
	words = models.ManyToManyField(Wordgroup_Source, default=None)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)

class Purchase_Order(models.Model):
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	last_paid = models.DateTimeField(default=timezone.now)


REPAYMENT_RATES = (
	("hourly", "Hourly"),
	("daily", "Daily"),
	("weekly", "Weekly"),
	("monthly", "Monthly"),
	("yearly", "Yearly"),
)

class Word_Loan(models.Model):
	amount_total = models.IntegerField(default=0)
	amount_owing = models.IntegerField(default=0)
	repayment_term = models.DateTimeField(default=timezone.now)
	pro_rata = models.FloatField(default=0.08)
	repayment_rates = models.CharField(default="hourly", choices=REPAYMENT_RATES, max_length=144)
	total_repayments_remaining = models.IntegerField(default=1)
	total_repayments = models.IntegerField(default=1)
	words = models.ManyToManyField(Word, default=None)


PRODUCT_CHOICES = (

	("unspecified", "Unspecified"),
	("package_post", "Posted Package"),
	("package_courier", "Courier Routes Package"),
	("package_direct", "Choose A Courier"),
	("package_pick_up", "Pick Up Yourself (with a pick-up)"),
	("package_collect", "Collect Yourself (by hand)"),
	("link", "Collect Links"),
	("poem", "Just Words"),
	("tickets", "Event Tickets"),
	("classes", "Classes"),
	("class_material", "Class Material"),
	("other", "Other Deal"),
)
 

class Sale(models.Model):
	user = models.OneToOneField(Author, default=None, on_delete=models.PROTECT)
	price_id = models.CharField(max_length=200, default="")
	deliver_to_address = models.CharField(max_length=200, default="Digital Product")
	deliver_to_instructions = models.CharField(max_length=1440, default="Leave By Postbox")
	courier_select = models.ManyToManyField(Author, default=None, related_name="courier_select")
	courier_order = models.CharField(max_length=1440, default="")
	courier_fees = models.CharField(max_length=1440, default="1")
	courier_1_to_2_drop_location = models.CharField(max_length=1440, default="")#manufacturer
	courier_2_to_3_drop_location = models.CharField(max_length=1440, default="")#supplier
	courier_3_to_4_drop_location = models.CharField(max_length=1440, default="")#distributer
	courier_4_to_5_drop_location = models.CharField(max_length=1440, default="")#dealer
	courier_5_to_6_drop_location = models.CharField(max_length=1440, default="")#runner
	courier_6_to_7_drop_location = models.CharField(max_length=1440, default="")#pusher
	courier_1_to_2_drop_eta = models.CharField(max_length=1440, default="")#pusher
	courier_1_to_2_drop_update = models.CharField(max_length=1440, default="")#pusher
	courier_2_to_3_drop_eta = models.CharField(max_length=1440, default="")#pusher
	courier_2_to_3_drop_update = models.CharField(max_length=1440, default="")#pusher
	courier_3_to_4_drop_eta = models.CharField(max_length=1440, default="")#pusher
	courier_3_to_4_drop_update = models.CharField(max_length=1440, default="")#pusher
	courier_4_to_5_drop_eta = models.CharField(max_length=1440, default="")#pusher
	courier_4_to_5_drop_update = models.CharField(max_length=1440, default="")#pusher
	courier_5_to_6_drop_eta = models.CharField(max_length=1440, default="")#pusher
	courier_5_to_6_drop_update = models.CharField(max_length=1440, default="")#pusher
	courier_6_to_7_drop_eta = models.CharField(max_length=1440, default="")#pusher
	courier_6_to_7_drop_update = models.CharField(max_length=1440, default="")#pusher
	

class Price(models.Model):
    name = models.CharField(max_length=200, default='')
    anon_user_id = models.CharField(max_length=256, default='')
    url2purchase = models.URLField(max_length=2000, blank=True, default='')
    description2purchase = models.TextField(max_length=144000, default='')
    description2helpsell = models.TextField(max_length=144000, default='')
    img = models.URLField(max_length=2000, blank=True, default='')
    stripe_price_id = models.CharField(max_length=100, default='')
    stripe_product_id = models.CharField(max_length=100, default='')
    price = models.IntegerField(default=0)  # cents

    monthly = models.BooleanField(default=False)
    comments = models.ManyToManyField(Comment_Source, default=None)
    sum_comments = models.IntegerField(default=0)
    invoices = models.ManyToManyField(Invoice, default=None)
    sum_invoices = models.IntegerField(default=0)

    sponsors = models.ManyToManyField(Sponsor, default=None)

    #location_of_product = models.CharField(max_length=200, default='Remote')
    point_of_sale = models.ManyToManyField(Sale, default=None)

    #product_type = models.CharField(choices=PRODUCT_CHOICES, max_length=200, default='unspecified')
    
    def author(self):
    	return Author.objects.get(username=Anon.objects.get(id=anon_user_id).username.username)

    def get_display_price(self):
        return "{0:.2f}".format(self.price / 100)

    def max_sponsor(self):
    	return self.sponsors.all().order_by('-price_limit').first() or Sponsor.all().order_by('-price_limit').first()

class Storefront(models.Model):
	author = models.OneToOneField(Author, default=None, on_delete=models.PROTECT)
	logo = models.OneToOneField(Word, default=None, on_delete=models.PROTECT)
	title = models.TextField(max_length=144, default="")
	preview_text = models.TextField(max_length=1440, default="")
	disclaimer = models.TextField(max_length=1440, default="")
	image_1 = models.URLField(max_length=2000, default="")
	image_2 = models.URLField(max_length=2000, default="")
	image_3 = models.URLField(max_length=2000, default="")
	image_4 = models.URLField(max_length=2000, default="")
	image_5 = models.URLField(max_length=2000, default="")
	template_section_size_1_1 = models.IntegerField(default=0)
	template_section_size_1_2 = models.IntegerField(default=0)
	template_section_size_1_3 = models.IntegerField(default=0)
	template_section_size_2_1 = models.IntegerField(default=0)
	template_section_size_2_2 = models.IntegerField(default=0)
	template_section_size_2_3 = models.IntegerField(default=0)
	template_section_size_3_1 = models.IntegerField(default=0)
	template_section_size_3_2 = models.IntegerField(default=0)
	template_section_size_3_3 = models.IntegerField(default=0)
	textblock_1  = models.TextField(max_length=14400, default="")
	textblock_2  = models.TextField(max_length=14400, default="")
	textblock_3  = models.TextField(max_length=14400, default="")
	textblock_4  = models.TextField(max_length=14400, default="")
	products = models.ManyToManyField(Price, default=None)
	sales = models.ManyToManyField(Sale, default=None)
	business_admin = models.ManyToManyField(Author, default=None, related_name="business_admin")



class Dictionary(models.Model):
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, related_name='dicauthor')
	public = models.BooleanField(default=False)
	for_sale = models.BooleanField(default=False)
	invite_only = models.BooleanField(default=False)
	invite_active = models.BooleanField(default=False)
	invite_code = models.CharField(max_length=200, default='') # Make a URL for inviting to dictionaries
	views = models.IntegerField(default=0)
	the_dictionary_itself = models.CharField(max_length=200, default='dictionary_name')
	latest_change_date = models.DateTimeField(default=timezone.now)
	creation_date = models.DateTimeField(default=timezone.now)
	traded_date = models.DateTimeField(default=timezone.now)
	purchase_orders = models.ManyToManyField(Purchase_Order, default=None, related_name='purchase_orders') # put purchaser with author when created
	allowed_to_view_authors = models.ManyToManyField(Author, default=None, related_name='dic_allowed')
	allowed_count = models.IntegerField(default=0)
	words = models.ManyToManyField(Word, default=None)
	word_count = models.IntegerField(default=0)
	wordgroups = models.ManyToManyField(Wordgroup, default=None)
	votes = models.ManyToManyField(Votes, default=None)
	votes_count = models.IntegerField(default=0)
	true_translations = models.ManyToManyField(True_Translation, default=None)
	viewcount = models.IntegerField(default=0)
	sentences = models.ManyToManyField(Sentence, default=None)
	sentence_count = models.IntegerField(default=0)
	analyses = models.ManyToManyField(Analysis, default=None)
	analysis_count = models.IntegerField(default=0)
	renditions = models.ManyToManyField(Rendition, default=None)
	rendition_count = models.IntegerField(default=0)
	revoked_authors = models.ManyToManyField(Author, default=None, related_name='dic_unallowed')
	
	prerequisite_dics = models.ManyToManyField(Dictionary_Source, default=None)
	prerequisite_dics_count = models.IntegerField(default=0)
	
	entry_fee = models.IntegerField(default=0)
	continuation_fee = models.IntegerField(default=0)


	dictionary_source = models.CharField(max_length=400, default='')

	word_loans = models.ManyToManyField(Word_Loan, default=None)
	storefronts = models.ManyToManyField(Storefront, default=None)
	dictionary_wallet = models.IntegerField(default=0)
	
	class Meta:
		unique_together = (('author', 'the_dictionary_itself'),)

	def get_allowed(self):
		for anon in Anon.objects.all():
			for dic in anon.purchased_dictionaries.all():
				if self.dictionary_name == dic.dictionary_name:
					self.allowed_to_view_authors.add(Author.objects.get(username=anon.username.username))
	# can be applied to everything with votes.
	

	def screen_votes(self, the_user):
		self.returning_vote_styles = ''
		for vote in self.votes.all():
			if vote in the_user.applied_votestyles:
				self.returning_vote_styles.append(vote)
		# must request the dictionary.returning_vote_styles.votes or the_vote_name
	def to_source(self):
		if Dictionary_Source.objects.filter(author=self.author, the_dictionary_itself=self.the_dictionary_itself):
			return Dictionary_Source.objects.get(author=self.author, the_dictionary_itself=self.the_dictionary_itself)
		else:
			Dictionary_Source.objects.create(author=self.author, the_dictionary_itself=self.the_dictionary_itself)
			return Dictionary_Source.objects.get(author=self.author, the_dictionary_itself=self.the_dictionary_itself)

	def sponsors_count(self):
		count = 0
		for word in self.words.all():
			count += word.sponsors.all().count()
		return count

	def max_sponsor(self):
		max_price = 0
		pks = Sponsor.objects.values_list('pk', flat=True)
		random_pk = choice(pks)
		random_obj = Sponsor.objects.get(pk=random_pk)
		max_sponsor = random_obj
		for word in self.words.all():
			for sponsor in word.sponsors.all().filter(payperview=False):
				if sponsor.allowable_expenditure >= sponsor.price_limit:
					if sponsor.price_limit >= max_price:
						max_price = sponsor.price_limit
						max_sponsor = sponsor
		return max_sponsor

	def prereq_ef_cost(self):
		pr_c_ef_cost = 0
		for dic in self.prerequisite_dics.all():
			pr_c_ef_cost += dic.entry_fee
		return pr_c_ef_cost

	def prereq_ct_cost(self):
		pr_c_ct_cost = 0
		for dic in self.prerequisite_dics.all():
			pr_c_ct_cost += dic.continuation_fee
		return pr_c_ct_cost

	def update_purchases(self):
		for purchase in self.purchase_orders.all():
			time_between = timezone.now() - purchase.last_paid
			if time_between.days > 30:
				if Anon.objects.get(username=User.objects.get(username=purchase.author.username)).false_wallet >= self.continuation_fee:
					Anon.objects.get(username=User.objects.get(username=purchase.author.username)).false_wallet -= self.continuation_fee
					Anon.objects.get(username=User.objects.get(username=self.author.username)).false_wallet += self.continuation_fee
				else:
					self.purchase_orders.remove(purchase)
					Anon.objects.get(username=User.objects.get(username=purchase.author.username)).purchased_dictionaries.remove(self)





# needs alphabetical
DICTIONARY_SORT_CHOICES = (
	(0, "freshest"),
	(1, "stalest"),
	(2, "common"),
	(3, "prized"),
	(4, "oldest"),
	(5, "newest"),
	(6, "dispersed"),
	(7, "origin"),
	(8, "words"),
	(9, "votes"),
	(10, "translations"),
	(11, "sentences"),
	(12, "renditions"),
	(13, "analyses"),
	(14, "viewcount"),
)

DICTIONARY_SORT_CHOICES_CHAR = (
	("-latest_change_date", "Most Recent Change"),
	("latest_change_date", "Least Recent Change"),
	("-views", "Most Viewed"),
	("views", "Least Viewed"),
	("-price", "Most Expensive"),
	("price", "Least Expensive"),
	("-creation_date", "Oldest"),
	("creation_date", "Newest"),
	("-traded_date", "Most Recent Trade"),
	("traded_date", "Least Recent Trade"),
	("-word_count", "Most Words"),
	("word_count", "Least Words"),
	("-votes_count", "Most Votes"),
	("votes_count", "Least Votes"),
	("-rendition_count", "Most Renditions"),
	("rendition_count", "Least Renditions"),
	("-analysis_count", "Most Analyses"),
	("analysis_count", "Least Analyses"),

)
	

#class Video(models.Model):
#	the_video_itself = VideoField(default='')

#class Playlist(models.Model):
#	videos = models.ManyToManyField(Video)
class Task(models.Model):
	the_owner = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	the_task_itself = models.TextField(max_length=200, default='')
	priority = models.IntegerField(default=0)

'''
class Anon(AbstractBaseUser):
	dictionaries = models.ManyToManyField(Dictionary, default=None)
	examples = models.ManyToManyField(Example, default=None) # saved comments
	tasks = models.ManyToManyField(Task, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	#playlists = models.ManyToManyField(Playlist)
	spaces = models.ManyToManyField(SpaceSource, default=None)
	username = models.CharField(max_length=40, unique=True)
	USERNAME_FIELD = 'username'
	objects = UserManager()
'''

#class CommentManager(models.Manager):
#	def filter_by_instance(self, instance):


class Attribution(models.Model):
	author = models.OneToOneField(Author, on_delete=models.PROTECT, default=None)
	variable = models.FloatField(default=0)
	words = models.TextField(max_length=50, default="I think this is Working") #search for sponsorship_phrase


class AngelNumber(models.Model):
	digits = models.IntegerField(default=1)
	numbers = models.IntegerField(default=0)
	description = models.TextField(max_length=14400)
	sponsors = models.ManyToManyField(Sponsor, default=None)
	attributions = models.ManyToManyField(Attribution, default=None)


class Comment(MPTTModel):
	angel_numbers = models.ManyToManyField(AngelNumber, default=None)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None)
	dictionaries = models.ManyToManyField(Dictionary, default=None)
	sum_dictionaries = models.IntegerField(default=0)
	allowed_to_view_authors = models.ManyToManyField(Author, default=None, related_name='comment_allowed')
	words = models.ManyToManyField(Word, default=None)
	sum_dictionaries = models.IntegerField(default=0)
	body = models.TextField(max_length=144000, default='')
	sponsors = models.ManyToManyField(Sponsor, default=None)
	top_price = models.IntegerField(default=0)
	votes = models.ManyToManyField(Votes, default=None)
	votes_count = models.IntegerField(default=0)
	viewcount = models.IntegerField(default=0)
	latest_change_date = models.DateTimeField(default=timezone.now)
	has_commented = models.ManyToManyField(Author, default=None, related_name='comments_has_commented')
	sum_has_commented = models.IntegerField(default=0)
	has_viewed = models.ManyToManyField(Author, default=author, related_name='comments_has_viewed')
	sum_has_viewed = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, default=None, related_name='comment_has_voted')
	sum_has_voted = models.IntegerField(default=0)
	parent = TreeForeignKey('self', on_delete=models.CASCADE, default=None, null=True, blank=True, related_name='children', db_index=True)
	children_count = models.IntegerField(default=0)

	def __str__(self):
		return self.body

	def __unicode__(self):
   		return unicode(self.body) or u''

	def children(self):
		return Comments.objects.filter(parent=self)

	@property
	def is_parent(self):
		if self.parent is not None:
			return False
		return True

	class MPTTMeta:
		order_insertion_by = ['votes_count', 'children_count']

	

	def max_sponsor(self):
		max_sponsor = self.sponsors.order_by('-price_limit').first()
		return max_sponsor

COMMENT_SORT_CHOICES = (
	(0, "dictionaries"),
	(1, "-dictionaries"),
	(2, "words"),
	(3, "-words"),
	(4, "sponsors"),
	(5, "-sponsors"),
	(6, "uniques"),
	(7, "-uniques"),
	(8, "viewcount"),
	(9, "unseen"),
	(10, "latest"),
	(11, "definition"),
	(12, "discussed"),
	(13, "final"),
	(14, "voters"),
)

COMMENT_SORT_CHOICES_CHAR = (
	("sum_dictionaries", "Generalist"),
	("-sum_dictionaries", "Broadness"),
	("sum_words", "Less Complex"),
	("-sum_words", "More Intelligent"),
	("sum_sponsors", "Encouraged"),
	("-sum_sponsors", "Discouraged"),
	("votes_uniques", "Less Uniques"),
	("-votes_uniques", "More Uniques"),
	("-viewcount", "Viewcount"),
	("viewcount", "Unseen"),
	("-latest_change_date", "Latest"),
	("latest_change_date", "Unchanged"),
	("-sum_has_commented", "Discussed"),
	("sum_has_commented", "Unspoken"),
)

class PostSource(models.Model):
	post_id = models.CharField(max_length=256, default='')

	def to_full():
		return Post.objects.get(id=int(post_id))
	
class Edit(models.Model):
	body = models.TextField(max_length=144000, default='')
	author = models.ForeignKey(Author, on_delete=models.PROTECT, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	post_source = models.ForeignKey(PostSource, on_delete=models.PROTECT, default=None)





class CommentLocations(models.Model):
	comments = models.ManyToManyField(Comment, default=None)

	from_top = models.IntegerField(default=0)
	from_left = models.IntegerField(default=0)



class SearchURL(models.Model):
	name = models.CharField(max_length=400, default='')
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, null=True)
	url = models.URLField(max_length=2000)
	comment_locations = models.ManyToManyField(CommentLocations, default=None)
	comment_height = models.IntegerField(default=0)
	comment_width = models.IntegerField(default=0)
	sum_comments = models.IntegerField(default=0)
	sponsors = models.ManyToManyField(Sponsor, default=None)
	sum_sponsors = models.IntegerField(default=0)
	viewcount = models.IntegerField(default=0)
	change_count = models.IntegerField(default=0)
	latest_change_date = models.DateTimeField(default=timezone.now)
	pub_date = models.DateTimeField(default=timezone.now)
	public = models.BooleanField(default=1)
	allowed_to_view_authors = models.ManyToManyField(Author, default=None, related_name='search_allowed')
	votes = models.ManyToManyField(Votes, default=None)
	votes_count = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, related_name="search_has_voted", default=None)
	views = models.IntegerField(default=0)
	post_allowed = models.ManyToManyField(Author, default=None, related_name='search_allowed_authors')
	cc = models.CharField(max_length=400, default='')
	img = models.URLField(max_length=2000, blank=True, default='')
	stripe_price_id = models.CharField(max_length=100, default='')
	stripe_product_id = models.CharField(max_length=100, default='')
	price = models.IntegerField(default=0)  # cents

	monthly = models.BooleanField(default=False)


    
class Barcode(models.Model):
	barcode_value = models.IntegerField(default=0)
	barcode_meaning = models.TextField(default='', max_length=144)
	barcode_definition = models.TextField(default='', max_length=1440)
	barcode_story = models.TextField(default='', max_length=14400)
	has_commented = models.ManyToManyField(Author, default=None, related_name='barcode_has_commented')
	sum_has_commented = models.IntegerField(default=0)
	has_viewed = models.ManyToManyField(Author, default=None, related_name='barcode_has_viewed')
	sum_has_viewed = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, default=None, related_name='barcode_has_voted')
	sum_has_voted = models.IntegerField(default=0)
	votes_uniques = models.IntegerField(default=0)
	comments = models.ManyToManyField(Comment, default=None)
	sum_comments = models.IntegerField(default=0)
	sponsors = models.ManyToManyField(Sponsor, default=None)
	sum_sponsors = models.IntegerField(default=0)
	viewcount = models.IntegerField(default=0)
	change_count = models.IntegerField(default=0)
	latest_change_date = models.DateTimeField(default=timezone.now)
	
	
	
	

class Post(models.Model):
	author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, null=True)
	angel_numbers = models.ManyToManyField(AngelNumber, default=None)
	barcodes = models.ManyToManyField(Barcode, default=None)
	edits = models.ManyToManyField(Edit, default=None)
	products = models.ManyToManyField(Price, default=None)
	title = models.CharField(max_length=200, default='')
	url2 = models.URLField(max_length=2000, blank=True, default='')
	img = models.URLField(max_length=2000, blank=True, default='')
	has_commented = models.ManyToManyField(Author, default=None, related_name='post_has_commented')
	sum_has_commented = models.IntegerField(default=0)
	has_viewed = models.ManyToManyField(Author, default=None, related_name='post_has_viewed')
	sum_has_viewed = models.IntegerField(default=0)
	has_voted = models.ManyToManyField(Author, default=None, related_name='post_has_voted')
	sum_has_voted = models.IntegerField(default=0)
	votes_uniques = models.IntegerField(default=0)
	under_talked = models.FloatField(default=0)
	dictionaries = models.ManyToManyField(Dictionary, default=None)
	sum_dictionaries = models.IntegerField(default=0)
	words = models.ManyToManyField(Word, default=None)
	sum_words = models.IntegerField(default=0)
	body = models.TextField(max_length=144000, default='')
	comments = models.ManyToManyField(Comment, default=None)
	sum_comments = models.IntegerField(default=0)
	sponsors = models.ManyToManyField(Sponsor, default=None)
	sum_sponsors = models.IntegerField(default=0)
	viewcount = models.IntegerField(default=0)
	change_count = models.IntegerField(default=0)
	latest_change_date = models.DateTimeField(default=timezone.now)
	pub_date = models.DateTimeField(default=timezone.now)
	public = models.BooleanField(default=1)
	spaces = models.ManyToManyField(SpaceSource, default=None)
	sum_spaces = models.IntegerField(default=0)
	allowed_to_view_authors = models.ManyToManyField(Author, default=None, related_name='post_allowed')
	votes = models.ManyToManyField(Votes, default=None)
	votes_count = models.IntegerField(default=0)
	post_allowed = models.ManyToManyField(Author, default=None, related_name='post_allowed_authors')
	post_source = models.CharField(max_length=400, default='')
	cc = models.CharField(max_length=400, default='')
	search_urls = models.ManyToManyField(SearchURL, default=None)

	shuffle = models.IntegerField(default=0)
	attention = models.IntegerField(default=99999999)
	sales = models.ManyToManyField(Sale, default=None)

	def __str__(self):
		return self.title

	def __eq__(self, other):
		return self.id == other.id

	def __hash__(self):
		return hash(('id', self.id))
	
	def __unicode__(self):
   		return unicode(self.title) or u''


	def screen_votes(self, the_user):
		for vote in self.votes.all():
			if vote in the_user.applied_votestyles:
				self.returning_vote_styles.append(vote)


	def attention_save(self, loggedinanon):
		densities = loggedinanon.home_page_density.order_by('?')[0:25]
		for density in densities:
			denseness = []
			for densitivity in density.density.all():
				densensess.append(densitivity.dense)
			posts = []
			for post_id in density.post_ids.all():
				posts.append(Post.objects.get(id=post_id.the_posts_id))

	
	def shuffle_save(self, loggedinanon, count):
		posts = Post.objects.order_by('?')[count: count+25]
		i = 0
		for post in posts:
			post.shuffle = i
			post.save()
			i+=1

	def max_sponsor(self):
		max_sponsor = self.sponsors.order_by('-price_limit').first()
		if not max_sponsor:
			return Sponsor.objects.all().order_by('-price_limit').first()
		return max_sponsor

	def max(self):
		max_sponsor = self.sponsors.order_by('-price_limit').first()
		if not max_sponsor:
			return Sponsor.objects.all().order_by('-price_limit').first()
		return max_sponsor

	def first_sorted_comment(self, anon):
		# takes each comment and the anon's sort preference to auto select 1 comment for duo-displays.
		return 0

	def preview(self):
		if len(self.url):
			# title, description, image = web_preview(self.url, timeout=5)
			title, description, image = None, None, None
		else:
			image = None
		return image

	def name_sort_dics(self):
		
		return self.dictionaries.all().order_by("the_dictionary_itself")

	def date_sort_dics(self):
		
		return self.dictionaries.all().order_by("creation_date")

	def count_sort_votes(self):
		return self.votes.all().order_by("votes")


POST_SORT_CHOICES = (
	(0, "viral"),
	(1, "early"),
	(2, "freshest"),
	(3, "eldest"),
	#(4, "uniques"),
	#(5, "voters"),
	#(6, "broadness"),
	#(7, "intricacy"),
	#(8, "talkative"),
	#(9, "homes"),
	#(10, "encouraged"),
	(11, "votes"),
	(12, "unvoted"),
	
)

POST_SORT_CHOICES_CHAR = (
	("-viewcount", "Viral"),
	("viewcount", "Early"),
	("-latest_change_date", "Freshest"),
	("latest_change_date", "Eldest"),
	("-sum_has_viewed", "Uniques"),
	("-sum_has_voted", "Voters"),
	("-sum_dictionaries", "Broadness"),
	("-sum_words", "Intricacy"),
	("-sum_comments", "Talkative"),
	("sum_comments", "Silencio"),
	("-under_talked", "Under Commented"),
	("under_talked", "Over Commented"),
	("-sum_spaces", "Homes"),
	("-sum_sponsors", "Encouraged"),
	("-votes_count", "Votes"),
	("votes_count", "Unvoted"),
	("-shuffle", "Shuffle"),
	("shuffle", "Counter-Shuffle"),
	("-attention", "Attention Span Up"),
	("attention", "Scroll Past"),

)

class Dictionary_Loan(models.Model):
	amount_total = models.IntegerField(default=0)
	amount_owing = models.IntegerField(default=0)
	repayment_term = models.DateTimeField(default=timezone.now)
	pro_rata = models.FloatField(default=0.08)
	repayment_rates = models.CharField(default="Hourly", choices=REPAYMENT_RATES, max_length=144)
	total_repayments_remaining = models.IntegerField(default=1)
	total_repayments = models.IntegerField(default=1)
	dictionaries = models.ManyToManyField(Dictionary, default=None)

class ConditionEdit(models.Model):
	conditions = models.TextField(max_length=1666000, default="Pay Attention 3000 Pounds of Flesh")
	votes = models.ManyToManyField(Author, default=None)


class ConditionalVote(models.Model):
	votee = models.OneToOneField(Author, default=None, on_delete=models.PROTECT, related_name='conditional_votee')
	votes = models.ManyToManyField(Author, default=None, related_name='conditional_votes')

class Terms(models.Model):
	chapter = models.CharField(max_length=160, default='')
	conditionees_select_primate = models.BooleanField(default=False)
	conditioners_select_external = models.BooleanField(default=False)
	conditionees = models.ManyToManyField(Author, default=None, related_name="conditionees") # must stake primation fee to accept, under certain conditions, votes on edits to chapters, chosen by precessive council members
	conditionee_votes = models.ManyToManyField(ConditionalVote, default=None, related_name="conditionee_votes")
	conditioners = models.ManyToManyField(Author, default=None, related_name="conditioners") # votes on edits to conditions, includes precessive council members
	conditioner_votes = models.ManyToManyField(ConditionalVote, default=None, related_name="conditioner_votes")
	conditions = models.TextField(max_length=1666000, default="Pay Attention 3000 Pounds of Flesh") # changed by conditioners, judged by primation reference, written by precessive council members
	condition_edits = models.ManyToManyField(ConditionEdit, default=None) # changed by conditioners, judged by primation reference, written by precessive council members
	accostings = models.TextField(max_length=6660000, default="You've been accounted for as for the following") # written by terms council members
	primation_fee = models.IntegerField(default=1000) # price up for grabs if you violate certain conditions as punishment (how much you have to keep in your account to pay if you lose your job)
	
	delete = models.BooleanField(default=False)
	primation_reference = models.ManyToManyField(Author, default=None, related_name="reference") # who judges the paying of the primation fee, who you have to impress to keep your balance / job. # I'll put 10k on the line to prove to you that I can sell his product. Etc.

class Chapters(models.Model):
	title = models.CharField(max_length=220, default="Chapter X")
	verses = models.TextField(max_length=14400, default="In the beginning")
	side_notes = models.TextField(max_length=144000, default="About this text") # by legislative
	external_commentary = models.TextField(max_length=144000, default="You've heard about this text") # by administrative
	execution_prose = models.TextField(max_length=144000, default="You hear this text better when we say") # by executive
	judiciary_feedback = models.TextField(max_length=144000, default="You said this last time") # by executive


MEMBER_VOTE_TYPE_CHAR = (
	("legislative", "Legislative"),
	("administrative", "Administrative"),
	("executive", "Executive"),
	("judiciary", "Judiciary"),
)

class MemberVotes(models.Model):
	voter = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="voter")
	space = models.ForeignKey(SpaceSource, on_delete=models.CASCADE)
	vote_type = models.CharField(max_length=144, choices=MEMBER_VOTE_TYPE_CHAR, default="legislative")
	vote_member = models.OneToOneField(Author, on_delete=models.PROTECT, default=None, related_name="vote_member")

class TaxIncentive(models.Model):
	words = models.ManyToManyField(Word, default=None)
	tax = models.IntegerField(default=0)
	bounty = models.IntegerField(default=0)
	voters = models.ManyToManyField(Author, default=None, related_name="voters")
	initiators = models.ManyToManyField(Author, default=None, related_name="initiators")
	passers = models.ManyToManyField(Author, default=None, related_name="passers") # passes pass whether the bounty is due
	bounty_description = models.TextField(max_length=14400, default="")



class ServerUser(models.Model):
	username = models.CharField(max_length=140, default='')
	player_id = models.CharField(max_length=140, default="0")

class ServerHistory(models.Model):
	server_name = models.CharField(max_length=140, default='')
	server_log_in_date = models.DateTimeField(default=timezone.now)
	server_users = models.ManyToManyField(ServerUser, default=None)

class Player(models.Model):
	player_name = models.CharField(max_length=140, default='')
	last_logged_in = models.DateTimeField(default=timezone.now)
	server_history = models.ManyToManyField(ServerHistory, default=None)


class PlayerCount(models.Model):
	count = models.IntegerField(default=0)
	max_size_of_server = models.IntegerField(default=12)
	players = models.ManyToManyField(Player, default=None)
	current_log_date = models.DateTimeField(default=timezone.now)


class GameMode(models.Model):
	game_mode_name = models.CharField(default='', max_length=140)

class MinecraftServer(models.Model):
	version = models.FloatField(default=0)
	domain = models.TextField(max_length=140, default='')
	port = models.IntegerField(default=1234)
	player_count = models.ManyToManyField(PlayerCount, default=None)
	online = models.BooleanField(default=False)
	location = models.CharField(max_length=140, default='')
	tags = models.ManyToManyField(Word, default=None)
	registered_by = models.CharField(max_length=140, default='')
	registered_since = models.DateTimeField(default=timezone.now)
	last_update = models.DateTimeField(default=timezone.now)
	theme = models.ManyToManyField(SpaceSource, default=None)
	about = models.TextField(default='', max_length=4000)
	website = models.URLField(default='', max_length=400)
	game_modes = models.ManyToManyField(GameMode, default=None)
	sponsor = models.ManyToManyField(Sponsor, default=None)




class Space(models.Model):
	tax_incentives = models.ManyToManyField(TaxIncentive, default=None)
	the_space_itself = models.ForeignKey(Word, on_delete=models.CASCADE, default=00000) # check pre-requisite dictionary acquired
	angel_numbers = models.ManyToManyField(AngelNumber, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	sidebar = models.TextField(max_length=1000, default='')
	values = models.TextField(max_length=1000, default='Values')
	vision = models.TextField(max_length=1000, default='Vision')
	mission = models.TextField(max_length=1000, default='Mission')
	minecraft_servers = models.ManyToManyField(MinecraftServer, default=None)

	author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='author', default=None)
	viewcount = models.IntegerField(default=0)
	posts_viewcount = models.IntegerField(default=0)
	posts = models.ManyToManyField(Post, default=None)
	postcount = models.IntegerField(default=0)
	votes = models.ManyToManyField(Votes, default=None)
	votes_count = models.IntegerField(default=0)
	sponsors = models.ManyToManyField(Sponsor, default=None)
	sponsor_count = models.IntegerField(default=0)
	approved_voters = models.ManyToManyField(Author, related_name='approved_voters', default=None)
	approved_voter_count = models.IntegerField(default=0)
	public = models.BooleanField(default=False)
	for_sale = models.BooleanField(default=False)
	free_sponsorships = models.BooleanField(default=False)
	anyone_can_edit = models.BooleanField(default=False)
	elected_sponsorships = models.BooleanField(default=False)

	entry_fee = models.IntegerField(default=1)
	continuation_fee = models.IntegerField(default=1)

	space_wallet = models.IntegerField(default=0)

	invite_only = models.BooleanField(default=False)
	invite_active = models.BooleanField(default=False)
	invite_code = models.CharField(max_length=200, default='')

	dictionary_loans = models.ManyToManyField(Dictionary_Loan, default=None)

	elected_legislative = models.BooleanField(default=False) # writes the rule book for the space
	elected_administrative = models.BooleanField(default=False) # decides how to interpret the rules for a given breach
	elected_executive = models.BooleanField(default=False) # apprehends publicly
	elected_judiciary = models.BooleanField(default=False) # designates appropriate punishment

	successive = models.BooleanField(default=False) # each higher level of government can kick the lower levels
	progressive = models.BooleanField(default=False) # each lower level of government can vote to elevate to higher levels

	legislative_members = models.ManyToManyField(Author, default=None, related_name="legislative_members")
	legislative_level = models.IntegerField(default=0) # designates how many members there are to be max.
	legislative_votes = models.ManyToManyField(MemberVotes, default=None, related_name="legislative_votes") #who's been voted to be included in this group
	legislative_blind = models.BooleanField(default=False)
	legislative_conditionees_select_primate = models.BooleanField(default=False)
	legislative_conditioners_select_external = models.BooleanField(default=False)
	administrative_members = models.ManyToManyField(Author, default=None, related_name="administrative_members")
	administrative_level = models.IntegerField(default=0)
	administrative_votes = models.ManyToManyField(MemberVotes, default=None, related_name="administrative_votes")
	administrative_blind = models.BooleanField(default=False)
	administrative_conditionees_select_primate = models.BooleanField(default=False)
	administrative_conditioners_select_external = models.BooleanField(default=False)
	executive_members = models.ManyToManyField(Author, default=None, related_name="executive_members")
	executive_level = models.IntegerField(default=0)
	executive_votes = models.ManyToManyField(MemberVotes, default=None, related_name="executive_votes")
	executive_blind = models.BooleanField(default=False)
	executive_conditionees_select_primate = models.BooleanField(default=False)
	executive_conditioners_select_external = models.BooleanField(default=False)
	judiciary_members = models.ManyToManyField(Author, default=None, related_name="judiciary_members")
	judiciary_level = models.IntegerField(default=0)
	judiciary_votes = models.ManyToManyField(MemberVotes, default=None, related_name="judiciary_votes")
	judiciary_blind = models.BooleanField(default=False)
	judiciary_conditionees_select_primate = models.BooleanField(default=False)
	judiciary_conditioners_select_external = models.BooleanField(default=False)
	
	legislation = models.ManyToManyField(Chapters, default=None, related_name="legislation")
	legislating_terms = models.ManyToManyField(Terms, default=None, related_name="legislating")
	administration = models.ManyToManyField(Chapters, default=None, related_name="administration")
	administrating_terms = models.ManyToManyField(Terms, default=None, related_name="administrating")
	execution = models.ManyToManyField(Chapters, default=None, related_name="execution")
	executing_terms = models.ManyToManyField(Terms, default=None, related_name="executing")
	adjudication = models.ManyToManyField(Chapters, default=None, related_name="adjudication")
	adjudicating_terms = models.ManyToManyField(Terms, default=None, related_name="adjudicating")

	storefronts = models.ManyToManyField(Storefront, default=None)
	

	class Meta:
		unique_together = (('author', 'the_space_itself'),)

	def __str__(self):
		return self.the_space_itself.the_word_itself

	def get_absolute_url(self):
		return reverse("Bable:space", kwargs={"id": self.id})

	def __unicode__(self):
		return unicode(self.the_space_itself) or u''

	@property
	def count_posts(self):
		return self.posts.all().count()

	@property
	def count_votes(self):
		return self.votes.all().count()

	@property
	def count_sponsors(self):
		return self.sponsors.all().count()

	@property
	def count_approved_voters(self):
		return self.approved_voters.all().count()

	def to_source(self):
		return SpaceSource.objects.all().filter(author=self.author, the_space_itself=self.the_space_itself.to_source()).first()

	def max_sponsor(self):
		max_price = 0
		pks = Sponsor.objects.values_list('pk', flat=True)
		if not pks:
			Sponsor.objects.get(id=1).delete()
			new_spon = Sponsor.objects.create(img="https://www.predictionary.us/B/static/babylonpolice.com.gif", url2="https://www.predictionary.us", author=Author.object.get(username='test'))
			pks = [new_spon.id]
		random_pk = choice(pks)
		random_obj = Sponsor.objects.get(pk=random_pk)
		max_sponsor = random_obj
		for sponsor in self.sponsors.all().filter(payperview=False):
			if sponsor.allowable_expenditure >= sponsor.price_limit:
				if sponsor.price_limit >= max_price:
					max_price = sponsor.price_limit
					max_sponsor = sponsor
		return max_sponsor

SPACE_SORT_CHOICES = (
	(0, "viral"),
	(1, "early"),
	(2, "freshest"),
	(3, "eldest"),
	(4, "starter"),
	(5, "useful"),
	(6, "encourage"),
	(7, "synched"),
)

SPACE_SORT_CHOICES_CHAR = (
	("-viewcount", "Most Viewed"),
	("viewcount", "Least Viewed"),
	("-latest_change_date", "Recent Change"),
	("latest_change_date", "Distant Change"),
	("-posts_viewcount", "Most Post Views"),
	("posts_viewcount", "Least Post Views"),
	("-votes_count", "Most Votes"),
	("votes_count", "Least Votes"),
	("-sponsor_count", "Most Sponsored"),
	("sponsor_count", "Least Sponsored"),
	("-approved_voter_count", "Most Approved Voters"),
	("approved_voter_count", "Least Approved Voters"),
)

ANON_SORT_CHOICES = (
	(0, "dictionaries"),
	(1, "saved_dictionaries"),
	(2, "examples"),
	(3, "tasks"),
	(4, "latest"),
	(5, "posted_comments"),
	(6, "saved_comments"),
	(7, "posts"),
	(8, "spaces"),
	(9, "saved_spaces"),
)


import gpg_lite as gpg
import os
if os.name =="nt":
	class Message(models.Model):
		sender = models.OneToOneField(Author, on_delete=models.CASCADE, related_name='author_sender')
		receiver = models.OneToOneField(Author, on_delete=models.CASCADE, related_name='author_receiver')
		encrypted_message = models.TextField(max_length=10000, default='')
		key_fingerprint = models.CharField(max_length=1000, default='')

		

		def encrypt_message(message):
			self.encrypted_message = message
			return message

		def decrypt_message():
			return self.encrypted_message
			
else:
	gpg_store = gpg.GPGStore()
	class Message(models.Model):
		sender = models.OneToOneField(Author, on_delete=models.CASCADE, related_name='author_sender')
		receiver = models.OneToOneField(Author, on_delete=models.CASCADE, related_name='author_receiver')
		encrypted_message = models.TextField(max_length=10000, default='')
		key_fingerprint = models.CharField(max_length=1000, default='')

		def set_fingerprint():
			self.key_fingerprint = str(gpg_store.gen_key(key_type='RSA', key_length=4096, full_name=self.sender.username, email=self.sender.to_anon().email, passphrase=self.sender.to_anon().password))

		def encrypt_message(message):
			encrypted_file = '/gpg/'+self.key_fingerprint
			with open(encrypted_file, "w") as f:
				gpg_store.encrypt(
					source=message,
					recipients=[self.receiver.to_anon().email],
					output=f,
					sign=self.sender.to_anon().email,
					passphrase=self.sender.to_anon().password)
			with open(encrypted_file, "rb") as f:
				message = f.read()
				self.encrypted_message = message
				return self.encrypted_message

		def decrypt_message():
			encrypted_file = '/gpg/'+self.key_fingerprint
			decrypted_file = '/gpg/'+self.receiver.username
			with open(encrypted_file, "rb") as f, open(decrypted_file, "w") as f_out:
				gpg_store.decrypt(
					source=f,
					output=f_out,
					passphrase=self.receiver.to_anon().password)
				return f_out.read()


ANON_SORT_CHOICES_CHAR = (
	("-sum_dictionaries", "Most Dictionaries"),
	("sum_dictionaries", "Least Dictionaries"),
	("-sum_purchased_dictionaries", "Most Purchased Dictionaries"),
	("sum_purchased_dictionaries", "Least Purchased Dictionaries"),
	("-sum_excluded_authors", "Most Authors Blocked"),
	("sum_excluded_authors", "Least Authors Blocked"),
	("-sum_examples", "Most Examples"),
	("sum_examlpes", "Least Examples"),
	("-sum_tasks", "Most Tasks"),
	("sum_tasks", "Least Tasks"),
	("-sum_posts", "Most Posts"),
	("sum_posts", "Least Posts"),
	("-sum_posted_comments", "Most Posted Comments"),
	("sum_posted_comments", "Least Posted Comments"),
	("-sum_saved_comments", "Most Saved Comments"),
	("sum_saved_comments", "Least Saved Comments"),
	("-sum_purchased_spaces", "Most Purchased Spaces"),
	("sum_purchased_spaces", "Least Purchased Spaces"),
	("-sum_created_votestyles", "Most Created Votestyles"),
	("sum_created_votestyles", "Least Created Votestyles"),
	("-latest_change_date", "Most Recent Update"),
	("latest_change_date", "Least Recent Update"),
	("-creation_date", "Newest Account Creation"),
	("creation_date", "Oldest Account Creation"),
)
class Densitivity(models.Model):
	dense = models.IntegerField(default=0)

class Post_id(models.Model):
	the_posts_id = models.IntegerField(default=0)


class Page_Density(models.Model):
	ip = models.CharField(max_length=15, default="")
	time_spent = models.IntegerField(default=0)
	density = models.ManyToManyField(Densitivity, default=None)
	post_ids = models.ManyToManyField(Post_id, default=None)
	scroll_height = models.IntegerField(default=0)
	scroll_type = models.CharField(choices=POST_SORT_CHOICES_CHAR, default="latest_change_date", max_length=180)
	client_height = models.IntegerField(default=0)
	duration = models.IntegerField(default=2)


class Loan(models.Model):
	amount_total = models.IntegerField(default=0)
	amount_owing = models.IntegerField(default=0)
	repayment_term = models.DateTimeField(default=timezone.now)
	pro_rata = models.FloatField(default=0.08)
	repayment_rates = models.CharField(default="hourly", choices=REPAYMENT_RATES, max_length=144)
	total_repayments_remaining = models.IntegerField(default=1)
	total_repayments = models.IntegerField(default=1)

	spaces = models.ManyToManyField(Space, default=None)



class RQAnswers(models.Model):
	answer = models.TextField(max_length=140)


class RequestQuestion(models.Model):
	question = models.TextField(max_length=140)
	answers = models.ManyToManyField(RQAnswers, default=None)



class Availability(models.Model):
	concerning = models.TextField(max_length=140, default="All")
	location = models.TextField(max_length=140, default="Zoom/Meets/Messenger/WhatsApp/Instagram/Discord")
	request_questions = models.ManyToManyField(RequestQuestion, default=None, related_name="request_questions")
	post_request_questions = models.ManyToManyField(RequestQuestion, default=None, related_name="post_request_questions")
	words = models.ManyToManyField(Word, default=None) # for styling the block on the calendar
	start_time = models.DateTimeField(timezone.now)
	end_time = models.DateTimeField(timezone.now)
	available = models.BooleanField(default=False) #mark either when you're availabilities are, or your unavailabilities are. "I can do any time from X" vs "I can't do these times"




class MoveTo(models.Model):
	x = models.IntegerField(default=0)
	y = models.IntegerField(default=0)
	#context.moveTo(x, y)

class LineTo(models.Model):
	x = models.IntegerField(default=0)
	y = models.IntegerField(default=0)
	#context.lineTo(x, y)

class QuadraticCurveTo(models.Model):
	x = models.IntegerField(default=0)
	y = models.IntegerField(default=0)
	p1 = models.IntegerField(default=0)
	p2 = models.IntegerField(default=0)
	#context.quadraticCurveTo(x, y, p1, p2)
#circle
class ArcTo(models.Model):
	x = models.IntegerField(default=0)
	y = models.IntegerField(default=0)
	radius = models.IntegerField(default=0)
	start_angle = models.IntegerField(default=0) #0
	end_angle = models.IntegerField(default=0) # Math.PI
	counter_clockwise = models.BooleanField(default=False) # false
	# context.arc(x, y, radius, start_angle, end_angle, counter_clockwise)

class BezierCurveTo(models.Model):
	x1 = models.IntegerField(default=0)
	y1 = models.IntegerField(default=0)
	x2 = models.IntegerField(default=0)
	y2 = models.IntegerField(default=0)
	x3 = models.IntegerField(default=0)
	y3 = models.IntegerField(default=0)
	#context.bezierCurveTo(x1, y1, x2, y2, x3, y3)



class Movement(models.Model):
	move_to = models.OneToOneField(MoveTo, default=None, on_delete=models.CASCADE)
	line_to = models.OneToOneField(LineTo, default=None, on_delete=models.CASCADE)
	quadratic_curve_to = models.OneToOneField(QuadraticCurveTo, default=None, on_delete=models.CASCADE)
	arc_to = models.OneToOneField(ArcTo, default=None, on_delete=models.CASCADE)
	line_width = models.FloatField(default=5.0)
	stroke_style = models.TextField(max_length=2000, default="black")
	stroke = models.BooleanField(default=False)
	fill_style = models.TextField(max_length=2000, default="black")
	fill = models.BooleanField(default=False)
	order = models.IntegerField(default=0)

class Path(models.Model):
	movements = models.ManyToManyField(Movement, default=None)

class Triangle(models.Model):
	a = models.IntegerField(default=0)
	b = models.IntegerField(default=0)
	c = models.IntegerField(default=0)
	x = models.IntegerField(default=0)
	y = models.IntegerField(default=0)
	theta = models.FloatField(default=0)
	fill_style = models.CharField(default='blue', max_length=14)

#var ctx = canvas.getContext('2d');
#ctx.beginPath();
#ctx.moveTo(50, 100);
#ctx.lineTo(100, 50);
#ctx.lineTo(150, 100);
#ctx.lineTo(50, 100);
#ctx.fillStyle = "blue";
#ctx.fill()


class Star(models.Model):
	x = models.IntegerField(default=0)
	y = models.IntegerField(default=0)
	r = models.IntegerField(default=0)
	n = models.IntegerField(default=5)


	'''function star(R, X, Y, N) {
            ctx.beginPath();
            ctx.moveTo(X + R, Y);
            for (var i = 1; i <= N * 2; i++) {
               if (i % 2 == 0) {
                  var theta = i * (Math.PI * 2) / (N * 2);
                  var x = X + (R * Math.cos(theta));
                  var y = Y + (R * Math.sin(theta));
               } else {
                  var theta = i * (Math.PI * 2) / (N * 2);
                  var x = X + ((R / 2) * Math.cos(theta));
                  var y = Y + ((R / 2) * Math.sin(theta));
               }
               ctx.lineTo(x, y);
            }
            ctx.closePath();
            ctx.fillStyle = "yellow";
            ctx.fill();
            ctx.fillStyle = "green";
            ctx.stroke();
         }
'''


class Rectangle(models.Model):
	x = models.IntegerField(default=0)
	y = models.IntegerField(default=0)
	width = models.IntegerField(default=0)
	height = models.IntegerField(default=0)
	paste = models.TextField(max_length=150, default="var x = 150;var y = 50;var width = 200;var height = 250;context.strokeRect(x, y, width, height);")
	filled = models.BooleanField(default=False)#canvas.fillRect(150, 50, 200, 250);
	clear = models.BooleanField(default=False)#canvas.clearRect(150, 50, 200, 250);

class Drawing(models.Model):
	name = models.CharField(max_length=140, default="Builder Owners Project")
	author = models.OneToOneField(Author, default=None, on_delete=models.PROTECT)
	created_date = models.DateTimeField(timezone.now)
	latest_change_date = models.DateTimeField(timezone.now)
	rectangles = models.ManyToManyField(Rectangle, default=None)
	init = models.TextField(max_length=20000, default="<script>function rectangle() {var canvas = document.getElementById('canvas');var context = canvas.getContext('2d');}</script>")

class Anon(models.Model):
	angel_numbers = models.ManyToManyField(AngelNumber, default=None)
	minecraft_servers = models.ManyToManyField(MinecraftServer, default=None)
	drawings = models.ManyToManyField(Drawing, default=None)
	storefronts = models.ManyToManyField(Storefront, default=None)
	saless = models.ManyToManyField(Sale, default=None)
	products = models.ManyToManyField(Price, related_name="anon_product", default=None)
	purchases = models.ManyToManyField(Price, related_name="anon_purchase", default=None)
	stripe_private_key = models.CharField(max_length=600, default='', null=True)
	stripe_webhook_secret = models.CharField(max_length=600, default='', null=True)
	#stripe_api_key = models.CharField(max_length=600, default='', null=True)
	stripe_api_secret = models.CharField(max_length=600, default='', null=True)
	home_page_density = models.ManyToManyField(Page_Density, default=None)
	username = models.OneToOneField(User, on_delete=models.CASCADE)
	email = models.EmailField(max_length=144, default='', null=True)
	anon_sort = models.IntegerField(choices=ANON_SORT_CHOICES, default=0)
	anon_sort_char = models.CharField(choices=ANON_SORT_CHOICES_CHAR, default="latest_change_date", max_length=180)
	dictionaries = models.ManyToManyField(Dictionary, default=None, related_name='dictionaries')
	sum_dictionaries = models.IntegerField(default=0)
	
	purchased_dictionaries = models.ManyToManyField(Dictionary, default=None, related_name='purchased_dictionaries')
	sum_purchased_dictionaries = models.IntegerField(default=0)
	applied_dictionaries = models.ManyToManyField(Dictionary_Source, default=None, related_name='applied_dictionaries')
	excluded_dic_authors = models.ManyToManyField(Author, default=None)
	sum_excluded_authors = models.IntegerField(default=0)

	dictionary_sort = models.IntegerField(choices=DICTIONARY_SORT_CHOICES, default=0)
	dictionary_sort_char = models.CharField(choices=DICTIONARY_SORT_CHOICES_CHAR, default="views", max_length=180)
	word_sort = models.IntegerField(choices=WORD_SORT_CHOICES, default=0)
	word_sort_char = models.CharField(choices=WORD_SORT_CHOICES_CHAR, default="viewcount", max_length=180)
	attribute_sort = models.IntegerField(choices=ATTRIBUTE_SORT_CHOICES, default=0)
	attribute_sort_char = models.CharField(choices=ATTRIBUTE_SORT_CHOICES_CHAR, default="the_attribute_itself", max_length=180)
	examples = models.ManyToManyField(Example, blank=True, default=None) # saved comments
	sum_examples = models.IntegerField(default=0)
	example_sort = models.IntegerField(choices=EXAMPLE_SORT_CHOICES, default=0)
	sponsor_sort = models.IntegerField(choices=SPONSOR_SORT_CHOICES, default=0)
	tasks = models.ManyToManyField(Task, default=None)
	sum_tasks = models.IntegerField(default=0)
	latest_change_date = models.DateTimeField(default=timezone.now)
	creation_date = models.DateTimeField(default=timezone.now)
	#playlists = models.ManyToManyField(Playlist)=
	sent_messages = models.ManyToManyField(Comment_Source, default=None, related_name='sent_messages')
	received_messages = models.ManyToManyField(Comment_Source, default=None, related_name='received_messages')
	posted_comments = models.ManyToManyField(Comment, default=None, related_name='posted_comments')
	sum_posted_comments = models.IntegerField(default=0)
	saved_comments = models.ManyToManyField(Comment, default=None, related_name='saved_comments')
	sum_saved_comments = models.IntegerField(default=0)
	reposting_comments = models.ManyToManyField(Comment, default=None, related_name='reposting_comments')
	reposting_comment_sources = models.ManyToManyField(Comment_Source, default=None, related_name='reposting_comment_sources')
	comment_sort = models.IntegerField(choices=COMMENT_SORT_CHOICES, default=0)
	comment_sort_char = models.CharField(choices=COMMENT_SORT_CHOICES_CHAR, default="latest_change_date", max_length=180)


	posts = models.ManyToManyField(Post, blank=True, default=None)
	sum_posts = models.IntegerField(default=0)
	post_sort = models.IntegerField(choices=POST_SORT_CHOICES, default=0)
	post_sort_char = models.CharField(choices=POST_SORT_CHOICES_CHAR, default="latest_change_date", max_length=180)
	
	spaces = models.ManyToManyField(Space, blank=True, default=None, related_name='spaces')
	sum_spaces = models.IntegerField(default=0)

	saved_spaces = models.ManyToManyField(Space, blank=True, default=None, related_name='saved_spaces')
	
	purchased_spaces = models.ManyToManyField(Space, blank=True, default=None, related_name='purchased_spaces')
	sum_purchased_spaces = models.IntegerField(default=0)
	space_sort = models.IntegerField(choices=SPACE_SORT_CHOICES, default=0)
	space_sort_char = models.CharField(choices=SPACE_SORT_CHOICES_CHAR, default="latest_change_date", max_length=180)

	created_votestyles = models.ManyToManyField(Votes, default=None, related_name='created_votestyles')
	sum_created_votestyles = models.IntegerField(default=0)
	saved_votestyles = models.ManyToManyField(Votes, default=None, related_name='saved_votestyles')
	applied_votestyles = models.ManyToManyField(Votes, default=None, related_name='applied_votestyles')
	excluded_votestyles = models.ManyToManyField(Votes, default=None, related_name='excluded_votestyles')

	past_votes = models.ManyToManyField(Votings, default=None, related_name='past_votes')
	sum_past_votes = models.IntegerField(default=0)
	search_urls = models.ManyToManyField(SearchURL, default=None)
	
	monero_wallet = models.CharField(max_length=200, default='')
	false_wallet = models.IntegerField(default=0)

	is_viewing = models.BooleanField(default=False)


	all_files = models.ManyToManyField(File, default=None, related_name="all_files")
	public_files = models.ManyToManyField(File, default=None, related_name="public_files")

	notifications = models.ManyToManyField(Notification, default=None)

	availabilities = models.ManyToManyField(Availability, default=None, related_name="availabilities")
	shared_with_availabilities = models.ManyToManyField(Availability, default=None, related_name="shared_with_availabilities")
	students = models.ManyToManyField(Author, default=None, related_name="students")
	student_of = models.ManyToManyField(Author, default=None, related_name="student_of")
	employees = models.ManyToManyField(Author, default=None, related_name="employees")
	employed_by = models.ManyToManyField(Author, default=None, related_name="employed_by")

	loans = models.ManyToManyField(Loan, default=None)


	def __unicode__(self):
		return unicode(self.username) or u''

import datetime
class UserViews(models.Model):
	anon = models.ForeignKey(Anon, default=None, on_delete=models.PROTECT)
	view_date = models.DateTimeField(default=timezone.now)
	page_view = models.CharField(max_length=200, default='')
	previous_view_id = models.CharField(max_length=144, default='')
	previous_page = models.CharField(max_length=200, default='')
	previous_view_date = models.DateTimeField(default=timezone.now)
	previous_view_time_between_pages = models.DurationField(default=datetime.timedelta(days=0, seconds=1))

class Pageviews(models.Model):
	page = models.CharField(max_length=200, default='')
	views = models.IntegerField(default=0)
	user_views = models.ManyToManyField(UserViews, default=None)
	translation = models.CharField(max_length=2, default='en')




