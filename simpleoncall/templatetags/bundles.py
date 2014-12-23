import os.path

from django import template

from simpleoncall import settings

register = template.Library()


class StylesheetNode(template.Node):
    def __init__(self, name):
        self.name = name

    def render(self, context):
        output = ''
        if self.name in settings.STYLESHEETS:
            if not settings.USE_BUNDLES:
                for css_file in settings.STYLESHEETS[self.name]:
                    path = os.path.join(settings.STATIC_URL, css_file)
                    output += '<link rel="stylesheet" type="text/css" href="%s" />' % (path, )
            else:
                path = os.path.join(settings.STATIC_URL, self.name)
                output = '<link rel="stylesheet" type="text/css" href="%s" />' % (path, )
        return output


@register.tag('stylesheet')
def stylesheet(parser, token):
    try:
        _, name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            '%r requires exactly one argument: the bundled stylesheet path' % token.split_contents()[0]
        )

    return StylesheetNode(name)
