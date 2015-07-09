# coding=utf-8
import os
import collections

# General settings
import datetime

base = os.path.dirname(os.path.abspath(__file__))

_path = lambda d: os.path.join(base, d)
Dir = collections.namedtuple('Dir', ['full_path', 'relative_path'])

# DIR variables
ARTICLE_DIR = Dir(_path('articles'), 'articles')
OUTPUT_DIR = Dir(_path('output'), 'output')
STATIC_DIR = Dir(_path('static'), 'static')

# Use `TEMPLATE` to import settings details into the templates
TEMPLATE = {
    'static_url': '/' + STATIC_DIR.relative_path + '/',
    'article_dir': '/' + ARTICLE_DIR.relative_path + '/',
    'year': datetime.datetime.utcnow().year,
}

# This is list of the obligatory meta fields of articles
META_TAGS = [
    'Date',
    'Title',
    'Url',
]

BLOG_TITLE = u'Блог'
HOST = 'http://localhost:8000'

# if you don't want feed - pass None or {} to FEED
FEED = {
    'articles_count': 10,
    'author': u'Марий Йонов',
    'link': '',  # this should be the link to the blog
    'language': 'bg',
}