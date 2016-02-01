from django import template
from django.template.defaultfilters import stringfilter

from core.models import Vote

register = template.Library()

@register.filter
def user_vote_info(vote, user_id):
    """Return user's vote, if it exists"""
    if vote.user_vote(user_id):
        return vote.user_vote(user_id).value
    else:
        return 0
