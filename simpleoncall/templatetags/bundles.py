import os.path

from django import template

from simpleoncall import settings

register = template.Library()


class StylesheetNode(template.Node):
    def __init__(self, name):
        self.name = name

    def render_style(self, name):
        path = os.path.join(settings.STATIC_URL, name)
        return '<link rel="stylesheet" type="text/css" href="%s" />' % (path, )

    def render(self, context):
        output = ''
        if self.name in settings.STYLESHEETS:
            if not settings.USE_BUNDLES:
                for css_file in settings.STYLESHEETS[self.name]:
                    output += self.render_style(css_file)
            else:
                output = self.render_style(self.name)
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


class ScriptNode(template.Node):
    def __init__(self, name):
        self.name = name

    def render_script(self, name):
        path = os.path.join(settings.STATIC_URL, name)
        return '<script stype="text/javascript" src="%s"></script>' % (path, )

    def render(self, context):
        output = ''
        if self.name in settings.SCRIPTS:
            if not settings.USE_BUNDLES:
                for script_file in settings.SCRIPTS[self.name]:
                    output += self.render_script(script_file)
            else:
                output = self.render_script(self.name)
        return output


@register.tag('script')
def script(parser, token):
    try:
        _, name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            '%r requires exactly one argument: the bundled script path' % token.split_contents()[0]
        )

    return ScriptNode(name)
