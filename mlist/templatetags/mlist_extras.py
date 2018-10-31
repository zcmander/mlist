from django.utils.safestring import mark_safe
from django.template import Library, Node, TemplateSyntaxError

from mlist.models import Collection

register = Library()


class RangeNode(Node):
    def __init__(self, range_args, context_name):
        self.range_args = range_args
        self.context_name = context_name

    def render(self, context):
        context[self.context_name] = range(*self.range_args)
        return ""

@register.tag
def mkrange(parser, token):
    """
    Accepts the same arguments as the 'range' builtin and creates
    a list containing the result of 'range'.

    Syntax:
        {% mkrange [start,] stop[, step] as context_name %}

    For example:
        {% mkrange 5 10 2 as some_range %}
        {% for i in some_range %}
          {{ i }}: Something I want to repeat\n
        {% endfor %}

    Produces:
        5: Something I want to repeat
        7: Something I want to repeat
        9: Something I want to repeat
    """

    tokens = token.split_contents()
    fnctl = tokens.pop(0)

    def error():
        raise TemplateSyntaxError(
            "%s accepts the syntax: {%% %s [start,] " + \
            "stop[, step] as context_name %%}, where 'start', 'stop' " + \
            "and 'step' must all be integers." % (fnctl))

    range_args = []
    while True:
        if len(tokens) < 2:
            error()

        token = tokens.pop(0)

        if token == "as":
            break

        if not token.isdigit():
            error()
        range_args.append(int(token))

    if len(tokens) != 1:
        error()

    context_name = tokens.pop()

    return RangeNode(range_args, context_name)


@register.inclusion_tag('mlist/tags/collection_list.html')
def collection_list(user):
    collections = Collection.objects.filter(user=user)
    return {'collections': collections}


class Tag:
    scope = None
    value = None

    def __init__(self, scope, value):
        self.scope = scope
        self.value = value


@register.inclusion_tag("mlist/tags/tag_list.html")
def tag_list(tags):
    processed_tags = []
    for tag in tags:
        splitted = str(tag).split(":")
        if len(splitted) > 1:
            processed_tags.append(Tag(splitted[0], ':'.join(splitted[1:]) ))
        else:
            processed_tags.append(Tag('bookmark', splitted[0]))

    return {'tags': processed_tags}


@register.inclusion_tag("mlist/tags/genre_list.html")
def genre_list(imdb_genres, tmdb_genres):
    if not imdb_genres:
        imdb_genres = ""
    if not tmdb_genres:
        tmdb_genres = ""

    raw_imdb_genres = set([x.strip() for x in imdb_genres.split(',') if x])
    raw_tmdb_genres = set([x.strip() for x in tmdb_genres.split(',') if x])

    if 'Science Fiction' in raw_tmdb_genres:
        raw_tmdb_genres = (raw_tmdb_genres - set(["Science Fiction"])) | set(["Sci-Fi"])

    set_common_genres = raw_imdb_genres & raw_tmdb_genres
    set_imdb_genres = raw_imdb_genres - set_common_genres
    set_tmdb_genres = raw_tmdb_genres - set_common_genres

    return {'common_genres': sorted(set_common_genres),
            'imdb_genres': sorted(set_imdb_genres),
            'tmdb_genres': sorted(set_tmdb_genres)}


@register.inclusion_tag("mlist/tags/br_list.html")
def br_list(text):
    if text:
        return {'values': [x.strip() for x in text.split(',')]}
    else:
        return {'values': []}


@register.simple_tag
def movie_stars(value):
    converted_value = (float(value))
    string_converted_value = u'<small class="pull-right">' + str(converted_value) + "</small>"
    star = u'<i class="icon-star"></i>'
    #star_empty = u'<i class="icon-star-empty"></i>'
    star_empty = ''
    return mark_safe(star * int(converted_value) + star_empty * (10 - int(converted_value)) + u" " + string_converted_value)


def get_query_string(p, new_params=None, remove=None):
    """
    Add and remove query parameters. From `django.contrib.admin`.
    """
    if new_params is None: new_params = {}
    if remove is None: remove = []
    for r in remove:
        for k in p.keys():
            if k.startswith(r):
                del p[k]
    for k, v in new_params.items():
        if k in p and v is None:
            del p[k]
        elif v is not None:
            p[k] = v
    return mark_safe('?' + '&amp;'.join([u'%s=%s' % (k, v) for k, v in p.items()]).replace(' ', '%20'))


def string_to_dict(string):
    """
    Usage::

        {{ url|thumbnail:"width=10,height=20" }}
        {{ url|thumbnail:"width=10" }}
        {{ url|thumbnail:"height=20" }}
    """
    kwargs = {}
    if string:
        string = str(string)
        if ',' not in string:
            # ensure at least one ','
            string += ','
        for arg in string.split(','):
            arg = arg.strip()
            if arg == '': continue
            kw, val = arg.split('=', 1)
            kwargs[kw] = val
    return kwargs

def string_to_list(string):
    """
    Usage::

        {{ url|thumbnail:"width,height" }}
    """
    args = []
    if string:
        string = str(string)
        if ',' not in string:
            # ensure at least one ','
            string += ','
        for arg in string.split(','):
            arg = arg.strip()
            if arg == '': continue
            args.append(arg)
    return args

@register.inclusion_tag('_response.html', takes_context=True)
def query_string(context, add=None, remove=None):
    """
    Allows the addition and removal of query string parameters.

    _response.html is just {{ response }}

    Usage:
    http://www.url.com/{% query_string "param_to_add=value, param_to_add=value" "param_to_remove, params_to_remove" %}
    http://www.url.com/{% query_string "" "filter" %}filter={{new_filter}}
    http://www.url.com/{% query_string "sort=value" "sort" %}
    """
    # Written as an inclusion tag to simplify getting the context.
    add = string_to_dict(add)
    remove = string_to_list(remove)
    params = dict( context['request'].GET.items())
    response = get_query_string(params, add, remove)
    return {'response': response }
