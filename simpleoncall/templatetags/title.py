from django import template

register = template.Library()


@register.filter('title')
def title(name=None):
    if not name:
        name = 'SimpleOnCall'
    elif not name.startswith('SimpleOnCall'):
        name = 'SimpleOnCall - %s' % (name, )
    return '<title>%s</title>' % (name, )
