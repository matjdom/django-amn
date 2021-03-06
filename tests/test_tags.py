
from django.test import TestCase

from django.test.utils import setup_test_template_loader, override_settings
from django.template import Context, TemplateSyntaxError
from django.template.loader import get_template

TEMPLATES = {
    'basetag': '''{% load damn %}{% assets %}''',
    'test_one': '''
{% load damn %}{% assets %}
{% asset 'js/jquery.js' %}
''',
    'test_two': '''
{% load damn %}{% assets %}
{% asset 'js/jquery.js' %}
{% asset 'js/knockout.js' %}
''',
    'test_three': '''
{% load damn %}{% assets %}
{% asset 'js/knockout.js' 'js/jquery.js' %}
{% asset 'js/jquery.js' %}
''',
    'test_mixed': '''
{% load damn %}{% assets %}
{% asset 'js/jquery.js' %}
{% asset 'css/bootstrap.css' %}
''',

    'test_alias': '''
{% load damn %}{% assets %}
{% asset 'js/knockout.js' 'jquery' %}
{% asset 'js/jquery.js' alias='jquery' %}
''',

    'test_ordering': '''
{% load damn %}{% assets %}
{% asset 'js/jquery.js' %}
{% asset 'css/bootstrap.css' %}
''',

    'config_deps': '''
{% load damn %}{% assets %}
{% asset 'js/knockout.js' %}
''',

    'extend_deps': '''
{% load damn %}{% assets %}
{% asset 'js/bootstrap.js' 'knockout' %}
''',

    'self_alias': '''
{% load damn %}{% assets %}
{% asset 'jquery' alias='jquery' %}
''',

}

DEFAULT_SETTINGS = {
    'STATIC_URL': '/static/',

    'DAMN_PROCESSORS': {
        'js': {
            'processor': 'damn.processors.ScriptProcessor',
        },
        'css': {
            'processor': 'damn.processors.LinkProcessor',
            'type': 'text/css',
        },
    }

}

@override_settings(**DEFAULT_SETTINGS)
class TagTests(TestCase):

    @classmethod
    def setUpClass(self):
        setup_test_template_loader(TEMPLATES)

    def test_simple(self):
        t = get_template('basetag')
        t.render(Context())

    def test_one(self):
        t = get_template('test_one')
        o = t.render(Context())
        self.assertTrue('<script src="/static/js/jquery.js"></script>' in o)

    def test_two(self):
        t = get_template('test_two')
        o = t.render(Context())
        self.assertTrue('<script src="/static/js/jquery.js"></script>' in o)
        self.assertTrue('<script src="/static/js/knockout.js"></script>' in o)

    def test_three(self):
        t = get_template('test_three')
        o = t.render(Context())
        self.assertTrue('<script src="/static/js/jquery.js"></script>' in o)
        self.assertTrue('<script src="/static/js/knockout.js"></script>' in o)
        self.assertTrue(
            o.index('src="/static/js/jquery.js"') < o.index('src="/static/js/knockout.js"')
        )

    def test_mixed(self):
        t = get_template('test_mixed')
        o = t.render(Context())
        self.assertTrue('<script src="/static/js/jquery.js"></script>' in o)
        self.assertTrue('<link rel="stylesheet" type="text/css" href="/static/css/bootstrap.css">' in o)

    def test_alias(self):
        t = get_template('test_alias')
        o = t.render(Context())

        self.assertTrue('<script src="/static/js/jquery.js"></script>' in o)
        self.assertTrue('<script src="/static/js/knockout.js"></script>' in o)
        self.assertTrue(
            o.index('src="/static/js/jquery.js"') < o.index('src="/static/js/knockout.js"')
        )

    def test_ordering(self):
        t = get_template('test_ordering')
        o = t.render(Context())

        self.assertTrue(o.index('bootstrap.css') < o.index('jquery.js'))

    @override_settings(
        DAMN_PROCESSORS = {
            'js': {
                'processor': 'damn.processors.ScriptProcessor',
                'deps': {
                    'js/knockout.js': ['jquery'],
                    'js/jquery.js': [],
                },
                'aliases': {
                    'jquery': 'js/jquery.js',
                },
            },
        }
    )
    def test_config_deps(self):
        t = get_template('config_deps')
        o = t.render(Context())

        self.assertTrue('<script src="/static/js/jquery.js"></script>' in o)
        self.assertTrue('<script src="/static/js/knockout.js"></script>' in o)


    @override_settings(
        DAMN_PROCESSORS = {
            'js': {
                'processor': 'damn.processors.ScriptProcessor',
                'aliases': {
                    'knockout': 'js/knockout.js',
                    'jquery': 'js/jquery.js',
                },
                'deps': {
                    'js/knockout.js': ['jquery'],
                    'js/jquery.js': [],
                },
            },
        }
    )
    def test_extend_deps(self):
        t = get_template('extend_deps')
        o = t.render(Context())

    def test_self_alias(self):
        t = get_template('self_alias')
        with self.assertRaises(TemplateSyntaxError):
            t.render(Context())

