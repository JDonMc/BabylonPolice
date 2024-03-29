# Copyright Aden Handasyde 2019
from django.conf.urls import include
from django.urls import re_path as url
from . import views
from . import models
from django.contrib import admin
from django.urls import path

# ^^^^ Use for cleaning up dodgy datatables

from rest_framework import routers
# ^^^^ Use for cleaning up dodgy datatables

# Each has a sort
# Needs a page-number
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt import views as jwt_views
app_name='Bable'
# url(r'^admin/', admin.site.urls),
router = routers.DefaultRouter()
router.register(r'author', views.AuthorViewSet)
#router.register(r'post', views.PostViewSet)
	
# Each has a sort
# Needs a page-number
urlpatterns = [
	path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
	path('i18n/', include('django.conf.urls.i18n')),
	url(r'^examples/', views.ListCreateExampleAPIView.as_view()),
	url(r'^posts/', views.ListCreatePostAPIView.as_view()),
	url(r'^words/', views.ListCreateWordAPIView.as_view()),
	url(r'^sponsor/', views.ListCreateSponsorAPIView.as_view()),
	#url(r'^author/retrieve_by_username/(?P<username>\w+)', views.getByUsername, name='author_username'),
	#path('docs/', include_docs_urls(title='Todo Api')),
	#path('api/v1/todo/', include("todo.urls")),

	#path('stream/', views.stream, name='stream'),
	#path('stream_unseen/', views.stream_unseen, name='stream_unseen'),
	path('api/token', obtain_auth_token, name="auth_token"),
	path('api/jwt/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/jwt/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('checkout/<int:pk>', views.CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
	path('keyup/<int:pk>/<int:post_id>', views.KeyupCheckoutSessionView.as_view(), name='keyup-checkout-session'),

	# url(r'^admin/', admin.site.urls),
	url(r'^logout/$', views.logout_user, name='logout_user'),
	url(r'^sign_wallet/$', views.sign_wallet, name='sign_wallet'),
	url(r'^autocomplete_votestyles/$', views.autocomplete_votestyles, name='autocomplete_votestyles'),
	url(r'^grabvoteid/$', views.grabvoteid, name='grabvoteid'),
	#url(r'^gensim_test/$', views.gensim_test, name='gensim_test'),
	url(r'^create_product_w_price/(?P<post_id>[\w-]+)/$', views.create_product_w_price, name='create_product_w_price'),
	url(r'^login/$', views.login_view, name='login_view'),
	url(r'^owner/$', views.owner, name='owner'),
	url(r'^feedback/$', views.feedback, name='feedback'),
	url(r'^create_feedback/$', views.create_feedback, name='create_feedback'),
	url(r'^thanks/$', views.thanks, name='thanks'),
	url(r'^about/$', views.about, name='about'),
	url(r'^management/$', views.management, name='management'),
	url(r'^register/$', views.register_view, name='register_view'),
	url(r'^index/$', views.tower_of_bable, name='tower_of_bable'),
	url(r'^buy_credits/coinbase/$', views.home_view, name='home_view'),
	url(r'^landingpage/$', views.landingpage, name='landingpage'),
	url(r'^change_password/$', views.change_password, name='change_password'),
	url(r'^search/count/(?P<count>[\w-]+)/$', views.search, name='search'),
	url(r'^annotate_url/(?P<search_url_id>[\w-]+)/$', views.annotate_url, name='annotate_url'),
	url(r'^annotate_url_delete/(?P<search_url_id>[\w-]+)/$', views.delete_annotation_url, name='delete_annotation_url'),
	url(r'^annotate_url_post_comment/(?P<search_url_id>[\w-]+)/$', views.annotate_url_post_comment, name='annotate_url_post_comment'),
	url(r'^annotate_url_post_comment_location/(?P<search_url_id>[\w-]+)/(?P<location_id>[\w-]+)/$', views.annotate_url_post_comment_location, name='annotate_url_post_comment_location'),
	url(r'^annotate_url_comment_delete/(?P<search_url_id>[\w-]+)/(?P<comment_id>[\w-]+)/$', views.annotate_url_comment_delete, name='annotate_url_comment_delete'),
	url(r'^annotate_url_post_edits/(?P<search_url_id>[\w-]+)/$', views.annotate_url_post_edits, name='annotate_url_post_edits'),
	url(r'^index/count/(?P<count>[\w-]+)/$', views.tower_of_bable_count, name='tower_of_bable_count'),
	url(r'^index/time/$', views.tower_time, name='tower_time'),
	url(r'^spaces/$', views.tob_view_spaces, name='tob_view_spaces'),
	url(r'^spaces/count/(?P<count>[\w-]+)/$', views.tob_view_spaces_count, name='tob_view_spaces_count'),
	url(r'^space/(?P<space>[\w-]+)/count/(?P<count>[\w-]+)/$', views.tob_space_view_count, name='tob_space_view_count'),
	url(r'^space/(?P<space>[\w-]+)/$', views.tob_space_view, name='tob_space_view'),
	url(r'^space/(?P<space>[\w-]+)/post/(?P<post>[\w-]+)/count/(?P<count>[\w-]+)/$', views.tob_spaces_post, name='tob_spaces_post'),
	url(r'^space/(?P<space>[\w-]+)/post/(?P<post>[\w-]+)/comment/(?P<comment>[\w-]+)/$', views.tob_spaces_posts_comment, name='tob_spaces_posts_comment'),
	url(r'^users/$', views.tob_view_users, name='tob_view_users'),
	url(r'^users/count/(?P<count>[\w-]+)/$', views.tob_view_users_count, name='tob_view_users_count'),
	url(r'^change_dictionary/sort/(?P<sort>[\w-]+)/$', views.change_dictionary_sort, name='change_dictionary_sort'),
	url(r'^change_attribute/sort/(?P<sort>[\w-]+)/$', views.change_attribute_sort, name='change_attribute_sort'),
	url(r'^change_anon/sort/(?P<sort>[\w-]+)/$', views.change_anon_sort, name='change_anon_sort'),
	url(r'^change_anon_sort_char/$', views.change_anon_sort_char, name='change_anon_sort_char'),
	url(r'^change_space_sort_char/$', views.change_space_sort_char, name='change_space_sort_char'),
	url(r'^change_dic_sort_char/$', views.change_dic_sort_char, name='change_dic_sort_char'),
	url(r'^change_word_sort_char/$', views.change_word_sort_char, name='change_word_sort_char'),
	url(r'^change_attribute_sort_char/$', views.change_attribute_sort_char, name='change_attribute_sort_char'),
	url(r'^change_comment/sort/(?P<sort>[\w-]+)/$', views.change_comment_sort, name='change_comment_sort'),
	url(r'^change_word/sort/(?P<sort>[\w-]+)/$', views.change_word_sort, name='change_word_sort'),
	url(r'^change_post/sort/(?P<sort>[\w-]+)/$', views.change_post_sort, name='change_post_sort'),
	url(r'^change_post_sort_char/$', views.change_post_sort_char, name='change_post_sort_char'),
	url(r'^change_example/sort/(?P<sort>[\w-]+)/$', views.change_example_sort, name='change_example_sort'),
	url(r'^user/(?P<user>[\w-]+)/$', views.tob_user_view, name='tob_user_view'),
	url(r'^user/(?P<user>[\w-]+)/count/(?P<count>[\w-]+)/$', views.tob_user_view_count, name='tob_user_view_count'),
	url(r'^user/(?P<user>[\w-]+)/spaces/count/(?P<count>[\w-]+)/$', views.tob_users_spaces, name='tob_users_spaces'),
	url(r'^user/(?P<user>[\w-]+)/sponsor/(?P<sponsor>[\w-]+)/$', views.tob_users_sponsor, name='tob_users_sponsor'),
	url(r'^user/(?P<user>[\w-]+)/sponsors/count/(?P<count>[\w-]+)/$', views.tob_users_sponsors, name='tob_users_sponsors'),
	url(r'^user/(?P<user>[\w-]+)/space/(?P<space_id>[\w-]+)/count/(?P<count>[\w-]+)/$', views.tob_users_space, name='tob_users_space'),
	url(r'^user/(?P<user>[\w-]+)/space/(?P<space_id>[\w-]+)/sponsor/(?P<sponsor>[\w-]+)/$', views.tob_users_spaces_sponsor, name='tob_users_spaces_sponsor'),
	url(r'^user/(?P<user>[\w-]+)/space/(?P<space_id>[\w-]+)/post/(?P<post_id>[\w-]+)/$', views.tob_users_spaces_post, name='tob_users_spaces_post'),
	url(r'^user/(?P<user>[\w-]+)/vote/(?P<vote>[\w-]+)/$', views.tob_users_vote, name='tob_users_vote'),
	url(r'^user/(?P<user>[\w-]+)/votes/count/(?P<count>[\w-]+)/$', views.tob_users_votes, name='tob_users_votes'),
	url(r'^user/(?P<user>[\w-]+)/space/(?P<space>[\w-]+)/post/(?P<post>[\w-]+)/count/(?P<count>[\w-]+)/$', views.tob_users_spaces_post_count, name='tob_users_spaces_post_count'),
	url(r'^user/(?P<user>[\w-]+)/space/(?P<space>[\w-]+)/post/(?P<post>[\w-]+)/comment/(?P<comment>[\w-]+)/$', views.tob_users_spaces_post_comment, name='tob_users_spaces_post_comment'),
	url(r'^user/(?P<user>[\w-]+)/posts/count/(?P<count>[\w-]+)/$', views.tob_users_posts, name='tob_users_posts'),
	url(r'^user/(?P<user>[\w-]+)/post/(?P<post>[\w-]+)/count/(?P<count>[\w-]+)/$', views.tob_users_post, name='tob_users_post'),
	url(r'^user/(?P<user>[\w-]+)/post/(?P<post>[\w-]+)/comment/(?P<comment>[\w-]+)/$', views.tob_users_posts_comment, name='tob_users_posts_comment'),
	url(r'^user/(?P<user>[\w-]+)/examples/count/(?P<count>[\w-]+)/$', views.tob_users_examples, name='tob_users_examples'),
	url(r'^user/(?P<user>[\w-]+)/dictionaries/count/(?P<count>[\w-]+)/$', views.tob_users_dics, name='tob_users_dics'),
	url(r'^user/(?P<user>[\w-]+)/dictionary/(?P<dictionary>[\w-]+)/count/(?P<count>[\w-]+)/$', views.tob_users_dic, name='tob_users_dic'),
	url(r'^user/(?P<user>[\w-]+)/dictionary/(?P<dictionary>[\w-]+)/word/(?P<word>[\w-]+)/count/(?P<count>[\w-]+)/$', views.tob_users_dic_word_count, name='tob_users_dic_word_count'),
	url(r'^user/(?P<user>[\w-]+)/dictionary/(?P<dictionary>[\w-]+)/word/(?P<word>[\w-]+)/pronunciation/(?P<pronunciation_id>[\w-]+)/$', views.tob_users_dic_word_pronunciations, name='tob_users_dic_word_pronunciations'),
	url(r'^user/(?P<user>[\w-]+)/dictionary/(?P<dictionary>[\w-]+)/word/(?P<word>[\w-]+)/attribute/(?P<attribute>[\w-]+)/$', views.tob_users_dic_word_attribute, name='tob_users_dic_word_attribute'),
	url(r'^user/(?P<user>[\w-]+)/dictionary/(?P<dictionary>[\w-]+)/word/(?P<word>[\w-]+)/similarity/(?P<similarity>[\w-]+)/$', views.tob_users_dic_word_similarity, name='tob_users_dic_word_similarity'),
	url(r'^user/(?P<user>[\w-]+)/dictionary/(?P<dictionary>[\w-]+)/word/(?P<word>[\w-]+)/translation/(?P<translation>[\w-]+)/$', views.tob_users_dic_word_translation, name='tob_users_dic_word_translation'),
	url(r'^user/(?P<user>[\w-]+)/dictionary/(?P<dictionary>[\w-]+)/word/(?P<word>[\w-]+)/example/(?P<example>[\w-]+)/$', views.tob_users_dic_word_example, name='tob_users_dic_word_example'),
	url(r'^user/(?P<user>[\w-]+)/dictionary/(?P<dictionary>[\w-]+)/word/(?P<word>[\w-]+)/story/(?P<story>[\w-]+)/$', views.tob_users_dic_word_story, name='tob_users_dic_word_story'),
	url(r'^user/(?P<user>[\w-]+)/dictionary/(?P<dictionary>[\w-]+)/word/(?P<word>[\w-]+)/relation/(?P<relation>[\w-]+)/$', views.tob_users_dic_word_relation, name='tob_users_dic_word_relation'),
	url(r'^user/(?P<user>[\w-]+)/dictionary/(?P<dictionary>[\w-]+)/word/(?P<word>[\w-]+)/sponsor/(?P<sponsor>[\w-]+)/$', views.tob_users_dic_word_sponsor, name='tob_users_dic_word_sponsor'),
	url(r'^user/(?P<user>[\w-]+)/dictionary/(?P<dictionary>[\w-]+)/word/(?P<word>[\w-]+)/space/(?P<space>[\w-]+)/$', views.tob_users_dic_word_space, name='tob_users_dic_word_space'),
	url(r'^user/(?P<user>[\w-]+)/dictionary/(?P<dictionary>[\w-]+)/words/count/(?P<count>[\w-]+)/$', views.tob_users_dic_words, name='tob_users_dic_words'),
	url(r'^user/(?P<user>[\w-]+)/dictionary/(?P<dictionary>[\w-]+)/wordgroups/count/(?P<count>[\w-]+)/$', views.tob_users_dic_wordgroups, name='tob_users_dic_wordgroups'),
	url(r'^user/(?P<user>[\w-]+)/dictionary/(?P<dictionary>[\w-]+)/translations/count/(?P<count>[\w-]+)/$', views.tob_users_dic_translations, name='tob_users_dic_translations'),
	url(r'^user/(?P<user>[\w-]+)/dictionary/(?P<dictionary>[\w-]+)/sentences/count/(?P<count>[\w-]+)/$', views.tob_users_dic_sentences, name='tob_users_dic_sentences'),
	url(r'^user/(?P<user>[\w-]+)/dictionary/(?P<dictionary>[\w-]+)/sentences/(?P<sentence>[\w-]+)/renditions/count/(?P<count>[\w-]+)/$', views.tob_users_dic_renditions, name='tob_users_dic_renditions'),
	url(r'^user/(?P<user>[\w-]+)/dictionary/(?P<dictionary>[\w-]+)/analyses/count/(?P<count>[\w-]+)/$', views.tob_users_dic_analyses, name='tob_users_dic_analyses'),
	url(r'^user/(?P<user>[\w-]+)/dictionary/(?P<dictionary>[\w-]+)/votes/count/(?P<count>[\w-]+)/$', views.tob_users_dic_votes, name='tob_users_dic_votes'),
	url(r'^tob_word/word/(?P<word_id>[\w-]+)/$', views.tob_word, name='tob_word'),
	url(r'^tob_pronunciations/word/(?P<word_id>[\w-]+)/$', views.tob_pronunciations, name='tob_pronunciations'),
	url(r'^tob_pronunciation/pron/(?P<pron_id>[\w-]+)/$', views.tob_pronunciation, name='tob_pronunciation'),
	url(r'^dictionary/$', views.tob_dics, name='tob_dics'),
	url(r'^dictionary/(?P<dictionary_id>[\w-]+)/$', views.tob_dic, name='tob_dic'),
	url(r'^universal_pronunciation/$', views.universal_pronunciations, name='universal_pronunciations'),
	url(r'^universal_pronunciation/(?P<pronunciation>[\w-]+)/$', views.universal_pronunciation, name='universal_pronunciation'),
	url(r'^word_attributes/$', views.word_attributess, name='word_attributess'),
	url(r'^word_attributes/(?P<word>[\w-]+)/$', views.word_attributes, name='word_attributes'),
	url(r'^attribute/(?P<attribute_id>[\w-]+)/$', views.attribute, name='attribute'),
	url(r'^attributes/(?P<word_id>[\w-]+)/$', views.attributes, name='attributes'),
	url(r'^mutawords/$', views.mutawords, name='mutawords'),
	url(r'^mutaword/(?P<word>[\w-]+)/$', views.mutaword, name='mutaword'),
	#url(r'^complementary_scholar/$', views.complementary_scholar, name='complementary_scholar'),
	url(r'^logout_user/$', views.logout_user, name='logout_user'),
	url(r'^create_post/$', views.create_post, name='create_post'),
	url(r'^edit_post/(?P<post_id>[\w-]+)/$', views.edit_post, name='edit_post'),
	url(r'^create_space/$', views.create_space, name='create_space'),
	url(r'^create_dic/$', views.create_dic, name='create_dic'),
	url(r'^create_task/$', views.create_task, name='create_task'),
	url(r'^create_word/$', views.create_word, name='create_word'),
	url(r'^create_wordgroup/$', views.create_wordgroup, name='create_wordgroup'),
	url(r'^create_translation/$', views.create_translation, name='create_translation'),
	url(r'^create_sentence/$', views.create_sentence, name='create_sentence'),
	url(r'^create_rendition/$', views.create_rendition, name='create_rendition'),
	url(r'^create_analysis/$', views.create_analysis, name='create_analysis'),
	url(r'^create_story/$', views.create_story, name='create_story'),
	url(r'^create_pronunciations/$', views.create_pronunciations, name='create_pronunciations'),
	url(r'^update_own_dic/(?P<dicid>[\w-]+)/$', views.update_own_dic, name='update_own_dic'),
	url(r'^prereq_own_dic/(?P<dicid>[\w-]+)/$', views.prereq_own_dic, name='prereq_own_dic'),
	url(r'^want_to_purchase_dic/(?P<dicid>[\w-]+)/(?P<invitecode>[\w-]+)/$', views.want_to_purchase_dic, name='want_to_purchase_dic'),
	url(r'^buy_dic/(?P<dicid>[\w-]+)/$', views.buy_dic, name='buy_dic'),
	url(r'^submit_buy_dic_form/(?P<dicid>[\w-]+)/$', views.submit_buy_dic_form, name='submit_buy_dic_form'),
	url(r'^submit_font/(?P<word_id>[\w-]+)/$', views.submit_font, name='submit_font'),
	url(r'^buy_bread/(?P<amount>[\w-]+)/$', views.buy_bread, name='buy_bread'),
	url(r'^failed_bread/(?P<amount>[\w-]+)/$', views.failed_to_purchase_bread, name='failed_to_purchase_bread'),
	url(r'^buy_donate/(?P<amount>[\w-]+)/$', views.buy_donate, name='buy_donate'),
	url(r'^tob_user_baking/(?P<invoice>[\w-]+)/$', views.tob_user_baking, name='tob_user_baking'),
	url(r'^apply_votes/$', views.apply_votes, name='apply_votes'),
	url(r'^apply_votes_to_votestyle/(?P<voteid>[\w-]+)/$', views.apply_votes_to_votestyle, name='apply_votes_to_votestyle'),
	url(r'^apply_votestyle/$', views.apply_votestyle, name='apply_votestyle'),
	url(r'^exclude_votes/$', views.exclude_votes, name='exclude_votes'),
	url(r'^apply_dic/$', views.apply_dic, name='apply_dic'),
	url(r'^exclude_dic/$', views.exclude_dic, name='exclude_dic'),
	url(r'^create_comment/(?P<source_type>[\w-]+)/(?P<source>[\w-]+)/(?P<com>[\w-]+)/$', views.create_comment, name='create_comment'),
	url(r'^create_comment_thread/(?P<source_type>[\w-]+)/(?P<source>[\w-]+)/(?P<com>[\w-]+)/$', views.create_comment_thread, name='create_comment_thread'),
	url(r'^buy_users_dic/(?P<user>[\w-]+)/(?P<dictionary>[\w-]+)/$', views.buy_users_dic, name='buy_users_dic'),
	url(r'^delete_own_word/(?P<user>[\w-]+)/(?P<dictionary>[\w-]+)/(?P<word>[\w-]+)/$', views.delete_own_word, name='delete_own_word'),
	url(r'^delete_own_word_id/(?P<word_id>[\w-]+)/$', views.delete_own_word_id, name='delete_own_word_id'),
	url(r'^delete_own_dic/(?P<user>[\w-]+)/(?P<dictionary>[\w-]+)/$', views.delete_own_dic, name='delete_own_dic'),
	url(r'^delete_bought_dic/(?P<user>[\w-]+)/(?P<dictionary>[\w-]+)/$', views.delete_bought_dic, name='delete_bought_dic'),
	url(r'^delete_own_com/(?P<com>[\w-]+)/(?P<which>[\w-]+)/$', views.delete_own_com, name='delete_own_com'),
	url(r'^delete_own_attr/(?P<user>[\w-]+)/(?P<dic>[\w-]+)/(?P<word>[\w-]+)/(?P<attr>[\w-]+)/$', views.delete_own_attr, name='delete_own_attr'),
	url(r'^delete_own_attr_def/(?P<user>[\w-]+)/(?P<dic>[\w-]+)/(?P<word>[\w-]+)/(?P<attr>[\w-]+)/(?P<def>[\w-]+)/$', views.delete_own_attr_def, name='delete_own_attr_def'),
	url(r'^delete_own_attr_syn/(?P<user>[\w-]+)/(?P<dic>[\w-]+)/(?P<word>[\w-]+)/(?P<attr>[\w-]+)/(?P<syn>[\w-]+)/$', views.delete_own_attr_syn, name='delete_own_attr_syn'),
	url(r'^delete_own_attr_ant/(?P<user>[\w-]+)/(?P<dic>[\w-]+)/(?P<word>[\w-]+)/(?P<attr>[\w-]+)/(?P<ant>[\w-]+)/$', views.delete_own_attr_ant, name='delete_own_attr_ant'),
	url(r'^delete_own_attr_hom/(?P<user>[\w-]+)/(?P<dic>[\w-]+)/(?P<word>[\w-]+)/(?P<attr>[\w-]+)/(?P<hom>[\w-]+)/$', views.delete_own_attr_hom, name='delete_own_attr_hom'),
	url(r'^delete_own_pron/(?P<user>[\w-]+)/(?P<dic>[\w-]+)/(?P<word>[\w-]+)/(?P<pron>[\w-]+)/$', views.delete_own_pron, name='delete_own_pron'),
	url(r'^delete_own_exam/(?P<user>[\w-]+)/(?P<dic>[\w-]+)/(?P<word>[\w-]+)/(?P<exam>[\w-]+)/$', views.delete_own_exam, name='delete_own_exam'),
	url(r'^delete_own_trans/(?P<user>[\w-]+)/(?P<dic>[\w-]+)/(?P<word>[\w-]+)/(?P<trans>[\w-]+)/$', views.delete_own_trans, name='delete_own_trans'),
	url(r'^delete_own_stor/(?P<user>[\w-]+)/(?P<dic>[\w-]+)/(?P<word>[\w-]+)/(?P<stor>[\w-]+)/$', views.delete_own_stor, name='delete_own_stor'),
	url(r'^delete_own_rela/(?P<user>[\w-]+)/(?P<dic>[\w-]+)/(?P<word>[\w-]+)/(?P<rela>[\w-]+)/$', views.delete_own_rela, name='delete_own_rela'),
	url(r'^delete_own_conn/(?P<user>[\w-]+)/(?P<dic>[\w-]+)/(?P<word>[\w-]+)/(?P<rela>[\w-]+)/(?P<conn>[\w-]+)/$', views.delete_own_conn, name='delete_own_conn'),
	url(r'^delete_own_spon/(?P<user>[\w-]+)/(?P<dic>[\w-]+)/(?P<word>[\w-]+)/(?P<spon>[\w-]+)/$', views.delete_own_spon, name='delete_own_spon'),
	url(r'^delete_own_spons/(?P<spon>[\w-]+)/$', views.delete_own_spons, name='delete_own_spons'),
	url(r'^delete_own_spac/(?P<user>[\w-]+)/(?P<dic>[\w-]+)/(?P<word>[\w-]+)/(?P<spac>[\w-]+)/$', views.delete_own_spac, name='delete_own_spac'),
	url(r'^delete_own_post/(?P<user>[\w-]+)/(?P<post>[\w-]+)/$', views.delete_own_post, name='delete_own_post'),
	url(r'^delete_own_space/(?P<user>[\w-]+)/(?P<space>[\w-]+)/$', views.delete_own_space, name='delete_own_space'),
	url(r'^delete_own_votestyle/(?P<voteid>[\w-]+)/$', views.delete_own_votestyle, name='delete_own_votestyle'),
	url(r'^vote/(?P<vote>[\w-]+)/$', views.vote, name='vote'),
	url(r'^votewvotestyle/(?P<source_type>[\w-]+)/(?P<source_id>[\w-]+)/$', views.votewvotestyle, name='votewvotestyle'),
	url(r'^clickthrough/$', views.clickthrough, name='clickthrough'),
	url(r'^viewsponsor/(?P<sponsor_id>[\w-]+)/$', views.viewsponsor, name='viewsponsor'),
	url(r'^tob_buy_space/(?P<user>[\w-]+)/(?P<space>[\w-]+)/$', views.tob_buy_space, name='tob_buy_space'),
	url(r'^submit_buy_space_form/(?P<space_id>[\w-]+)/$', views.submit_buy_space_form, name='submit_buy_space_form'),
	url(r'^tob_remove_space/(?P<user>[\w-]+)/(?P<space>[\w-]+)/$', views.tob_remove_space, name='tob_remove_space'),
	url(r'^tob_save_space/(?P<user>[\w-]+)/(?P<space>[\w-]+)/$', views.tob_save_space, name='tob_save_space'),
	url(r'^tob_unsave_space/(?P<user>[\w-]+)/(?P<space>[\w-]+)/$', views.tob_unsave_space, name='tob_unsave_space'),
	url(r'^tob_save_exa/(?P<user>[\w-]+)/(?P<exa>[\w-]+)/$', views.save_own_exa, name='save_own_exa'),
	url(r'^tob_save_com/(?P<user>[\w-]+)/(?P<com>[\w-]+)/$', views.tob_save_com, name='tob_save_com'),
	url(r'^tob_save_votestyle/(?P<user>[\w-]+)/(?P<votestyleid>[\w-]+)/$', views.tob_save_votestyle, name='tob_save_votestyle'),
	url(r'^users_space_edit/(?P<space>[\w-]+)/$', views.users_space_edit, name='users_space_edit'),
	url(r'^tob_vote/(?P<vote_id>[\w-]+)/$', views.tob_vote, name='tob_vote'),
	url(r'^tob_post/(?P<post>[\w-]+)/$', views.tob_post, name='tob_post'),
	url(r'^tob_product/(?P<product_id>[\w-]+)/$', views.tob_product, name='tob_product'),
	url(r'^tob_word_sponsor/word_id/(?P<word_id>[\w-]+)/sponsor_id/(?P<sponsor_id>[\w-]+)/$', views.tob_word_sponsor, name='tob_word_sponsor'),
	url(r'^tob_word_translation/word_id/(?P<word_id>[\w-]+)/translation_id/(?P<translation_id>[\w-]+)/$', views.tob_word_translation, name='tob_word_translation'),
	url(r'^tob_word_attribute/word_id/(?P<word_id>[\w-]+)/attribute_id/(?P<attribute_id>[\w-]+)/$', views.tob_word_attribute, name='tob_word_attribute'),
	url(r'^tob_word_pronunciation/word_id/(?P<word_id>[\w-]+)/pronunciation_id/(?P<pronunciation_id>[\w-]+)/$', views.tob_word_pronunciation, name='tob_word_pronunciation'),
	url(r'^tob_pronunciation/(?P<pronunciation_id>[\w-]+)/$', views.tob_pronunciation, name='tob_pronunciation'),
	url(r'^tob_word_example/word_id/(?P<word_id>[\w-]+)/example_id/(?P<example_id>[\w-]+)/$', views.tob_word_example, name='tob_word_example'),
	url(r'^tob_word_story/word_id/(?P<word_id>[\w-]+)/story_id/(?P<story_id>[\w-]+)/$', views.tob_word_story, name='tob_word_story'),
	url(r'^tob_word_relation/word_id/(?P<word_id>[\w-]+)/relation_id/(?P<relation_id>[\w-]+)/$', views.tob_word_relation, name='tob_word_relation'),
	url(r'^tob_wallet/(?P<vote_id>[\w-]+)/$', views.tob_wallet, name='tob_wallet'),
	url(r'^submit_wallet/(?P<amount>[\w-]+)/$', views.submit_wallet, name='submit_wallet'),
	url(r'^tob_email/(?P<token_id>[\w-]+)/(?P<count>[\w-]+)/$', views.tob_email, name='tob_email'),
	url(r'^submit_email/$', views.submit_email, name='submit_email'),
	url(r'^roadmap/$', views.roadmap, name='roadmap'),
	url(r'^upload_file/$', views.upload_file, name='upload_file'),
	url(r'^tob_users_files/(?P<user>[\w-]+)/$', views.tob_users_files, name='tob_users_files'),
    path('api/checkout-session/<price>/', views.create_checkout_session, name='api_checkout_session'),
	path('api/checkout_ads/', views.checkout_ads, name='checkout_ads'),
]