import os.path

from django import template

from simpleoncall import settings

register = template.Library()


class EvilIconsNode(template.Node):
    def render(self, context):
        evil_icons = os.path.join(settings.STATIC_ROOT, 'icons/evil-icons.svg')
        with open(evil_icons) as fp:
            return fp.read()


class EvilIconNode(template.Node):
    def __init__(self, name):
        self.name = name

    def render(self, context=None):
        return (
            '<svg viewBox="0 0 100 100" class="icon %(name)s-icon">'
            '<use xlink:href="#%(name)s-icon"></use>'
            '</svg>'
        ) % {'name': self.name}


@register.tag('evil_icons')
def evil_icons(parser, token):
    return EvilIconsNode()


@register.tag('evil_icon')
def evil_icon(parser, token):
    try:
        _, name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError()
    return EvilIconNode(name)
