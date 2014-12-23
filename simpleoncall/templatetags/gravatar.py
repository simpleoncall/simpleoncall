import md5

from django import template

register = template.Library()


@register.filter('gravatar_url')
def gravatar_url(email):
    hash = md5.new(email).hexdigest()
    return '<img class="avatar" src="http://www.gravatar.com/avatar/%s" />' % (hash, )
