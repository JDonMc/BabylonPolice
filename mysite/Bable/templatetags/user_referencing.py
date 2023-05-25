import random
from django import template
from django.urls import reverse
from datetime import datetime
from Bable import models
import bleach

register = template.Library()

@register.filter(is_safe=True)
def usernames(value):
	return value.replace('/user/', 'https://www.babylonpolice.com/B/user/')


@register.filter(is_safe=True)
def spaces(value):
	return value.replace('/space/', 'https://www.babylonpolice.com/B/space/')
# register.filter('usernames', usernames) # can be used instead of decorator
# enter {% load user_referencing %}
# to incorporate into HTML
@register.filter(is_safe=True)
def subset(value, subset):
	counter = []*subset.length
	for val in value:
		for x in range(0, subset.length):
			if val == subset[x]:
				counter[x] = True
				break
	for x in range(0, subset.length):
		if not counter[x]:
			break
		if x == subset.length:
			return True
	if not value.count():
		return True
	return False





@register.filter(is_safe=True)
def sponsor(value, dictionaries):
	pricemax = 0
	top_sponsor = 0
	contained_dic = 0
	for dic in dictionaries:
		for word in dic.words.all():
			for spon in word.sponsors.all():
				if spon.price_limit > pricemax:
					pricemax = spon.price_limit
					top_sponsor = spon
					contained_dic = dic
	if not top_sponsor:
		if not contained_dic:
			value = value.replace('{}'.format(top_sponsor.the_sponsorship_phrase), '<a class=plain href="{}" onmouseover="dropdown("{}");" onmouseout="dropdown("{}");"><img src="{}" style="height: 4em; width: 4em">{}</a><div class=dropdown data="{}"style="display: none;">"{}"</div>'.format(reverse('Bable:clickthrough', kwargs={'author': 'replacewclickthrough', 'sponsor_id':top_sponsor.id}), top_sponsor.id, top_sponsor.img, top_sponsor.id, top_sponsor.id, top_sponsor.the_sponsorship_phrase, top_sponsor.the_sponsorship_phrase))
	return value

@register.filter(is_safe=True)
def clickthrough(value, author):
	value = value.replace('replacewclickthrough', '{}'.format(author))
	return value

# sponsors twist own your words (livingly) and twist it to their own, and you get paid for that.
# commenters choose the displayed images 

@register.filter(is_safe=True)
def safety_clean(value):
	return	bleach.clean(value)				


@register.filter(is_safe=True)
def safety_check(value):
	return bleach.clean(value, tags=['a', 'div', 'style', 'img', 'video'])

@register.filter(is_safe=True)
def nodic_word_up(value):
	if len(value) < 280:
		exclude = ''
		wordlen = -1
		word2len = -1
		word3len = -1
		words = models.Word.objects.all()
		nodic_words = words.filter(home_dictionary=None).order_by('the_word_itself')
		for word in nodic_words:
			if word.the_word_itself in value.split(" "):
				wordlen += 1
				if word.the_word_itself not in exclude:
					replaced = False
					wordsponsor = word.random_sponsor()
					if wordsponsor.url:
						wordsponsordiv = '<div><a href="{}" ><p style="color: white; position: absolute; top: 3em; background: rgba(0,0,0,0.5); width: -webkit-fill-available;">'.format(reverse('Bable:clickthrough', kwargs={'author':'test', 'sponsor_id':wordsponsor.id})) + wordsponsor.the_sponsorship_phrase + '</p><img style="height: 4em; width: 4em; position: absolute;" src="' + wordsponsor.img + '" >' + '</a></div>'
					else:
						wordsponsordiv = '<div><a href="https://www.babylonpolice.com" ><p style="color: white; position: absolute; top: 3em; background: rgba(0,0,0,0.5); width: -webkit-fill-available;">' + wordsponsor.the_sponsorship_phrase + '</p><img style="height: 4em; width: 4em; position: absolute;" src="' + wordsponsor.img + '" ></a></div>'
					attribute_div1 = '<div class=dropdown-menu-1><style>.dropdown-menu-1 { opacity: 0; display: none; } .inner-' + str(word.id) + '-' + str(wordlen) + ':hover, .inner-' + str(word.id) + '-' + str(wordlen) + '.active, .dropdown-menu-1:hover, .dropdown-menu-1.active { opacity: 1; display: block; transform: translateY(0px); pointer-events: auto;}</style>'
					for att1 in word.attributes.all():
						for def1 in att1.definitions.all():
							attribute_div1 += '<div>'+def1.the_definition_itself+'</div>'
					attribute_div1 += wordsponsordiv + '</div>'
					value = value.replace('{}'.format(word.the_word_itself), '<div class="inner-{}-{} inner" style="cursor: pointer; width: fit-content; display: inline-block;"><a class="plain1 overlay" style="color: yellow;" href="{}">{}</a><script>$("a.plain1").one("click", function() {{if( $(this).attr("href") > 0) {{$(this).attr("data", $(this).attr("href")); $(this).attr("href", "");$(this).addClass("active");$(".dropdown-menu-1").addClass("active");}} else {{$(this).attr("href", $(this).attr("data"));$(this).removeClass("active");$(".dropdown-menu-1").removeClass("active");}};$(".dropdown-menu-1").addClass("active");return false;}});</script></div>'.format(str(word.id), str(wordlen), reverse('Bable:tob_word', kwargs={'word_id':word.id}), word.the_word_itself+attribute_div1))
					exclude += '<div class="inner-{}-{} inner" style="cursor: pointer; width: fit-content; display: inline-block;"><a class="plain1 overlay" style="color: yellow;" href="{}">{}</a></div>'.format(str(word.id), str(wordlen), reverse('Bable:tob_word', kwargs={'word_id':word.id}), word.the_word_itself+attribute_div1)
			exclude += '<a class=plain href="{}">{}</a>'.format(reverse('Bable:tob_word', kwargs={'word_id':word.id}), word.the_word_itself)

									

	return value



@register.filter(is_safe=True)
def word_up(value, dictionaries):
	if len(value) < 280:
		exclude = ''
		wordlen = -1
		for dic in dictionaries.all()[:3]:
			for word in dic.words.all().order_by('the_word_itself')[:30]:
				if word.the_word_itself in value.split(" "):
					wordlen += 1
					if word.the_word_itself not in exclude:
						replaced = False
						wordsponsor = word.random_sponsor()
						if wordsponsor.url:
							wordsponsordiv = '<div><a href="{}" ><p style="color: white; position: absolute; top: 3em; background: rgba(0,0,0,0.5); width: -webkit-fill-available;">'.format(reverse('Bable:clickthrough', kwargs={'author':word.author.username, 'sponsor_id':wordsponsor.id})) + wordsponsor.the_sponsorship_phrase + '</p><img style="height: 4em; width: 4em; position: absolute;" src="' + wordsponsor.img + '" >' + '</a></div>'
						else:
							wordsponsordiv = '<div><a href="https://www.babylonpolice.com" ><p style="color: white; position: absolute; top: 3em; background: rgba(0,0,0,0.5); width: -webkit-fill-available;">' + wordsponsor.the_sponsorship_phrase + '</p><img style="height: 4em; width: 4em; position: absolute;" src="' + wordsponsor.img + '" ></a></div>'
						attribute_div1 = '<div class=dropdown-menu-1><style>.dropdown-menu-1 { opacity: 0; display: none; } .inner-' + str(word.id) + '-' + str(wordlen) + ':hover, .inner-' + str(word.id) + '-' + str(wordlen) + '.active, .dropdown-menu-1:hover, .dropdown-menu-1.active { opacity: 1; display: block; transform: translateY(0px); pointer-events: auto;}</style>'
						for att1 in word.attributes.all():
							for def1 in att1.definitions.all():
								attribute_div1 += '<div>'+def1.the_definition_itself+'</div>'
						attribute_div1 += wordsponsordiv + '</div>'
						value = value.replace('{}'.format(word.the_word_itself), '<div class="inner-{}-{} inner" style="cursor: pointer; width: fit-content; display: inline-block;"><a class="plain1 overlay" style="color: yellow;" href="{}">{}</a><script>$("a.plain1").one("click", function() {{if( $(this).attr("href") > 0) {{$(this).attr("data", $(this).attr("href")); $(this).attr("href", "");$(this).addClass("active");$(".dropdown-menu-1").addClass("active");}} else {{$(this).attr("href", $(this).attr("data"));$(this).removeClass("active");$(".dropdown-menu-1").removeClass("active");}};$(".dropdown-menu-1").addClass("active");return false;}});</script></div>'.format(str(word.id), str(wordlen), reverse('Bable:tob_users_dic_word_count', kwargs={'user':dic.author.username, 'dictionary':dic.the_dictionary_itself, 'word':word.the_word_itself, 'count':0}), word.the_word_itself+attribute_div1))
						exclude += '<div class="inner-{}-{} inner" style="cursor: pointer; width: fit-content; display: inline-block;"><a class="plain1 overlay" style="color: yellow;" href="{}">{}</a></div>'.format(str(word.id), str(wordlen), reverse('Bable:tob_users_dic_word_count', kwargs={'user':dic.author.username, 'dictionary':dic.the_dictionary_itself, 'word':word.the_word_itself, 'count':0}), word.the_word_itself+attribute_div1)
				exclude += '<a class=plain href="{}">{}</a>'.format(reverse('Bable:tob_users_dic_word_count', kwargs={'user':dic.author.username, 'dictionary':dic.the_dictionary_itself, 'word':word.the_word_itself, 'count':0}), word.the_word_itself)


	return value


@register.filter(is_safe=True)
def prereq_dics_word_up(value, dictionaries):
	for dic in dictionaries:
		if '/'+dic.the_dictionary_itself+'/' in value:
			print(dic.the_dictionary_itself)
			for prerequisite in dic.prerequisite_dics.all():
				if '/'+dic.the_dictionary_itself+'/'+prerequisite.the_dictionary_itself+'/' in value:
					for word in prerequisite.to_full().words.all():
						if '/'+dic.the_dictionary_itself+'/'+prerequisite.the_dictionary_itself+'/'+word.the_word_itself in value:
							value.replace('/{}/{}/{}'.format(dic.the_dictionary_itself, prerequisite.the_dictionary_itself, word.the_word_itself), '<a class=plain href="{}">{}</a>'.format(reverse('Bable:tob_users_dic_word_count', kwargs={'user':prerequisite.author.username, 'dictionary':prerequisite.the_dictionary_itself, 'word':word.the_word_itself, 'count':0}), word.the_word_itself))
	return value


@register.filter(is_safe=True)
def dics_word(value, dictionaries):
	for dic in dictionaries:
		if '/'+dic.the_dictionary_itself+'/' in value.split(" "):
			for word in dic.words.all():
				if '/'+dic.the_dictionary_itself+'/'+word.the_word_itself in value.split(" "):
					value.replace('/{}/{}'.format(dic.the_dictionary_itself, word.the_word_itself), '<a class=plain href="{}">{}</a>'.format(reverse('Bable:tob_users_dic_word_count', kwargs={'user':dic.author.username, 'dictionary':dic.the_dictionary_itself, 'word':word.the_word_itself, 'count':0}), word.the_word_itself))
	
	return value


from django.utils.safestring import mark_safe


@register.filter(is_safe=True)
def fontypes(value, words):
	for word in words:
		if word.the_word_itself in value:
			replace_to = '<a class="plain{} plain" href="{}" data-text="{}"style="font-style: url(\'{}\'); font-size: {}em; position: relative; display: inline-block;">{}</a><style>{}</style>'.format(word.id, reverse('Bable:tob_users_dic_word_count', kwargs={'user':word.home_dictionary.to_full().author.username, 'dictionary':word.home_dictionary.to_full().the_dictionary_itself, 'word':word.the_word_itself, 'count':0}), word.the_word_itself, word.fontstyle, word.fontsize, word.the_word_itself, word.fontype)
			value = value.replace('{}'.format(word.the_word_itself), replace_to)
			print(value)
	return value


@register.filter(is_safe=True)
def directive_jump_up(value, dictionaries):
	for dic in dictionaries:
		for word in dic.words.all():
			for pointforward in dic.words.all():
				if word.id + '+' + pointforward.id + '@' + '%H:%M:%S' + '/' in value:
					start = value.index(pointforward.id + '@') + len(pointforward.id + '@')
					color = datetime.strptime(value[start:], '%H')
					if color == "01": # not sure if string or digits
						color = "red"
					if color == "02":
						color = "blue"
					if color == "03":
						color = "green"
					delay = datetime.strptime(value[start+2:], '%M:%S')
					value = value.replace('{}'.format(pointforward.the_word_itself), '<div class=delay style:"transition-delay = {}; color = {};">{}</div>'.format(delay, color, pointfrward.the_word_itself))
	return value



