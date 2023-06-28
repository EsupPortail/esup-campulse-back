from django import template

register = template.Library()

# Used to resolve django template vars from db content


@register.tag(name="resolve")
def do_resolve(parser, token):
    nodelist = parser.parse(('endresolve',))

    parser.delete_first_token()

    return ResolveNode(nodelist)


class ResolveNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        output = self.nodelist.render(context)
        output = template.Template(output).render(context)
        return output
