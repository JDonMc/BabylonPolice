# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User, UserManager
from django.db import models
from models import Dictionary, Example, Task, SpaceSource
# Register your models here.
class Anon(User):
	dictionaries = models.ManyToManyField(Dictionary, default=None)
	examples = models.ManyToManyField(Example, default=None) # saved comments
	tasks = models.ManyToManyField(Task, default=None)
	latest_change_date = models.DateTimeField(default=timezone.now)
	#playlists = models.ManyToManyField(Playlist)
	spaces = models.ManyToManyField(SpaceSource, default=None)

	objects = UserManager()