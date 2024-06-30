from django.contrib import admin

# Register your models here.
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer



from .models import *

class AngelNumberSerializer(serializers.ModelSerializer):
	class Meta:
		model = AngelNumber
		fields = ('digits', 'numbers', 'description',)

class AuthorSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Author
		fields =  ( 'username', )

class PostSerializer(WritableNestedModelSerializer):
	class Meta:
		model = Post
		fields = ('title', 'body', 'url2',)


class ExampleSerializer(WritableNestedModelSerializer):
	class Meta:
		model = Example
		fields = ('the_example_itself',)


class WordSerializer(WritableNestedModelSerializer):
	class Meta:
		model = Word
		fields = ('the_word_itself',)


class SponsorSerializer(WritableNestedModelSerializer):
	class Meta:
		model = Sponsor
		fields = ('the_sponsorship_phrase', 'img', 'url2', 'payperview', 'price_limit', 'allowable_expenditure', 'author')
