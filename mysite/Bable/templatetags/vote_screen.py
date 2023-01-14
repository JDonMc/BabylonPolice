from django import template

register = template.Library()

@register.simple_tag
def screen_votes(object, the_user):
	object.screen_votes(the_user)
	# must be called before object.returning_vote_styles.votes or the_vote_name

# register.filter('usernames', usernames) # can be used instead of decorator
# enter {% load user_referencing %}
# to incorporate into HTML