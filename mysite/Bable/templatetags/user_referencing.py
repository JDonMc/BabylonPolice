import random
from django import template
from django.urls import reverse
from datetime import datetime
from Bable import models
import nh3

register = template.Library()

@register.filter(is_safe=True)
def usernames(value):
	return value.replace('/username/', 'https://www.babylonpolice.com/B/user/')


@register.filter(is_safe=True)
def stripwww(value):
	return value.replace('www.', '')


@register.filter(is_safe=True)
def spaces(value):
	return value.replace('/spacename/', 'https://www.babylonpolice.com/B/space/')
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
def random_int(a, b=None):
    if b is None:
        b = a
        a = 0
    return random.randint(a, b)

@register.filter(is_safe=True)
def left_over(a, b):
    return a%b



@register.filter(is_safe=True)
def sponsor(value, dictionaries):
	pricemax = 0
	top_sponsor = 0
	contained_dic = 0
	if type(dictionaries) == list:
		for dic in dictionaries:
			for word in dic.words.all():
				for spon in word.sponsors.all():
					if spon.price_limit > pricemax:
						pricemax = spon.price_limit
						top_sponsor = spon
						contained_dic = dic
	else:
		top_sponsor = models.Sponsor.objects.order_by('-price_limit').first()

	if top_sponsor:
		if not contained_dic:
			replacement = '<form action="{}" method=POST onmouseover="dropdown("{}");" onmouseout="dropdown("{}");"><input class=csrf type=text><input type=hidden value="{}" readonly><input type=hidden value="{}" readonly><button type=submit><img src="{}" style="height: 4em; width: 4em; float:right;"></button></form><img src="{}" style="height: 4em; width: 4em">{}</a><div class=dropdown data="{}"style="display: none;">"{}"</div>'.format(reverse('Bable:clickthrough'),'replacewclickthrough', top_sponsor.id),
			value = value.replace('{}'.format(top_sponsor.the_sponsorship_phrase),  replacement)
	return value

@register.filter(is_safe=True)
def clickthrough(value, author):
	value = value.replace('replacewclickthrough', '{}'.format(author))
	return value

# sponsors twist own your words (livingly) and twist it to their own, and you get paid for that.
# commenters choose the displayed images 

@register.filter(is_safe=True)
def safety_clean(value):
	return	nh3.clean(value)				


@register.filter(is_safe=True)
def safety_check(value):
	return nh3.clean(value)

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
						wordsponsordiv = '<div><form action="{}" method=POST onmouseover="dropdown("{}");" onmouseout="dropdown("{}");"><input class=csrf type=text><input type=hidden value="{}" readonly><input type=hidden value="{}" readonly><button type=submit><img src="{}" style="height: 4em; width: 4em; float:right;"></button></form> <p style="color: white; position: absolute; top: 3em; background: rgba(0,0,0,0.5); width: -webkit-fill-available;">'.format(reverse('Bable:clickthrough'), 'test', wordsponsor.id) + wordsponsor.the_sponsorship_phrase + '</p><img style="height: 4em; width: 4em; position: absolute;" src="' + wordsponsor.img + '" >' + '</a></div>'
					else:
						wordsponsordiv = '<div><a href="https://www.babylonpolice.com" ><p style="color: white; position: absolute; top: 3em; background: rgba(0,0,0,0.5); width: -webkit-fill-available;">' + wordsponsor.the_sponsorship_phrase + '</p><img style="height: 4em; width: 4em; position: absolute;" src="' + wordsponsor.img + '" ></a></div>'
					attribute_div1 = '<div class=dropdown-menu-1><style>.dropdown-menu-1 { opacity: 0; display: none; } .inner-' + str(word.id) + '-' + str(wordlen) + ':hover, .inner-' + str(word.id) + '-' + str(wordlen) + '.active, .dropdown-menu-1:hover, .dropdown-menu-1.active { opacity: 1; display: block; transform: translateY(0px); pointer-events: auto;}</style>'
					for att1 in word.attributes.all():
						for def1 in att1.definitions.all():
							attribute_div1 += '<div>'+def1.the_definition_itself+'</div>'
					attribute_div1 += wordsponsordiv + '</div>'
					value = value.replace('{}'.format(word.the_word_itself), '&nbsp;<div class="inner-{}-{} inner" style="cursor: pointer; width: fit-content; display: inline-block;"><a class="plain1 overlay" style="color: yellow;" href="{}">{}</a><script>$("a.plain1").one("click", function() {{if( $(this).attr("href") > 0) {{$(this).attr("data", $(this).attr("href")); $(this).attr("href", "");$(this).addClass("active");$(".dropdown-menu-1").addClass("active");}} else {{$(this).attr("href", $(this).attr("data"));$(this).removeClass("active");$(".dropdown-menu-1").removeClass("active");}};$(".dropdown-menu-1").addClass("active");return false;}});</script></div>'.format(str(word.id), str(wordlen), reverse('Bable:tob_word', kwargs={'word_id':word.id}), word.the_word_itself+attribute_div1))
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
						if wordsponsor.url2:
							wordsponsordiv = '<div><form action="{}" method=POST><input class=csrf type=text><input type=hidden value="{}" readonly><input type=hidden value="{}" readonly><button type=submit><img src="{}" style="height: 4em; width: 4em; float:right;"></button></form><p style="color: white; position: absolute; top: 3em; background: rgba(0,0,0,0.5); width: -webkit-fill-available;">'.format(reverse('Bable:clickthrough'), word.author.username, wordsponsor.id, wordsponsor.img) + wordsponsor.the_sponsorship_phrase + '</p></div>'
						else:
							wordsponsordiv = '<div><a href="https://www.babylonpolice.com" ><p style="color: white; position: absolute; top: 3em; background: rgba(0,0,0,0.5); width: -webkit-fill-available;">' + wordsponsor.the_sponsorship_phrase + '</p><img style="height: 4em; width: 4em; position: absolute;" src="' + wordsponsor.img + '" ></a></div>'
						attribute_div1 = '<div class=dropdown-menu-1><style>.dropdown-menu-1 { opacity: 0; display: none; } .inner-' + str(word.id) + '-' + str(wordlen) + ':hover, .inner-' + str(word.id) + '-' + str(wordlen) + '.active, .dropdown-menu-1:hover, .dropdown-menu-1.active { opacity: 1; display: block; transform: translateY(0px); pointer-events: auto;}</style>'
						for att1 in word.attributes.all():
							for def1 in att1.definitions.all():
								attribute_div1 += '<div>'+def1.the_definition_itself+'</div>'
						attribute_div1 += wordsponsordiv + '</div>'
						value = value.replace('{}'.format(word.the_word_itself), '&nbsp;<div class="inner-{}-{} inner" style="cursor: pointer; width: fit-content; display: inline-block;"><a class="plain1 overlay" style="color: yellow;" href="{}">{}</a><script>$("a.plain1").one("click", function() {{if( $(this).attr("href") > 0) {{$(this).attr("data", $(this).attr("href")); $(this).attr("href", "");$(this).addClass("active");$(".dropdown-menu-1").addClass("active");}} else {{$(this).attr("href", $(this).attr("data"));$(this).removeClass("active");$(".dropdown-menu-1").removeClass("active");}};$(".dropdown-menu-1").addClass("active");return false;}});</script></div>'.format(str(word.id), str(wordlen), reverse('Bable:tob_users_dic_word_count', kwargs={'user':dic.author.username, 'dictionary':dic.the_dictionary_itself, 'word':word.the_word_itself, 'count':0}), word.the_word_itself+attribute_div1))
						exclude += '<div class="inner-{}-{} inner" style="cursor: pointer; width: fit-content; display: inline-block;"><a class="plain1 overlay" style="color: yellow;" href="{}">{}</a></div>'.format(str(word.id), str(wordlen), reverse('Bable:tob_users_dic_word_count', kwargs={'user':dic.author.username, 'dictionary':dic.the_dictionary_itself, 'word':word.the_word_itself, 'count':0}), word.the_word_itself+attribute_div1)
				exclude += '<a class=plain href="{}">{}</a>'.format(reverse('Bable:tob_users_dic_word_count', kwargs={'user':dic.author.username, 'dictionary':dic.the_dictionary_itself, 'word':word.the_word_itself, 'count':0}), word.the_word_itself)


	return value


@register.filter(is_safe=True)
def prereq_dics_word_up(value, dictionaries):
	for dic in dictionaries:
		for prerequisite in dic.prerequisite_dics.all():
			for word in prerequisite.to_full().words.all():
				if '/'+dic.the_dictionary_itself+'/'+prerequisite.the_dictionary_itself+'/'+word.the_word_itself in value.split(" "):
					value.replace('/{}/{}/{}'.format(dic.the_dictionary_itself, prerequisite.the_dictionary_itself, word.the_word_itself), '<a class=plain href="{}">{}</a>'.format(reverse('Bable:tob_users_dic_word_count', kwargs={'user':prerequisite.author.username, 'dictionary':prerequisite.the_dictionary_itself, 'word':word.the_word_itself, 'count':0}), word.the_word_itself))
	return value


@register.filter(is_safe=True)
def dics_word(value, dictionaries):
	for dic in dictionaries:
		for word in dic.words.all():
			if '/'+dic.the_dictionary_itself+'/'+word.the_word_itself in value.split(" "):
				value.replace('/{}/{}'.format(dic.the_dictionary_itself, word.the_word_itself), '<a class=plain href="{}">{}</a>'.format(reverse('Bable:tob_users_dic_word_count', kwargs={'user':dic.author.username, 'dictionary':dic.the_dictionary_itself, 'word':word.the_word_itself, 'count':0}), word.the_word_itself))
	
	return value


from django.utils.safestring import mark_safe


@register.filter(is_safe=True)
def fontypes(value, words):
	wordlen = -1
	for word in words:
		if word.the_word_itself in value.split(" "):
			wordlen += 1
			wordsponsor = word.sponsors.order_by('-price_limit').first()
			wordsponsordiv = ''
			if wordsponsor:
				if wordsponsor.url2:
					wordsponsordiv += '<div><form action="{}" method=POST><input class=csrf type=text><input type=hidden value="{}" readonly><input type=hidden value="{}" readonly><button type=submit><img src="{}" style="height: 4em; width: 4em; float:right;"></button></form><p style="z-index: 1; color: white; top: 3em; background: rgba(0,0,0,0.5); width: -webkit-fill-available;">'.format(reverse('Bable:clickthrough'),word.author.username, wordsponsor.id, wordsponsor.img) + wordsponsor.the_sponsorship_phrase + '</p><img style="height: 4em; width: 4em; position: absolute;" src="' + wordsponsor.img + '" >' + '</a></div>'
				else:
					wordsponsordiv += '<div><a href="https://www.predictionary.us" ><p style="color: white; top: 3em; background: rgba(0,0,0,0.5); width: -webkit-fill-available;">' + wordsponsor.the_sponsorship_phrase + '</p><img style="height: 4em; width: 4em; position: absolute;" src="' + wordsponsor.img + '" ></a></div>'
			attribute_div1 = '<div class=dropdown-menu-1><style>.dropdown-menu-1 { position: absolute; background-color: green; width: fit-content; opacity: 0; display: none; } .inner-' + str(word.id) + '-' + str(wordlen) + ':hover, .inner-' + str(word.id) + '-' + str(wordlen) + '.active, .dropdown-menu-1:hover, .dropdown-menu-1.active { opacity: 1; display: block; transform: translateY(0px); pointer-events: auto;}</style>'
			for att1 in word.attributes.order_by('?'):
				for def1 in att1.definitions.order_by('?'):
					attribute_div1 += '<div style="width: 16em;">'+def1.the_definition_itself+'</div>'
			attribute_div1 += wordsponsordiv + '</div>'


			
			#replace_to = '<a class="plain{} plain" href="{}" data-text="{}" style="font-style: url(\'{}\'); font-size: {}em; position: relative; display: inline-block;">{}</a><style>{}</style>'.format(word.id, reverse('Bable:tob_users_dic_word_count', kwargs={'user':word.home_dictionary.to_full().author.username, 'dictionary':word.home_dictionary.to_full().the_dictionary_itself, 'word':word.the_word_itself, 'count':0}), word.the_word_itself, word.fontstyle, word.fontsize, word.the_word_itself, word.fontype)
			
			replace_to = '&nbsp;<div class="inner-{}-{} inner" style="cursor: pointer; width: fit-content; display: inline-block;"><a class="plain{} plain overlay" data-text="{}" style="color: yellow; font-style: url(\'{}\'); font-size: {}em; position: relative; display: inline-block;" href="{}">{}</a><style>{} p {{display: inline-block;}}</style><script>$("a.plain{}").one("click", function() {{if( $(this).attr("href") > 0) {{$(this).attr("data", $(this).attr("href")); $(this).attr("href", "");$(this).addClass("active");$(".dropdown-menu-1").addClass("active");}} else {{$(this).attr("href", $(this).attr("data"));$(this).removeClass("active");$(".dropdown-menu-1").removeClass("active");}};$(".dropdown-menu-1").addClass("active");return false;}});</script></div>{}'.format(str(word.id), str(wordlen), word.id, word.the_word_itself, word.fontstyle, word.fontsize, reverse('Bable:tob_word', kwargs={'word_id':word.id}), word.the_word_itself, word.fontype, word.id, attribute_div1)

			value = value.replace('{}'.format(word.the_word_itself), replace_to)
			print(value)
	return value


@register.filter(is_safe=True)
def fontype(value, word):
	wordlen = -1
	if word.the_word_itself in value:
		wordlen += 1
		wordsponsor = word.sponsors.order_by('-price_limit').first()
		wordsponsordiv = ''
		if wordsponsor:
			if wordsponsor.url2:
				wordsponsordiv += '<div><form action="{}" method=POST><input class=csrf type=text><input type=hidden value="{}" readonly><input type=hidden value="{}" readonly><button type=submit><img src="{}" style="height: 4em; width: 4em; float:right;"></button></form><p style="z-index: 1; color: white; top: 3em; background: rgba(0,0,0,0.5); width: -webkit-fill-available;">'.format(reverse('Bable:clickthrough'), word.author.username, wordsponsor.id) + wordsponsor.the_sponsorship_phrase + '</p><img style="height: 4em; width: 4em; position: absolute;" src="' + wordsponsor.img + '" >' + '</div>'
			else:
				wordsponsordiv += '<div><a href="https://www.predictionary.us" ><p style="color: white; top: 3em; background: rgba(0,0,0,0.5); width: -webkit-fill-available;">' + wordsponsor.the_sponsorship_phrase + '</p><img style="height: 4em; width: 4em; position: absolute;" src="' + wordsponsor.img + '" ></a></div>'
		attribute_div1 = '<div class=dropdown-menu-1><style>.dropdown-menu-1 { position: absolute; background-color: green; width: fit-content; opacity: 0; display: none; } .inner-' + str(word.id) + '-' + str(wordlen) + ':hover, .inner-' + str(word.id) + '-' + str(wordlen) + '.active, .dropdown-menu-1:hover, .dropdown-menu-1.active { opacity: 1; display: block; transform: translateY(0px); pointer-events: auto;}</style>'
		for att1 in word.attributes.order_by('?'):
			for def1 in att1.definitions.order_by('?'):
				attribute_div1 += '<div style="width: 16em;">'+def1.the_definition_itself+'</div>'
		attribute_div1 += wordsponsordiv + '</div>'


		
		#replace_to = '<a class="plain{} plain" href="{}" data-text="{}" style="font-style: url(\'{}\'); font-size: {}em; position: relative; display: inline-block;">{}</a><style>{}</style>'.format(word.id, reverse('Bable:tob_users_dic_word_count', kwargs={'user':word.home_dictionary.to_full().author.username, 'dictionary':word.home_dictionary.to_full().the_dictionary_itself, 'word':word.the_word_itself, 'count':0}), word.the_word_itself, word.fontstyle, word.fontsize, word.the_word_itself, word.fontype)
		
		replace_to = '&nbsp;<div class="inner-{}-{} inner" style="cursor: pointer; width: fit-content; display: inline-block;"><a class="plain{} plain overlay" data-text="{}" style="color: yellow; font-style: url(\'{}\'); font-size: {}em; position: relative; display: inline-block;" href="{}">{}</a><style>{} p {{display: inline-block;}}</style><script>$("a.plain{}").one("click", function() {{if( $(this).attr("href") > 0) {{$(this).attr("data", $(this).attr("href")); $(this).attr("href", "");$(this).addClass("active");$(".dropdown-menu-1").addClass("active");}} else {{$(this).attr("href", $(this).attr("data"));$(this).removeClass("active");$(".dropdown-menu-1").removeClass("active");}};$(".dropdown-menu-1").addClass("active");return false;}});</script></div>{}'.format(str(word.id), str(wordlen), word.id, word.the_word_itself, word.fontstyle, word.fontsize, reverse('Bable:tob_word', kwargs={'word_id':word.id}), word.the_word_itself, word.fontype, word.id, attribute_div1)

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



