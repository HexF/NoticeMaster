import json

from django import template
from django.db.models import QuerySet
from django.urls import reverse

from notices.models import Subscriber, Notice

register = template.Library()


@register.filter('only_subscribed')
def only_subscribed(value: QuerySet[Notice], subscriber: Subscriber) -> QuerySet[Notice]:
    return value.exclude(
        tags__in=subscriber.unsubscribed_tags.all()
    )

@register.filter('only_unsubscribed')
def only_unsubscribed(value: QuerySet[Notice], subscriber: Subscriber) -> QuerySet[Notice]:
    return value.filter(
        tags__in=subscriber.unsubscribed_tags.all()
    )

@register.filter("json")
def make_json(value):
    return json.dumps(value)


@register.simple_tag(takes_context=True)
def abs_url(context, view_name, *args, **kwargs):
    # Could add except for KeyError, if rendering the template
    # without a request available.
    return context['request'].build_absolute_uri(
        reverse(view_name, args=args, kwargs=kwargs)
    )