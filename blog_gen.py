# coding=utf-8
from __future__ import print_function
from os.path import join as pjoin
import codecs
import sys
import os
import shutil
import time

from jinja2 import Environment, PackageLoader
import markdown

import settings


HELP_INFO = '''
    Usage:
    blog_gen compile - it takes all articles from `ARTICLE_DIR` dir,
    uses `STATIC_DIR` for js, css and images and creates the static
    website in `OUTPUT_DIR` folder
'''


class PageException(Exception):
    pass


class ArticleException(Exception):
    pass


class Page(object):
    ENVIRONMENT = Environment(loader=PackageLoader('blog_gen'))
    TEMPLATE = None

    def __init__(self, template_settings, **kwargs):
        self.env = kwargs
        self.env['template_settings'] = template_settings

    def render(self, **kwargs):
        if 'page' in kwargs:
            page = kwargs['page']
        else:
            page = self.__class__.TEMPLATE

        print('Render page {0}'.format(page))
        return self.template.render(self.env)

    def save(self, fname):
        with codecs.open(fname, 'w', 'utf-8') as f:
            f.write(self.render())

    @property
    def template(self):
        if self.__class__.TEMPLATE is None:
            raise PageException('Class should have `TEMPLATE` instance')
        return self.__class__.ENVIRONMENT.get_template(self.__class__.TEMPLATE)


class Article(Page):
    TEMPLATE = 'article.jinja2'

    def __init__(self, template_settings, relative_article_path, **kwargs):
        super(Article, self).__init__(template_settings, **kwargs)
        article_path = pjoin(
            settings.ARTICLE_DIR.full_path,
            relative_article_path
        )
        self.path = article_path
        try:
            meta, content = Article._parse_article(article_path)
            self.meta = meta
            self.content = content
        except Exception as e:
            self._error = unicode(e)

    @property
    def error(self):
        return getattr(self, '_error', None)

    @classmethod
    def _parse_article(cls, article_path):
        meta_status = 'not_started'
        meta = {}
        content = ''

        with codecs.open(article_path, 'r', 'utf-8') as farticle:
            for line in farticle:
                if line.strip() == 'META':
                    meta_status = 'started'
                    continue
                if line.strip() == '' and meta_status == 'started':
                    meta_status = 'ended'
                    continue
                if meta_status == 'started':
                    tokens = [token.strip() for token in line.split(':', 1)]
                    meta[tokens[0]] = tokens[1]
                if meta_status == 'ended':
                    content += line

        if 'Date' not in meta:
            raise ArticleException('Article {0} has not `Date` meta tag'.format(article_path))

        try:
            meta['_time'] = time.strptime(meta['Date'], '%H:%M %d.%m.%Y')
            meta['Date'] = meta['Date'].split()[1]
        except:
            raise ArticleException('Article {0} has invalid `Date` meta tag'.format(article_path))

        content = markdown.markdown(
            content,
            extensions=['markdown.extensions.fenced_code'],
        )

        return meta, content

    def render(self):
        self.env.update({'meta': self.meta, 'content': self.content, 'title': self.meta['Title']})
        return super(Article, self).render(page=self.path)


class Index(Page):
    TEMPLATE = 'index.jinja2'


class About(Page):
    TEMPLATE = 'about.jinja2'


def collect_articles():
    articles = []
    errors = 0
    for f in os.listdir(settings.ARTICLE_DIR.full_path):
        file_path = pjoin(settings.ARTICLE_DIR.full_path, f)
        if os.path.isfile(file_path) and f.endswith('.md'):
            article = Article(settings.TEMPLATE, f)
            if article.error is None:
                articles.append(article)
            else:
                print('[E] Skipping article\n', article.error)
                errors += 1

    articles = sorted(articles, key=lambda a: a.meta['_time'], reverse=True)

    return articles, errors


def dir_exist(path):
    return os.path.exists(path) and os.path.isdir(path)


def dir_empty(path):
    return len(os.listdir(path)) == 0


def clean_dir(path):
    for f in os.listdir(path):
        fpath = pjoin(path, f)
        if os.path.isfile(fpath) or os.path.islink(fpath):
            os.remove(fpath)
        else:
            shutil.rmtree(fpath)


def create_or_clean_dir(path):
    if not dir_exist(path):
        os.mkdir(path)
    else:
        clean_dir(path)

    if (not dir_exist(path) or
            not dir_empty(path)):
        print('Problems with creating/cleaning of the {0}. Remove the directory manually and try again.'.format(
            path
        ))
        sys.exit(1)


def copy_static_folder():
    shutil.copytree(settings.STATIC_DIR.full_path,
                    pjoin(settings.OUTPUT_DIR.full_path,
                          settings.STATIC_DIR.relative_path))


def compile_blog():
    create_or_clean_dir(settings.OUTPUT_DIR.full_path)
    copy_static_folder()
    create_or_clean_dir(pjoin(settings.OUTPUT_DIR.full_path, settings.ARTICLE_DIR.relative_path))
    articles, errors = collect_articles()

    output_path = lambda *name: pjoin(settings.OUTPUT_DIR.full_path, *name)

    About(settings.TEMPLATE, title=u'За мен', active='about').save(output_path('about.html'))
    Index(settings.TEMPLATE, title=u'Съдържание', active='index', articles=articles).save(output_path('index.html'))
    for a in articles:
        a.save(output_path('articles', a.meta['Url'] + '.html'))

    if errors != 0:
        if errors == 1:
            print('There was 1 error.')
        else:
            print('There were {0} errors'.format(errors))


def main():
    if len(sys.argv) != 2:
        print(HELP_INFO)
        return
    if sys.argv[1] == 'compile':
        compile_blog()


if __name__ == '__main__':
    main()