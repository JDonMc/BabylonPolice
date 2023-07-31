from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Post, Anon, Dictionary, Word

class Static_Sitemap(Sitemap):

    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['Bable:thanks', 'Bable:about', 'Bable:feedback', 'Bable:owner', 'Bable:landingpage', 'Bable:roadmap', 'Bable:tower_of_bable']

    def location(self, item):
        return reverse(item)




class Post_Sitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Post.objects.order_by('-latest_change_date')[0:1000]

    def location(self, obj):
        return reverse('Bable:tob_post', kwargs={'post': obj.id})

    def lastmod(self, obj): 
        return obj.latest_change_date


class Anon_Sitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Post.objects.order_by('-latest_change_date')[0:1000]

    def location(self, obj):
        return reverse('Bable:tob_post', kwargs={'post': obj.id})

    def lastmod(self, obj): 
        return obj.latest_change_date

class Dictionary_Sitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Dictionary.objects.order_by('-latest_change_date')[0:1000]

    def location(self, obj):
        return reverse('Bable:tob_dic', kwargs={'dictionary_id': obj.id})

    def lastmod(self, obj): 
        return obj.latest_change_date



class Word_Sitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Word.objects.order_by('-latest_change_date')[0:1000]

    def location(self, obj):
        return reverse('Bable:tob_word', kwargs={'word_id': obj.id})

    def lastmod(self, obj): 
        return obj.latest_change_date



